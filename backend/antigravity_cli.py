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
import re
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from backend.services.paths import InvalidIdError, get_project_dir, validate_episode_id, validate_scene_id
except ImportError:  # pragma: no cover
    from services.paths import InvalidIdError, get_project_dir, validate_episode_id, validate_scene_id

try:
    from backend.services.state_store import (
        read_state, update_state, snapshot_state, restore_state_from, write_json_atomic
    )
    from backend.services.scene_schema import normalize_scene, validate_scenes
except ImportError:  # pragma: no cover
    from services.state_store import (
        read_state, update_state, snapshot_state, restore_state_from, write_json_atomic
    )
    from services.scene_schema import normalize_scene, validate_scenes

logger = logging.getLogger("antigravity_cli")
logger.setLevel(logging.INFO)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
_HOME = Path(os.environ.get("USERPROFILE") or Path.home())
GEMINI_DIR = _HOME / ".gemini"
BRAIN_DIR = Path(os.environ.get("ANTIGRAVITY_BRAIN_DIR") or (GEMINI_DIR / "antigravity" / "brain"))

# Locate Antigravity binaries
_LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA") or (_HOME / "AppData" / "Local"))
DEFAULT_LANGUAGE_SERVER = _LOCALAPPDATA / "Programs" / "antigravity" / "resources" / "bin" / "language_server.exe"
PROMPT_DIR = BASE_DIR / ".agent_prompts"

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


def _is_agentapi_cmd(cmd: List[str]) -> bool:
    """True when the resolved CLI is the agentapi style (new-conversation --title=...)."""
    return any(Path(part).name.lower().startswith("agentapi") for part in cmd)


def _stage_prompt_file(prompt: str, title: str) -> Path:
    """Write the long prompt to disk so argv stays short and shell-safe."""
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")[:40] or "task"
    path = PROMPT_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{slug}.md"
    path.write_text(prompt, encoding="utf-8")
    return path


class EpisodeTask:
    """Tracks the state of an Antigravity background task for an episode."""
    def __init__(self, episode_id: str, task_type: str):
        self._status = "idle"
        self.episode_id = episode_id
        self.task_type = task_type  # "storyboard", "images", "regenerate_scene"
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
        self.cancel_requested = False
        self.snapshot_path: Optional[str] = None

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value
        self._persist()

    def _persist(self) -> None:
        try:
            write_json_atomic(get_project_dir(self.episode_id) / "task_status.json", self.to_dict())
        except Exception as exc:  # persistence must never break the task
            logger.warning("Could not persist task status for %s: %s", self.episode_id, exc)

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
_background_tasks: set = set()
_SCENE_IMG_RE = re.compile(r"^scene_\d{2,3}\.(png|jpg|jpeg)$", re.IGNORECASE)
MIN_IMAGE_BYTES = 50 * 1024


def _spawn(coro) -> None:
    t = asyncio.create_task(coro)
    _background_tasks.add(t)
    t.add_done_callback(_background_tasks.discard)


def _load_persisted(task: EpisodeTask) -> None:
    path = get_project_dir(task.episode_id) / "task_status.json"
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    task.task_type = data.get("task_type", "idle")
    task.conversation_id = data.get("conversation_id")
    task.started_at = data.get("started_at", task.started_at)
    task.logs = data.get("logs", [])[-60:]
    task.target_scene_id = data.get("target_scene_id")
    task.progress = data.get("progress", 0)
    status = data.get("status", "idle")
    if status == "running":
        task.error_message = ("Server restarted while this task was running; the agent session may still be active "
                              f"(conversation {task.conversation_id}). Check Antigravity, then re-run if needed.")
        task._status = "error"
    else:
        task.error_message = data.get("error_message")
        task._status = status
    task.current_step = data.get("current_step", task.current_step)


