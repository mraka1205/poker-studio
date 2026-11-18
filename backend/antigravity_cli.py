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
        for line in str(message).strip().splitlines():
            line = line.strip()
            if line:
                self.logs.append(f"[{timestamp}] {line}")
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
        err_msg = err_text or out_text or f"Process failed with returncode {proc.returncode}"
        logger.error("Antigravity CLI failed with code %d: %s", proc.returncode, err_msg)
        raise RuntimeError(f"Antigravity CLI returned code {proc.returncode}: {err_msg}")

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

    raise RuntimeError(f"Could not extract conversationId from output: {out_text or 'Empty output'}")


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
   - Include a structured `table_blueprint` object:
     {{
       "community_cards": {{ "stage": "preflop|flop|turn|river", "cards": ["..."], "layout": "..." }},
       "pot": {{ "total_bb": 4.5, "visual": "...", "position": "center of table" }},
       "player_zones": {{ "seat_1": {{ "character": "@Arash", "chip_stack": "...", "cards": "...", "props": "..." }}, ... }},
       "persistent_props": ["emerald green wool felt", "dark brown leather rail", ...],
       "lighting": "soft warm overhead studio macro lighting"
     }}
   - Write an exhaustive, cinema-grade `visual_prompt_en` (minimum 80–120 words) using the 8-part prompt anatomy formula:
     [1. CONTINUITY_LOCK (from scene_02+)] + [2. STYLE_LOCK] + [3. CAMERA_ANGLE_&_FRAMING] + [4. FOCAL_CHARACTER_DNA_&_ACTING] + [5. ADJACENT_CHARACTERS_AT_EDGES] + [6. TABLE_BLUEPRINT_STATE] + [7. PERSISTENT_PROPS_&_LANDMARKS] + [8. LIGHTING_&_COMPOSITION_LOCK]
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

    prompt = f"""You are the Visual Production & Continuity Director for Poker Studio.
Execute PHASE 2 (Sequential Image Generation) strictly following `/.agent/skills/04-scene-director.md` and the 5-Layer Visual Continuity Strategy.

═══════════════════════════════════════════════════════════════
CRITICAL CONTINUITY PROTOCOL:
═══════════════════════════════════════════════════════════════

1. PRE-FLIGHT CHECK:
   - Read `/projects/{episode_id}/state.json` to load approved scenes with `table_blueprint`.
   - Read `universe.json` to load image paths: `@Room_Master`, `@Seat_1`..`@Seat_6`, and character face/body sheets.

2. MASTER FRAME (scene_01.png):
   - Generate `scene_01.png` first using `@Room_Master` reference and active character face/body sheets.
   - Verify `scene_01.png` is generated, non-empty, and establishes canonical table felt, chip colors (red=5BB, green=25BB, black=100BB), lighting, and props.
   - This file is the EPISODE MASTER REFERENCE for all subsequent frames.

3. SEQUENTIAL GENERATION (scene_02.png through scene_N.png):
   For EVERY subsequent frame, strictly in order:
   - MANDATORY REFERENCES: ALWAYS pass `/projects/{episode_id}/assets/images/scene_01.png` as Master Reference, PLUS the camera angle reference (e.g. `@Seat_X`), PLUS active character sheets.
   - CONTINUITY HEADER: Prepend to the prompt:
     "Maintain exact visual continuity with the provided reference image: identical emerald green wool table felt, identical chip colors (red/green/black miniature felt chips), identical warm amber studio macro lighting direction, identical dark brown leather rail, identical brass chandelier, identical background landmarks per seat position. All character clothing, accessories, hair color, and puppet proportions must match their character reference sheets exactly."
   - INJECT TABLE BLUEPRINT: Include exact community cards, pot size in BB, and player chip stacks.
   - INJECT CHARACTER DNA: Use each character's exact physical DNA block from universe.json.

4. POST-GENERATION VERIFICATION:
   - Verify generated image exists and is non-empty.
   - Update `image_path` and `visual_asset` in `/projects/{episode_id}/state.json`.
   - Ensure visual continuity of felt, chips, and characters across consecutive scenes.
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

    prompt = f"""You are the Visual Production & Continuity Director for Poker Studio.
Regenerate keyframe image for scene `{scene_id}` in episode `{episode_id}` following `/.agent/skills/04-scene-director.md` and the 5-Layer Visual Continuity Strategy.

═══════════════════════════════════════════════════════════════
CRITICAL CONTINUITY PROTOCOL FOR SCENE REGENERATION:
═══════════════════════════════════════════════════════════════

1. PRE-FLIGHT & BLUEPRINT CHECK:
   - Read `/projects/{episode_id}/state.json` and find specific scene `{scene_id}`.
   - Extract `table_blueprint`, `visual_prompt_en`, `characters_present`, and `camera_angle` for `{scene_id}`.
   - Read `universe.json` to load character physical DNA blocks (`dna_block_en`), face/body sheets, and the angle reference image (`@Seat_X` or `@Room_Master`).

2. MASTER FRAME REFERENCE:
   - If `{scene_id}` != "scene_01": ALWAYS pass `/projects/{episode_id}/assets/images/scene_01.png` as Episode Master Reference, PLUS the specific `@Seat_X` angle reference from universe.json, PLUS active character face/body sheets.
   - If `{scene_id}` == "scene_01": Use `@Room_Master` reference and active character face/body sheets from `universe.json` to re-establish the master baseline.

3. CONTINUITY ENFORCEMENT & 8-PART PROMPT FORMULA:
   - MANDATORY CONTINUITY HEADER (Prepend to the image generation prompt):
     "Maintain exact visual continuity with Episode Master Reference (scene_01.png): identical emerald green wool table felt texture, identical chip colors (red=5BB, green=25BB, black=100BB miniature felt discs), identical warm amber studio macro lighting direction, identical dark brown leather rail, identical brass chandelier, identical background landmarks per seat position. Character clothing, hair, spectacles, mustache, and felt puppet proportions must strictly match character DNA blocks."
   - TABLE BLUEPRINT ENFORCEMENT:
     * Community cards on felt must match `{scene_id}`'s `table_blueprint.community_cards`.
     * Pot chips in center of felt must visually reflect `table_blueprint.pot.total_bb`.
     * Focal player's chip stack must match `table_blueprint.player_zones`.
   - CHARACTER DNA ENFORCEMENT:
     * Use each present character's exact physical `dna_block_en` from `universe.json`.
   - Follow the 8-Part Prompt Anatomy strictly:
     [1. CONTINUITY_LOCK] + [2. STYLE_LOCK] + [3. CAMERA_ANGLE_&_FRAMING] + [4. FOCAL_CHARACTER_DNA_&_ACTING] + [5. ADJACENT_CHARACTERS_AT_EDGES] + [6. TABLE_BLUEPRINT_STATE] + [7. PERSISTENT_PROPS_&_LANDMARKS] + [8. LIGHTING_&_COMPOSITION_LOCK]

4. POST-GENERATION VERIFICATION & REPLACEMENT:
   - Generate the new image and write it directly to `/projects/{episode_id}/assets/images/{scene_id}.png`.
   - Verify the file is written and non-empty (>50KB).
   - Verify that felt color, chip design, character facial features, and lighting are strictly consistent with scene_01.png.
   - Update `/projects/{episode_id}/state.json` (`image_path` and `visual_asset` for `{scene_id}`) and confirm completion.
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
