"""
Antigravity CLI Headless Runner & Task Monitor for Poker Studio
==============================================================
Directly orchestrates Antigravity agent sessions via subprocess,
monitoring progress through conversation transcript and disk assets.
"""

import os
import sys
import json
import time
import shutil
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("antigravity_cli")
logger.setLevel(logging.INFO)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
GEMINI_DIR = Path(os.environ.get("USERPROFILE", "C:/Users/mrali")) / ".gemini"
BRAIN_DIR = GEMINI_DIR / "antigravity" / "brain"

# Locate Antigravity binaries
DEFAULT_LANGUAGE_SERVER = Path(
    os.environ.get("LOCALAPPDATA", "C:/Users/mrali/AppData/Local")
) / "Programs" / "antigravity" / "resources" / "bin" / "language_server.exe"

DEFAULT_AGENTAPI_BAT = GEMINI_DIR / "antigravity" / "bin" / "agentapi.bat"
DEFAULT_ANTIGRAVITY_BAT = GEMINI_DIR / "antigravity" / "bin" / "antigravity.bat"


def get_cli_command() -> List[str]:
    """Finds the best available Antigravity CLI executable."""
    if DEFAULT_LANGUAGE_SERVER.exists():
        return [str(DEFAULT_LANGUAGE_SERVER), "agentapi", "new-conversation"]
    
    agentapi_which = shutil.which("agentapi")
    if agentapi_which:
        return [agentapi_which, "new-conversation"]
        
    if DEFAULT_AGENTAPI_BAT.exists():
        return [str(DEFAULT_AGENTAPI_BAT), "new-conversation"]

    antigravity_which = shutil.which("antigravity")
    if antigravity_which:
        return [antigravity_which]
        
    if DEFAULT_ANTIGRAVITY_BAT.exists():
        return [str(DEFAULT_ANTIGRAVITY_BAT)]

    raise RuntimeError("Antigravity CLI executable not found on this machine.")


class EpisodeTask:
    """Tracks the state of an Antigravity background task for an episode."""
    def __init__(self, episode_id: str, task_type: str):
        self.episode_id = episode_id
        self.task_type = task_type  # "storyboard", "images", "regenerate_scene"
        self.status = "idle"  # "idle", "running", "completed", "error"
        self.current_step = "آماده‌سازی برای شروع کار..."
        self.progress = 0
        self.total_scenes = 0
        self.completed_scenes = 0
        self.conversation_id: Optional[str] = None
        self.started_at = time.time()
        self.updated_at = time.time()
        self.error_message: Optional[str] = None
        self.generated_images: List[str] = []
        self.logs: List[str] = []
        self.target_scene_id: Optional[str] = None

    def add_log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 60:
            self.logs = self.logs[-60:]
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "task_type": self.task_type,
            "status": self.status,
            "current_step": self.current_step,
            "progress": self.progress,
            "total_scenes": self.total_scenes,
            "completed_scenes": self.completed_scenes,
            "conversation_id": self.conversation_id,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "error_message": self.error_message,
            "generated_images": self.generated_images,
            "target_scene_id": self.target_scene_id,
            "logs": self.logs,
        }


# Global in-memory state tracking per episode
_active_tasks: Dict[str, EpisodeTask] = {}


def get_task_for_episode(episode_id: str) -> EpisodeTask:
    if episode_id not in _active_tasks:
        task = EpisodeTask(episode_id, "idle")
        _active_tasks[episode_id] = task
        # Check existing images on disk
        _refresh_image_status(task)
    return _active_tasks[episode_id]


def _refresh_image_status(task: EpisodeTask):
    """Scans projects/<episode_id>/assets/images for existing scene images."""
    proj_dir = PROJECTS_DIR / task.episode_id
    img_dir = proj_dir / "assets" / "images"
    state_file = proj_dir / "state.json"

    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                scenes = state_data.get("scenes", [])
                task.total_scenes = len(scenes)
        except Exception:
            pass

    found = []
    if img_dir.exists():
        for f in img_dir.glob("scene_*.png"):
            found.append(f.name)
        for f in img_dir.glob("scene_*.jpg"):
            found.append(f.name)
    found.sort()
    task.generated_images = found
    task.completed_scenes = len(found)
    if task.total_scenes > 0 and task.task_type == "images":
        task.progress = min(100, int((task.completed_scenes / task.total_scenes) * 100))