def get_task_for_episode(episode_id: str) -> EpisodeTask:
    validate_episode_id(episode_id)
    if episode_id not in _active_tasks:
        task = EpisodeTask(episode_id, "idle")
        _active_tasks[episode_id] = task
        _load_persisted(task)
        # Check existing images on disk
        _refresh_image_status(task)
    return _active_tasks[episode_id]


def _refresh_image_status(task: EpisodeTask) -> None:
    try:
        proj_dir = get_project_dir(task.episode_id)
    except InvalidIdError:
        return
    img_dir = proj_dir / "assets" / "images"
    try:
        task.total_scenes = len(read_state(task.episode_id).get("scenes", []))
    except Exception:
        pass
    found, fresh = [], []
    if img_dir.exists():
        for f in sorted(img_dir.iterdir()):
            if f.is_file() and _SCENE_IMG_RE.match(f.name):
                found.append(f.name)
                try:
                    st = f.stat()
                    if st.st_mtime >= task.started_at - 1 and st.st_size >= MIN_IMAGE_BYTES:
                        fresh.append(f.name)
                except OSError:
                    pass
    task.generated_images = found
    running = task.status == "running" and task.task_type in ("images", "regenerate_scene")
    task.completed_scenes = len(fresh if running else found)
    if task.total_scenes > 0 and task.task_type == "images":
        pct = int(task.completed_scenes / task.total_scenes * 100)
        task.progress = min(95, pct) if task.status == "running" else min(100, pct)


async def _run_antigravity_cli_process(prompt: str, title: str) -> Optional[str]:
    """
    Executes the Antigravity CLI in non-interactive/headless mode,
    returning the conversationId.
    """
    cmd = get_cli_command()
    prompt_file = _stage_prompt_file(prompt, title)
    short_prompt = (
        f"Read the file {prompt_file.as_posix()} completely, then execute every instruction "
        "in it exactly. Do not ask clarifying questions."
    )
    # Format arguments depending on binary type
    if _is_agentapi_cmd(cmd):
        full_cmd = cmd + [f"--title={title}", short_prompt]
    else:
        full_cmd = cmd + ["--title", title, short_prompt]

    logger.info("Executing Antigravity CLI: %s", " ".join(full_cmd[:4]))

    # Execute asynchronously in BASE_DIR
    proc = await asyncio.create_subprocess_exec(
        *full_cmd,
        cwd=str(BASE_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError("Antigravity CLI did not respond within 120 seconds.")
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
    match = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", out_text)
    if match:
        return match.group(1)

    raise RuntimeError(f"Could not extract conversationId from output: {out_text or 'Empty output'}")


def _read_new_transcript_lines(path: Path, offset: int):
    """Return (complete_lines, new_offset). Safe against partially written last line."""
    if not path.exists():
        return [], offset
    if path.stat().st_size < offset:
        offset = 0
    with path.open("rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    last_nl = chunk.rfind(b"\n")
    if last_nl == -1:
        return [], offset
    complete = chunk[: last_nl + 1]
    lines = [ln for ln in complete.decode("utf-8", errors="replace").splitlines() if ln.strip()]
    return lines, offset + len(complete)


def _process_transcript_entry(task: EpisodeTask, entry: Dict[str, Any]) -> bool:
    """Update task.current_step/logs; return True if this entry looks like the agent's final answer."""
    source = entry.get("source")
    entry_type = entry.get("type")
    status = entry.get("status")
    thinking = entry.get("thinking", "")
    tool_calls = entry.get("tool_calls", []) or []
    content = entry.get("content", "")
    if tool_calls:
        for tc in tool_calls:
            tname = tc.get("name", "")
            targs = tc.get("args", {}) or {}
            if tname == "write_file":
                fname = Path(targs.get("Path", "")).name
                task.current_step = f"در حال نگارش فایل {fname}..."
                task.add_log(f"ویرایش فایل: {fname}")
            elif tname in ("image-generator", "invoke_subagent"):
                task.current_step = "در حال فراخوانی مدل تصویرسازی بومی برای تولید فریم..."
                task.add_log("درخواست تولید فریم تصویری")
            else:
                task.current_step = f"اجرای ابزار {tname}..."
    elif thinking:
        task.current_step = f"تحلیل هوش مصنوعی: {thinking.strip().splitlines()[0][:100]}..." if thinking.strip() else task.current_step
    elif content and source == "MODEL":
        task.add_log(f"پیام ایجنت: {str(content)[:80]}...")
    return status == "DONE" and entry_type == "PLANNER_RESPONSE" and not tool_calls


def _restore_snapshot(task: EpisodeTask) -> None:
    if task.snapshot_path and Path(task.snapshot_path).exists():
        restore_state_from(task.episode_id, Path(task.snapshot_path), keep_rejected_as="state.json.rejected")


def _finalize_storyboard(task: EpisodeTask) -> List[str]:
    ep = task.episode_id
    try:
        raw = read_state(ep).get("scenes")
    except Exception as exc:
        return [f"Cannot read state.json: {exc}"]
    if not isinstance(raw, list) or not raw:
        _restore_snapshot(task)
        return ["Agent finished but state.json has no scenes[]. Previous state restored (rejected copy: state.json.rejected)."]
    scenes = [normalize_scene(s, i, ep) for i, s in enumerate(raw) if isinstance(s, dict)]
    errors = validate_scenes(scenes)
    if errors:
        _restore_snapshot(task)
        return ["Storyboard rejected; previous state restored (rejected copy: state.json.rejected)."] + errors
    update_state(ep, lambda s: s.__setitem__("scenes", scenes))
    return []


def _finalize_images(task: EpisodeTask) -> List[str]:
    ep = task.episode_id
    try:
        scenes = read_state(ep).get("scenes", [])
    except Exception as exc:
        return [f"Cannot read state.json: {exc}"]
    ids = [task.target_scene_id] if task.task_type == "regenerate_scene" else [s.get("scene_id") or s.get("id") for s in scenes]
    img_dir = get_project_dir(ep) / "assets" / "images"
    found, missing = {}, []
    for sid in ids:
        hit = None
        for ext in ("png", "jpg", "jpeg"):
            f = img_dir / f"{sid}.{ext}"
            if f.exists() and f.stat().st_size >= MIN_IMAGE_BYTES and f.stat().st_mtime >= task.started_at - 1:
                hit = (ext, int(f.stat().st_mtime))
                break
        if hit:
            found[sid] = hit
        else:
            missing.append(str(sid))
    if missing:
        return [f"Missing or stale frames (<{MIN_IMAGE_BYTES // 1024}KB or not regenerated): {', '.join(missing)}"]

    def _mutate(state: dict) -> None:
        for sc in state.get("scenes", []):
            sid = sc.get("scene_id") or sc.get("id")
            if sid in found:
                ext, ver = found[sid]
                path = f"/media/{ep}/assets/images/{sid}.{ext}"
                sc["image_path"] = path
                sc["visual_asset"] = path
                sc["image_version"] = ver
                if sc.get("status") != "approved":
                    sc["status"] = "ready_for_review"

    update_state(ep, _mutate)
    return []


async def _finalize_task(task: EpisodeTask) -> None:
    fn = _finalize_storyboard if task.task_type == "storyboard" else _finalize_images
    errors = await asyncio.to_thread(fn, task)
    if errors:
        task.error_message = "\n".join(errors[:10])
        task.current_step = "خروجی ایجنت معتبر نبود."
        task.add_log("خطای اعتبارسنجی: " + errors[0])
        task.status = "error"
    else:
        task.progress = 100
        task.error_message = None
        task.current_step = "عملیات با موفقیت و پس از اعتبارسنجی پایان یافت."
        task.add_log("عملیات تکمیل و اعتبارسنجی شد.")
        task.status = "completed"


async def _monitor_task(task: EpisodeTask) -> None:
    try:
        await _monitor_task_inner(task)
    except Exception as exc:  # never leave the task stuck in "running"
        logger.exception("Monitor crashed for %s", task.episode_id)
        task.error_message = f"Monitor crashed: {exc}"
        task.add_log(f"خطای مانیتور: {exc}")
        task.status = "error"


async def _monitor_task_inner(task: EpisodeTask) -> None:
    conv_id = task.conversation_id
    transcript = BRAIN_DIR / conv_id / ".system_generated" / "logs" / "transcript.jsonl" if conv_id else None
    offset, last_step, finished, stable = 0, -1, False, 0
    start = time.time()
    max_wait = 1800
    while time.time() - start < max_wait:
        await asyncio.sleep(2.0)
        if task.cancel_requested:
            task.current_step = "پایش متوقف شد (نشست ایجنت ممکن است هنوز در Antigravity فعال باشد)."
            task.add_log("لغو توسط کاربر.")
            task.status = "cancelled"
            return
        await asyncio.to_thread(_refresh_image_status, task)
        if transcript is None:
            task.error_message = "No conversationId; cannot monitor."
            task.status = "error"
            return
        if not transcript.exists() and time.time() - start > 120:
            task.error_message = f"Transcript not found: {transcript}. Check ANTIGRAVITY_BRAIN_DIR."
            task.status = "error"
            return
        lines, offset = await asyncio.to_thread(_read_new_transcript_lines, transcript, offset)
        for line in lines:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            idx = entry.get("step_index", 0)
            if idx <= last_step:
                continue
            last_step = idx
            finished = _process_transcript_entry(task, entry)
        stable = stable + 1 if finished else 0
        if stable >= 2:
            await _finalize_task(task)
            return
        if task.task_type != "images":
            task.progress = max(task.progress, min(90, int((time.time() - start) * 0.5)))
    task.error_message = "زمان اجرای عملیات ایجنت به پایان رسید (Timeout)."
    task.add_log("خطا: تایماوت در انتظار پایان وظیفه.")
    task.status = "error"


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
    task.cancel_requested = False
    task.started_at = time.time()
    task.logs = []
    task.current_step = "راه‌اندازی ایجنت کارگردان آنتی‌گرویتی برای نگارش استوری‌بورد..."
    task.add_log(f"درخواست شروع استوری‌بورد برای اپیزود {episode_id}")
    try:
        task.snapshot_path = str(snapshot_state(episode_id, "state.json.pre_storyboard.bak"))
    except FileNotFoundError:
        task.error_message = f"state.json not found for episode {episode_id}"
        task.status = "error"
        return task

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
        _spawn(_monitor_task(task))
    except Exception as e:
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")
        task.status = "error"

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
    task.snapshot_path = None
    task.cancel_requested = False
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
        _spawn(_monitor_task(task))
    except Exception as e:
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")
        task.status = "error"

    return task


async def start_scene_regeneration(episode_id: str, scene_id: str) -> EpisodeTask:
    """
    Regenerates a single scene image via Antigravity CLI.
    """
    validate_scene_id(scene_id)
    task = get_task_for_episode(episode_id)
    if task.status == "running":
        return task

    task.task_type = "regenerate_scene"
    task.target_scene_id = scene_id
    task.status = "running"
    task.progress = 10
    task.error_message = None
    task.snapshot_path = None
    task.cancel_requested = False
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
        _spawn(_monitor_task(task))
    except Exception as e:
        task.error_message = str(e)
        task.add_log(f"خطا در اجرای ایجنت: {e}")
        task.status = "error"

    return task


def cancel_task(episode_id: str) -> EpisodeTask:
    task = get_task_for_episode(episode_id)
    if task.status == "running":
        task.cancel_requested = True
        task.add_log("درخواست لغو ثبت شد.")
    return task