async def _run_antigravity_cli_process(prompt: str, title: str) -> Optional[str]:
    """
    Executes the Antigravity CLI in non-interactive/headless mode,
    returning the conversationId.
    """
    cmd = get_cli_command()
    # Format arguments depending on binary type
    if "agentapi" in cmd:
        full_cmd = cmd + [f"--title={title}", prompt]
    else:
        full_cmd = cmd + ["--title", title, prompt]

    logger.info("Executing Antigravity CLI: %s", " ".join(full_cmd[:4]))

    # Execute asynchronously in BASE_DIR
    proc = await asyncio.create_subprocess_exec(
        *full_cmd,
        cwd=str(BASE_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    out_text = stdout.decode("utf-8", errors="replace").strip()
    err_text = stderr.decode("utf-8", errors="replace").strip()

    if proc.returncode != 0:
        logger.error("Antigravity CLI failed with code %d: %s", proc.returncode, err_text)
        raise RuntimeError(f"Antigravity CLI returned code {proc.returncode}: {err_text or out_text}")

    # Parse conversationId
    try:
        data = json.loads(out_text)
        conv_id = (
            data.get("response", {})
            .get("newConversation", {})
            .get("conversationId")
        )
        if conv_id:
            return conv_id
    except json.JSONDecodeError:
        pass

    # Fallback pattern match
    import re
    match = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", out_text)
    if match:
        return match.group(1)

    logger.warning("Could not parse conversationId from output: %s", out_text)
    return None


async def _monitor_task(task: EpisodeTask):
    """
    Monitors a running conversation by tailing transcript.jsonl
    and checking project files on disk.
    """
    episode_id = task.episode_id
    conv_id = task.conversation_id
    transcript_file = BRAIN_DIR / conv_id / ".system_generated" / "logs" / "transcript.jsonl" if conv_id else None

    logger.info("Starting task monitor for episode %s (conv: %s)", episode_id, conv_id)
    last_step_index = -1
    consecutive_done_checks = 0
    max_wait_seconds = 1800  # 30 minutes max
    start_time = time.time()

    initial_img_count = len(task.generated_images)

    while time.time() - start_time < max_wait_seconds:
        await asyncio.sleep(2.0)
        _refresh_image_status(task)

        # Check transcript if available
        if transcript_file and transcript_file.exists():
            try:
                lines = transcript_file.read_text(encoding="utf-8").splitlines()
                for line_str in lines:
                    line_str = line_str.strip()
                    if not line_str:
                        continue
                    entry = json.loads(line_str)
                    step_idx = entry.get("step_index", 0)

                    if step_idx > last_step_index:
                        last_step_index = step_idx
                        source = entry.get("source")
                        entry_type = entry.get("type")
                        status = entry.get("status")
                        thinking = entry.get("thinking", "")
                        tool_calls = entry.get("tool_calls", [])
                        content = entry.get("content", "")

                        # Extract step activity
                        if tool_calls:
                            for tc in tool_calls:
                                tname = tc.get("name", "")
                                targs = tc.get("args", {})
                                if tname == "write_file":
                                    target = targs.get("Path", "")
                                    task.current_step = f"در حال نگارش فایل {Path(target).name}..."
                                    task.add_log(f"ویرایش فایل: {Path(target).name}")
                                elif tname in ["image-generator", "invoke_subagent"]:
                                    task.current_step = "در حال فراخوانی مدل تصویرسازی بومی برای تولید فریم..."
                                    task.add_log("درخواست تولید فریم تصویری")
                                else:
                                    task.current_step = f"اجرای ابزار {tname}..."
                        elif thinking:
                            # Shorten thought for UI display
                            first_thought = thinking.strip().split("\n")[0][:100]
                            task.current_step = f"تحلیل هوش مصنوعی: {first_thought}..."
                        elif content and source == "MODEL":
                            task.add_log(f"پیام ایجنت: {content[:80]}...")

                        # Check if agent finished
                        if status == "DONE" and entry_type == "PLANNER_RESPONSE" and not tool_calls:
                            consecutive_done_checks += 1
                        else:
                            consecutive_done_checks = 0

            except Exception as e:
                logger.warning("Error reading transcript for %s: %e", conv_id, e)

        # Progress calculation
        if task.task_type == "storyboard":
            if consecutive_done_checks >= 1:
                task.progress = 100
                task.status = "completed"
                task.current_step = "نگارش استوری‌بورد و پرامپت‌ها با موفقیت به پایان رسید."
                task.add_log("عملیات استوری‌بورد کامل شد.")
                break
            else:
                # Approximate storyboard progress over time
                elapsed = time.time() - start_time
                task.progress = min(90, int(elapsed * 2))

        elif task.task_type == "images":
            if task.total_scenes > 0:
                task.progress = min(100, int((task.completed_scenes / task.total_scenes) * 100))
            if consecutive_done_checks >= 1 and (task.completed_scenes >= task.total_scenes or task.completed_scenes > initial_img_count):
                task.progress = 100
                task.status = "completed"
                task.current_step = f"تولید تصاویر به پایان رسید ({task.completed_scenes} فریم موجود)."
                task.add_log("تولید کامل تصاویر خاتمه یافت.")
                break

        elif task.task_type == "regenerate_scene":
            if consecutive_done_checks >= 1:
                task.progress = 100
                task.status = "completed"
                task.current_step = f"بازسازی تصویر {task.target_scene_id} با موفقیت انجام شد."
                task.add_log(f"بازسازی فریم {task.target_scene_id} تکمیل شد.")
                break
            else:
                task.progress = min(90, int((time.time() - start_time) * 3))

    if task.status == "running":
        if consecutive_done_checks >= 1:
            task.status = "completed"
            task.current_step = "عملیات ایجنت با موفقیت پایان یافت."
        else:
            task.status = "error"
            task.error_message = "زمان اجرای عملیات ایجنت به پایان رسید (Timeout)."
            task.add_log("خطا: تایم‌اوت در انتظار پایان وظیفه.")


async def start_storyboard_generation(episode_id: str) -> EpisodeTask:
    """
    Starts Phase 1 (Storyboard & Prompts generation) via Antigravity CLI.
    """
    task = get_task_for_episode(episode_id)
    if task.status == "running":
        return task

    task.task_type = "storyboard"
    task.status = "running"
    task.progress = 5
    task.error_message = None
    task.started_at = time.time()
    task.logs = []
    task.current_step = "راه‌اندازی ایجنت کارگردان آنتی‌گرویتی برای نگارش استوری‌بورد..."
    task.add_log(f"درخواست شروع استوری‌بورد برای اپیزود {episode_id}")

    prompt = f"""You are the Lead Scene Director Agent for Poker Studio.
Execute PHASE 1 (Storyboard Generation) strictly following `/.agent/skills/04-scene-director.md`.

CRITICAL CONSTRAINTS:
1. Read `universe.json` and `/projects/{episode_id}/state.json`.
2. Do NOT generate any image files in this step. Generate ONLY the storyboard JSON data.
3. For every scene in the episode (scene_01, scene_02, ...):
   - Write an exhaustive, cinema-grade `visual_prompt_en` (minimum 80–120 words) with the 6-part anatomy: camera angle/framing (@Room_Master, @Seat_X), focal character micro-expression and posture, adjacent seated players at frame edges, persistent table state and props, Scene 1 master continuity lock, and handcrafted needle-felted stop-motion style lock.
   - For every scene where `media_type` is "static_image": determine the dramatic camera movement and output structured `camera_direction`:
     {{
       "motion_type": "slow_zoom_in | fast_punch_in | slow_zoom_out | pan_left_to_right | pan_right_to_left | tilt_up | tilt_down | subtle_tilt_shake | static_hold",
       "start_focus_region": "...",
       "end_focus_region": "...",
       "zoom_intensity": 1.15,
       "easing": "smooth | dramatic_punch",
       "camera_prompt_en": "..."
     }}
   - For every scene where `media_type` is "ai_video": write a dedicated `motion_prompt_en` describing puppet physical acting, micro-motion, and physics.
4. Save the updated `scenes` list directly into `/projects/{episode_id}/state.json`, preserving all other episode state fields.
5. Once saved, confirm that Phase 1 storyboard is written to `/projects/{episode_id}/state.json`.
"""

    try:
        conv_id = await _run_antigravity_cli_process(prompt, f"Storyboard Generator ({episode_id})")
        task.conversation_id = conv_id
        task.add_log(f"نشست ایجنت با شناسه {conv_id} آغاز شد.")
        # Launch background monitor
        asyncio.create_task(_monitor_task(task))
    except Exception as e:
        task.status = "error"
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")

    return task


async def start_images_generation(episode_id: str) -> EpisodeTask:
    """
    Starts Phase 2 (Sequential Image Generation) via Antigravity CLI.
    """
    task = get_task_for_episode(episode_id)
    if task.status == "running":
        return task

    task.task_type = "images"
    task.status = "running"
    task.progress = 5
    task.error_message = None
    task.started_at = time.time()
    task.logs = []
    task.current_step = "راه‌اندازی ایجنت تولید تصویر بومی آنتی‌گرویتی..."
    task.add_log(f"درخواست شروع تولید متوالی تصاویر برای اپیزود {episode_id}")

    prompt = f"""You are the Visual Production Agent for Poker Studio.
Execute PHASE 2 (Sequential Image Generation) strictly following `/.agent/skills/04-scene-director.md`.

CRITICAL EXECUTION PROTOCOL:
1. Read `/projects/{episode_id}/state.json` to load the approved storyboard scenes.
2. Read `universe.json` to locate the reference image paths for Room Master, Seats, and active character face/body sheets.
3. Sequentially generate keyframe images for each scene directly into `/projects/{episode_id}/assets/images/`:
   - For `scene_01.png`: use `@Room_Master` and the active characters' face/body sheets as visual references.
   - For `scene_02.png` through `scene_N.png`: pass `/projects/{episode_id}/assets/images/scene_01.png` (as the Episode Master Reference) + the focal `@Seat_X` reference + active character sheets to enforce 100% visual and spatial continuity.
4. Verify each generated image file exists and is non-empty before proceeding to the next frame.
5. Update `image_path` in `/projects/{episode_id}/state.json` for each scene.
6. Once all frames are generated, provide a summary confirmation of all generated scene images.
"""

    try:
        conv_id = await _run_antigravity_cli_process(prompt, f"Image Generator ({episode_id})")
        task.conversation_id = conv_id
        task.add_log(f"نشست ایجنت با شناسه {conv_id} آغاز شد.")
        # Launch background monitor
        asyncio.create_task(_monitor_task(task))
    except Exception as e:
        task.status = "error"
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")

    return task


async def start_scene_regeneration(episode_id: str, scene_id: str) -> EpisodeTask:
    """
    Regenerates a single scene image via Antigravity CLI.
    """
    task = get_task_for_episode(episode_id)
    if task.status == "running":
        return task

    task.task_type = "regenerate_scene"
    task.target_scene_id = scene_id
    task.status = "running"
    task.progress = 10
    task.error_message = None
    task.started_at = time.time()
    task.logs = []
    task.current_step = f"راه‌اندازی ایجنت برای بازسازی فریم {scene_id}..."
    task.add_log(f"درخواست بازسازی فریم {scene_id} در اپیزود {episode_id}")

    prompt = f"""You are the Visual Production Agent for Poker Studio.
Regenerate keyframe image for scene `{scene_id}` in episode `{episode_id}` following `/.agent/skills/04-scene-director.md`.

CRITICAL INSTRUCTIONS:
1. Read `/projects/{episode_id}/state.json` and find the specific scene `{scene_id}`.
2. Read `visual_prompt_en` for `{scene_id}`.
3. Use `/projects/{episode_id}/assets/images/scene_01.png` as Episode Master Reference (if scene is not scene_01), plus the focal `@Seat_X` reference and character sheets from `universe.json`.
4. Generate the new image and write it directly to `/projects/{episode_id}/assets/images/{scene_id}.png`.
5. Verify the file is written and non-empty.
6. Update `state.json` if needed and confirm completion.
"""

    try:
        conv_id = await _run_antigravity_cli_process(prompt, f"Regenerate Frame {scene_id} ({episode_id})")
        task.conversation_id = conv_id
        task.add_log(f"نشست ایجنت با شناسه {conv_id} آغاز شد.")
        # Launch background monitor
        asyncio.create_task(_monitor_task(task))
    except Exception as e:
        task.status = "error"
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")

    return task
