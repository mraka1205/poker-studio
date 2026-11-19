import json
import shutil
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.antigravity_cli import (
    get_task_for_episode,
    start_storyboard_generation,
    start_images_generation,
    start_scene_regeneration,
)
from backend.services.paths import (
    get_project_dir,
    InvalidIdError,
    projects_dir,
    validate_scene_id,
    validate_episode_id,
)
from backend.services.state_store import (
    apply_patch,
    compute_etag,
    EtagConflict,
    read_state,
    read_universe,
    restore_state_from,
    snapshot_state,
    update_state,
    write_state,
    write_universe,
)
from backend.services.tts_validator import validate_segments
from backend.services.scene_schema import normalize_scene, validate_scenes
from backend.services.scene_prompt_builder import build_episode_prompts
from backend.services.seat_geometry import merge_roster, format_seating_summary, RosterError
from backend.services.visual_canon import SEED_ENV_CANON
from backend.services.camera_ffmpeg import build_scene_clip_command

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / ".agent" / "skills"

app = FastAPI(title="Poker Studio API", version="2.0.0")


@app.exception_handler(InvalidIdError)
async def _invalid_id_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure core directories exist
projects_dir().mkdir(parents=True, exist_ok=True)
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# Mount media directory for images, audio, exports
app.mount("/media", StaticFiles(directory=str(projects_dir())), name="media")


def get_project_path(episode_id: str) -> Path:
    proj_path = get_project_dir(episode_id)
    if not proj_path.exists() or not proj_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found")
    return proj_path


def _sanitize_token(value: Optional[str]) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str):
        value = str(value)
    stripped = value.strip()
    if not stripped:
        raise HTTPException(status_code=400, detail="Invalid identifier")
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", stripped)
    if not cleaned or cleaned != stripped:
        raise HTTPException(status_code=400, detail="Invalid identifier")
    return cleaned


def load_state(episode_id: str) -> Dict[str, Any]:
    proj_dir = get_project_path(episode_id)
    state_file = proj_dir / "state.json"
    if not state_file.exists():
        raise HTTPException(status_code=404, detail="state.json not found in episode folder")
    data = read_state(episode_id)

    # Automatically resolve scene image paths if files exist on disk
    assets_img_dir = proj_dir / "assets" / "images"
    scenes_dir = proj_dir / "scenes"

    scenes = data.get("scenes", [])
    for scene in scenes:
        s_id = scene.get("id") or scene.get("scene_id")
        if not s_id:
            continue

        existing_img = scene.get("image_path")
        exists_on_disk = False
        if existing_img:
            img_str = str(existing_img)
            if img_str.startswith(f"/media/{episode_id}/"):
                rel = img_str[len(f"/media/{episode_id}/"):]
                exists_on_disk = (proj_dir / rel).is_file()
            elif img_str.startswith("/media/"):
                rel = img_str[len("/media/"):]
                exists_on_disk = (projects_dir() / rel).is_file()
            else:
                p = Path(img_str)
                exists_on_disk = p.is_file() or (proj_dir / img_str).is_file()

        if not exists_on_disk:
            found_path = None
            # Check assets/images first
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                p = assets_img_dir / f"{s_id}{ext}"
                if p.exists():
                    found_path = f"/media/{episode_id}/assets/images/{s_id}{ext}"
                    break
            # Fallback to scenes directory
            if not found_path:
                for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
                    p = scenes_dir / f"{s_id}{ext}"
                    if p.exists():
                        found_path = f"/media/{episode_id}/scenes/{s_id}{ext}"
                        break

            if found_path:
                scene["image_path"] = found_path
                scene["visual_asset"] = found_path

    return data


def save_state(episode_id: str, data: Dict[str, Any]):
    get_project_path(episode_id)
    write_state(episode_id, data)


# ==========================================
# CHANNEL UNIVERSE (Fixed Poker Room & Global Cast)
# ==========================================

def _default_universe() -> Dict[str, Any]:
    return {
        "version": "1.2.0",
        "visual_canon_version": "1.0",
        "environment": {
            "id": "env_poker_room",
            "flow_tag": "@PokerRoom",
            "name": "میز زیرزمینی پوکر (The Underground Poker Room)",
            "description_fa": "اتاق اختصاصی پوکر زیرزمینی در تهران. میز بیضی ۶ نفره با نمد سبز تیره، صندلی‌های چرمی قهوه‌ای، دیوار آجری تیره با قفسه کتاب چوبی و تابلوهای هنری مدرن.",
            "visual_prompt_en": "Handcrafted needle-felted stop-motion animation style, miniature underground poker room, 6-max oval poker table with rich emerald green wool felt, dark mahogany wood trim, plush brown leather armrests. In background, dark needle-felted exposed brick walls with warm LED-lit wooden bookshelves holding antique trophies and old books, dark velvet curtains. Warm focused overhead brass chandelier casting soft glow on felt, subtle volumetric dust motes, rich tactile textures, vertical 9:16 composition --ar 9:16",
            "reference_image_path": "",
            "camera_angles": [],
            "canon_en": dict(SEED_ENV_CANON)
        },
        "characters": []
    }


def load_universe() -> Dict[str, Any]:
    (projects_dir() / "universe").mkdir(parents=True, exist_ok=True)
    return read_universe(default_factory=_default_universe)


def save_universe(data: Dict[str, Any]):
    write_universe(data)


def clean_and_parse_json(raw_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(raw_input, dict):
        return raw_input
    text = str(raw_input).strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        raise HTTPException(
            status_code=400,
            detail="فرمت ورودی نامعتبر است. خروجی باید یک شیء یا آرایه معتبر JSON باشد."
        )


@app.get("/api/health")
def health_check():
    return {
        "status": "ok", 
        "app": "Poker Studio Backend (Antigravity Native)", 
        "version": "2.0.0",
        "time": datetime.now().isoformat()
    }


# ==========================================
# CHANNEL UNIVERSE ENDPOINTS
# ==========================================

@app.get("/api/universe")
def get_universe():
    return load_universe()


@app.put("/api/universe")
def update_universe(data: Dict[str, Any]):
    save_universe(data)
    return {"status": "success", "message": "دنیای کانال با موفقیت ذخیره شد"}


@app.post("/api/universe/upload/{asset_type}")
async def upload_universe_asset(
    asset_type: str,
    file: UploadFile = File(...),
    character_id: Optional[str] = Form(None),
    angle_id: Optional[str] = Form(None),
    sheet_type: Optional[str] = Form(None)
):
    if asset_type not in ["environment", "character", "angle"]:
        raise HTTPException(status_code=400, detail="Invalid asset_type. Allowed: environment, character, angle")

    raw_name = Path(file.filename or "upload.bin").name
    suffix = Path(raw_name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    safe_char_id = _sanitize_token(character_id)
    safe_angle_id = _sanitize_token(angle_id)
    safe_sheet_type = _sanitize_token(sheet_type)

    safe_filename = raw_name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    if asset_type == "environment":
        dest_filename = f"environment_{safe_filename}"
    elif asset_type == "angle" and safe_angle_id:
        dest_filename = f"angle_{safe_angle_id}_{safe_filename}"
    elif asset_type == "character" and safe_char_id:
        st = f"_{safe_sheet_type}" if safe_sheet_type else ""
        dest_filename = f"char_{safe_char_id}{st}_{safe_filename}"
    else:
        dest_filename = f"{asset_type}_{timestamp}_{safe_filename}"

    universe_media_dir = projects_dir() / "universe"
    universe_media_dir.mkdir(parents=True, exist_ok=True)
    dest_path = (universe_media_dir / dest_filename).resolve()
    if dest_path.parent != universe_media_dir.resolve():
        raise HTTPException(status_code=400, detail="Invalid file path")
    file_path = dest_path
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_url = f"/media/universe/{dest_filename}"

    universe = load_universe()
    if asset_type == "environment":
        universe["environment"]["reference_image_path"] = relative_url
        save_universe(universe)
    elif asset_type == "angle" and safe_angle_id:
        updated = False
        for ang in universe.get("environment", {}).get("camera_angles", []):
            if isinstance(ang, dict) and ang.get("id") == safe_angle_id:
                ang["reference_image_path"] = relative_url
                updated = True
                break
        if updated:
            save_universe(universe)
    elif asset_type == "character" and safe_char_id:
        for c in universe.get("characters", []):
            if c.get("id") == safe_char_id:
                if safe_sheet_type == "face":
                    c["face_sheet_image_path"] = relative_url
                    if not c.get("reference_image_path"):
                        c["reference_image_path"] = relative_url
                elif safe_sheet_type == "body":
                    c["body_sheet_image_path"] = relative_url
                    c["reference_image_path"] = relative_url
                else:
                    c["reference_image_path"] = relative_url
                save_universe(universe)
                break

    return {
        "status": "success",
        "filename": dest_filename,
        "url": relative_url,
        "absolute_path": str(file_path)
    }


class SyncUniverseCharactersRequest(BaseModel):
    character_ids: List[str]


@app.post("/api/projects/{episode_id}/sync-universe-characters")
def sync_universe_characters(episode_id: str, req: SyncUniverseCharactersRequest):
    universe = load_universe()
    u_chars = {c.get("id"): c for c in universe.get("characters", [])}
    
    state = load_state(episode_id)
    ep_chars = state.get("characters", [])
    ep_chars_dict = {c.get("id"): c for c in ep_chars}

    synced_count = 0
    for cid in req.character_ids:
        if cid in u_chars:
            u_c = u_chars[cid]
            clean_name_en = (u_c.get("flow_tag") or "").replace("@", "").strip() or "Character"
            default_seat = u_c.get("default_seat", "seat_1")
            existing_seat = ep_chars_dict.get(cid, {}).get("assigned_seat", default_seat)
            
            ref_img = u_c.get("body_sheet_image_path") or u_c.get("reference_image_path") or u_c.get("face_sheet_image_path") or ""
            face_img = u_c.get("face_sheet_image_path") or ref_img
            body_p = u_c.get("full_body_prompt_en") or u_c.get("visual_prompt_en", "")
            face_p = u_c.get("face_expressions_prompt_en", "")
            persona_p = u_c.get("persona_behavior_prompt") or u_c.get("personality_and_catchphrases_fa", "")

            mapped = {
                "id": u_c.get("id", cid),
                "name_fa": u_c.get("name_fa", "کاراکتر"),
                "name_en": clean_name_en,
                "role": u_c.get("archetype", "Poker Player"),
                "flow_tag": u_c.get("flow_tag", f"@{clean_name_en}"),
                "default_seat": default_seat,
                "assigned_seat": existing_seat,
                "is_style_anchor": u_c.get("is_style_anchor", False),
                "status": "approved",
                "avatar_url": face_img,
                "turnaround_sheet": ref_img,
                "reference_image_path": ref_img,
                "face_sheet_image_path": u_c.get("face_sheet_image_path", ""),
                "body_sheet_image_path": u_c.get("body_sheet_image_path", ""),
                "face_expressions_prompt_en": face_p,
                "full_body_prompt_en": body_p,
                "persona_behavior_prompt": persona_p,
                "voice_description_fa": u_c.get("voice_description_fa", ""),
                "dna_block_en": u_c.get("dna_block_en", ""),
                "short_look_en": u_c.get("short_look_en", ""),
                "acting_beats_en": u_c.get("acting_beats_en", {}),
                "style_prompt": body_p,
                "character_sheet_prompt_en": body_p,
                "consistency_tags": u_c.get("flow_tag", ""),
                "voice_id": "eleven_persian_narrator",
                "tagline": persona_p
            }
            
            if cid in ep_chars_dict:
                existing = ep_chars_dict[cid]
                existing.update(mapped)
            else:
                ep_chars.append(mapped)
                ep_chars_dict[cid] = mapped
            synced_count += 1

    state["characters"] = ep_chars
    save_state(episode_id, state)
    return {
        "status": "success",
        "synced_count": synced_count,
        "characters": ep_chars,
        "message": f"{synced_count} کاراکتر از دنیای کانال با موفقیت با این اپیزود همگام‌سازی شدند"
    }


class UpdateSeatRequest(BaseModel):
    seat: str  # e.g. "seat_1"


@app.post("/api/projects/{episode_id}/characters/{char_id}/seat")
def update_character_seat(episode_id: str, char_id: str, req: UpdateSeatRequest):
    state = load_state(episode_id)
    characters = state.get("characters", [])
    found = False
    for c in characters:
        if c.get("id") == char_id:
            c["assigned_seat"] = req.seat
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="کاراکتر یافت نشد")
    save_state(episode_id, state)
    return {"status": "success", "char_id": char_id, "assigned_seat": req.seat}


# ==========================================
# PROJECTS CRUD & STATE
# ==========================================

@app.get("/api/projects")
def list_projects():
    projects = []
    for item in projects_dir().iterdir():
        if item.is_dir() and item.name != "universe":
            state_file = item / "state.json"
            if state_file.exists():
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    stages = data.get("stages", [])
                    approved_count = sum(1 for s in stages if s.get("status") == "approved")
                    total_stages = len(stages) or 9
                    progress_pct = int((approved_count / total_stages) * 100)
                    
                    projects.append({
                        "episode_id": data.get("episode_id", item.name),
                        "title": data.get("title", item.name),
                        "english_title": data.get("english_title", ""),
                        "current_stage": data.get("current_stage", 1),
                        "stages": stages,
                        "progress_pct": progress_pct,
                        "approved_stages": approved_count,
                        "total_stages": total_stages,
                        "characters_count": len(data.get("characters", [])),
                        "scenes_count": len(data.get("scenes", [])),
                        "audio_tracks_count": len(data.get("audio", {}).get("tracks", []))
                    })
                except Exception as e:
                    projects.append({
                        "episode_id": item.name,
                        "title": item.name,
                        "error": str(e)
                    })
    return {"projects": projects}


@app.get("/api/projects/{episode_id}")
def get_project_state(episode_id: str):
    state = load_state(episode_id)
    state["_etag"] = compute_etag(episode_id)
    return state


@app.put("/api/projects/{episode_id}")
def update_project_state(episode_id: str, new_state: Dict[str, Any]):
    get_project_path(episode_id)
    write_state(episode_id, new_state)
    return {
        "status": "success",
        "message": "State updated successfully",
        "_etag": compute_etag(episode_id),
    }


ALLOWED_PATCH_KEYS = {"script", "characters", "audio", "edit", "publish", "analytics", "idea", "bible", "scenes"}


@app.patch("/api/projects/{episode_id}")
def patch_project(episode_id: str, payload: dict = Body(...)):
    updates = payload.get("updates")
    base_etag = payload.get("base_etag")
    if not isinstance(updates, dict) or not updates:
        raise HTTPException(status_code=400, detail="updates must be a non-empty object")
    bad = set(updates) - ALLOWED_PATCH_KEYS
    if bad:
        raise HTTPException(status_code=400, detail=f"Keys not patchable: {sorted(bad)}")
    if "scenes" in updates and not base_etag:
        raise HTTPException(status_code=400, detail="base_etag is required when patching scenes")
    try:
        new_etag = apply_patch(episode_id, updates, base_etag)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Episode not found")
    except EtagConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"status": "success", "_etag": new_etag}


class StageActionRequest(BaseModel):
    stage_number: int
    status: str  # approved, waiting_approval, in_progress, pending
    notes: Optional[str] = None


@app.post("/api/projects/{episode_id}/stage_status")
def update_stage_status(episode_id: str, req: StageActionRequest):
    state = load_state(episode_id)
    stages = state.get("stages", [])
    
    found = False
    for s in stages:
        if s.get("stage_number") == req.stage_number:
            s["status"] = req.status
            if req.status == "approved":
                s["approved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            if req.notes:
                s["notes"] = req.notes
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=400, detail=f"Stage number {req.stage_number} not found")
        
    if req.status == "approved" and state.get("current_stage") == req.stage_number:
        if req.stage_number < 9:
            state["current_stage"] = req.stage_number + 1
            for next_s in stages:
                if next_s.get("stage_number") == req.stage_number + 1:
                    if next_s.get("status") == "pending":
                        next_s["status"] = "in_progress"

    save_state(episode_id, state)
    return {"status": "success", "current_stage": state.get("current_stage"), "stages": stages}


class NewProjectRequest(BaseModel):
    episode_id: Optional[str] = None
    title: str
    raw_hand_or_concept: Optional[str] = ""
    english_title: Optional[str] = ""
    theme: Optional[str] = ""


class SaveIdeaRequest(BaseModel):
    raw_hand_or_concept: str
    theme: Optional[str] = None
    core_lesson: Optional[str] = None


@app.post("/api/projects/{episode_id}/save-idea")
def save_episode_idea(episode_id: str, req: SaveIdeaRequest):
    state = load_state(episode_id)
    state["idea"] = state.get("idea", {})
    state["idea"]["raw_hand_or_concept"] = req.raw_hand_or_concept
    if req.theme:
        state["idea"]["theme"] = req.theme
    elif req.raw_hand_or_concept and not state["idea"].get("theme"):
        state["idea"]["theme"] = req.raw_hand_or_concept[:80]
    if req.core_lesson is not None:
        state["idea"]["core_lesson"] = req.core_lesson
        
    save_state(episode_id, state)
    return {
        "status": "success",
        "message": "ایده با موفقیت ذخیره شد",
        "idea": state["idea"]
    }


@app.post("/api/projects")
def create_project(req: NewProjectRequest):
    if not req.episode_id or not req.episode_id.strip():
        nums = [
            int(m.group(1))
            for d in projects_dir().iterdir()
            if d.is_dir() and (m := re.match(r"^ep(\d+)", d.name))
        ]
        ep_count = (max(nums) if nums else 0) + 1
        slug = req.english_title or req.title or ""
        ascii_slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
        if not ascii_slug:
            ascii_slug = "episode"
        folder_name = f"ep{ep_count:02d}-{ascii_slug}"[:56]
    else:
        folder_name = validate_episode_id(req.episode_id.strip())

    proj_dir = get_project_dir(folder_name)
    if proj_dir.exists():
        folder_name = f"{folder_name[:55]}-{datetime.now().strftime('%H%M%S')}"
        proj_dir = get_project_dir(folder_name)
        
    for sub in ["audio", "characters", "scenes", "exports", "assets/images"]:
        (proj_dir / sub).mkdir(parents=True, exist_ok=True)
        
    raw_idea = (req.raw_hand_or_concept or req.theme or "").strip()
    theme_text = (req.theme or raw_idea or req.title).strip()

    new_state = {
        "episode_id": folder_name,
        "title": req.title,
        "english_title": req.english_title or "",
        "version": "2.0.0",
        "current_stage": 1,
        "stages": [
            {"id": f"stage_{i}", "stage_number": i, "name_fa": name_fa, "name_en": name_en, "status": "pending", "approved_at": None, "notes": ""}
            for i, (name_fa, name_en) in enumerate([
                ("ایده", "Idea"), ("Bible", "Bible"), ("سناریو", "Script"),
                ("کاراکترها", "Characters"), ("صدا و میکس", "Audio & Mix"),
                ("صحنه‌ها", "Scenes"), ("تدوین", "Edit"),
                ("انتشار", "Publish"), ("عددها", "Analytics")
            ], 1)
        ],
        "idea": {
            "theme": theme_text,
            "raw_hand_or_concept": raw_idea,
            "target_platform": "YouTube Shorts / Instagram Reels (9:16)",
            "core_lesson": "",
            "punchline": ""
        },
        "bible": {
            "visual_style": "Handcrafted needle-felted stop-motion animation style, tactile fuzzy wool textures, warm studio macro lighting, vertical 9:16",
            "frame_aspect_ratio": "9:16",
            "concept_summary": {},
            "hand_details": {},
            "comedy_beats": []
        },
        "characters": [],
        "script": {"title": req.title, "segments": []},
        "scenes": [],
        "audio": {"tracks": []},
        "edit": {
            "subtitle_settings": {
                "font": "Vazirmatn",
                "font_size": 42,
                "direction": "rtl",
                "libass_harfbuzz": True
            }
        },
        "publish": {"platforms": ["YouTube Shorts", "Instagram Reels"], "caption_fa": "", "hashtags": []},
        "analytics": {}
    }
    new_state["stages"][0]["status"] = "in_progress"
    
    write_state(folder_name, new_state)
        
    return {"status": "success", "episode_id": folder_name}


# ==========================================
# ASSET UPLOADS (Characters, Scenes, Audio)
# ==========================================

@app.post("/api/projects/{episode_id}/upload/scene_image")
async def upload_scene_image(
    episode_id: str,
    scene_id: str = Form(...),
    file: UploadFile = File(...)
):
    validate_scene_id(scene_id)
    raw_name = Path(file.filename or "upload.bin").name
    suffix = Path(raw_name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    project_path = get_project_path(episode_id)
    target_dir = project_path / "assets" / "images"
    target_dir.mkdir(parents=True, exist_ok=True)

    dest_path = (target_dir / f"{scene_id}{suffix}").resolve()
    if dest_path.parent != target_dir.resolve():
        raise HTTPException(status_code=400, detail="Invalid file path")
    file_path = dest_path

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/media/{episode_id}/assets/images/{scene_id}{suffix}"
    ver = int(file_path.stat().st_mtime)

    def _mutate_scene_image(st: dict):
        for sc in st.get("scenes", []):
            if sc.get("scene_id") == scene_id or sc.get("id") == scene_id:
                sc["image_path"] = image_url
                sc["visual_asset"] = image_url
                sc["image_version"] = ver
                break

    update_state(episode_id, _mutate_scene_image)

    return {
        "status": "success",
        "scene_id": scene_id,
        "image_url": image_url,
        "image_path": image_url,
        "image_version": ver,
        "absolute_path": str(file_path)
    }


@app.post("/api/projects/{episode_id}/upload/scene_video")
async def upload_scene_video(
    episode_id: str,
    scene_id: str = Form(...),
    file: UploadFile = File(...)
):
    validate_scene_id(scene_id)
    raw_name = Path(file.filename or "upload.bin").name
    suffix = Path(raw_name).suffix.lower()
    if suffix not in {".mp4", ".mov", ".webm"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    project_path = get_project_path(episode_id)
    target_dir = project_path / "scenes"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = f"{scene_id}_motion_{raw_name.replace(' ', '_')}"
    dest_path = (target_dir / safe_filename).resolve()
    if dest_path.parent != target_dir.resolve():
        raise HTTPException(status_code=400, detail="Invalid file path")
    file_path = dest_path
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    video_url = f"/media/{episode_id}/scenes/{safe_filename}"
    
    def _mutate_video(st: dict):
        for sc in st.get("scenes", []):
            if sc.get("id") == scene_id or sc.get("scene_id") == scene_id:
                sc["video_path"] = video_url
                sc["video_asset"] = video_url
                sc["shot_mode"] = "ai_video"
                sc["media_type"] = "ai_video"
                break

    update_state(episode_id, _mutate_video)

    return {
        "status": "success",
        "scene_id": scene_id,
        "video_url": video_url,
        "video_path": video_url,
        "absolute_path": str(file_path)
    }


@app.post("/api/projects/{episode_id}/upload/{asset_type}")
@app.post("/api/projects/{episode_id}/upload")
async def upload_asset(
    episode_id: str,
    asset_type: Optional[str] = None,
    target_type: Optional[str] = Form(None),
    segment_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    chosen_type = asset_type or target_type
    if not chosen_type or chosen_type not in ["characters", "scenes", "audio", "exports", "assets/images"]:
        raise HTTPException(status_code=400, detail="Invalid target/asset type.")

    raw_name = Path(file.filename or "upload.bin").name
    suffix = Path(raw_name).suffix.lower()
    if chosen_type == "audio":
        allowed = {".mp3", ".wav", ".m4a"}
    elif chosen_type == "exports":
        allowed = {".mp4", ".mov", ".webm"}
    else:
        allowed = {".png", ".jpg", ".jpeg", ".webp"}

    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    project_path = get_project_path(episode_id)
    target_dir = project_path / chosen_type
    target_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = raw_name.replace(" ", "_")
    if chosen_type == "audio" and segment_id:
        safe_seg = _sanitize_token(segment_id)
        safe_filename = f"{safe_seg}_{safe_filename}"

    dest_path = (target_dir / safe_filename).resolve()
    if dest_path.parent != target_dir.resolve():
        raise HTTPException(status_code=400, detail="Invalid file path")
    file_path = dest_path
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    relative_url = f"/media/{episode_id}/{chosen_type}/{safe_filename}"
    return {
        "status": "success",
        "filename": safe_filename,
        "url": relative_url,
        "absolute_path": str(file_path)
    }


# =========================================================
# PROMPT BUILDER & JSON IMPORT (Antigravity Agent Workflow)
# =========================================================

def read_skill_file(filename: str) -> str:
    path = SKILLS_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


@app.post("/api/projects/{episode_id}/build-prompt/{stage}")
def build_ai_studio_prompt(episode_id: str, stage: str):
    state = load_state(episode_id)
    stage_key = stage.lower().strip()
    universe = load_universe()
    u_env = universe.get("environment", {})
    u_chars = universe.get("characters", [])
    u_chars_summary = "\n".join([
        f"  - {c.get('flow_tag', '')} ({c.get('name_en') or c.get('name_fa', '')} - {c.get('archetype', '')}):\n    Behavioral & Physical Profile: {c.get('persona_behavior_prompt') or c.get('personality_and_catchphrases_fa', '')}"
        for c in u_chars
    ])
    
    if stage_key in ["1", "2", "bible", "idea"]:
        skill_filename = "01-bible-and-jokes.md"
        skill_content = read_skill_file(skill_filename)
        idea_data = state.get("idea", {})
        raw_idea = (idea_data.get("raw_hand_or_concept") or idea_data.get("theme") or "").strip()
        
        prompt = f"""You are the Lead Comedy Writer & Poker Strategist for a hit Iranian animated comedy & poker YouTube/Instagram channel.
Follow the comprehensive instructions in the Skill Guidelines below to generate the complete Episode Bible in STRICT JSON format.

---
### PERSISTENT CHANNEL UNIVERSE (RECURRING CAST & FIXED ENVIRONMENT):
- Fixed Poker Room: {u_env.get('flow_tag', '@PokerRoom')}
  Visual Environment: {u_env.get('visual_prompt_en') or u_env.get('description_fa', '')}
- Recurring Characters Roster:
{u_chars_summary}
NOTE: You can cast any of the channel's 5 recurring stars (@Arash, @Bijan, @Rahim, @Farzad, @Keyvan) for the episode hand depending on the comedy scenario (or by default use @Arash and @Bijan).

---
### EPISODE CONTEXT:
- Episode ID: {state.get('episode_id')}
- Title (FA): {state.get('title')}
- English Title: {state.get('english_title', 'Persian Poker Comedy')}
- Raw Poker Hand / Idea Description:
{raw_idea}
- Concept / Theme: {idea_data.get('theme', raw_idea or 'Poker strategy and comical mistakes')}
- Core Lesson: {idea_data.get('core_lesson', '')}

---
### SKILL GUIDELINES (from {skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object matching the schema in the skill guidelines.
"""
        return {
            "episode_id": episode_id,
            "stage": stage,
            "skill_file": skill_filename,
            "stage_desc": "تولید کتابچه استراتژی و جوک‌ها (Bible)",
            "prompt": prompt
        }

    elif stage_key in ["3", "script"]:
        skill_filename = "02-persian-script-writer.md"
        skill_content = read_skill_file(skill_filename)
        bible_data = state.get("bible", {})
        
        prompt = f"""You are the Master Persian Poker Comedy Scriptwriter.
Follow the skill instructions below to write the full comedic Iranian poker dialogue script in STRICT JSON format with dual texts (Persian subtitle + fully diacritized TTS pronunciation).

---
### PERSISTENT CHANNEL UNIVERSE:
- Fixed Poker Room: {u_env.get('flow_tag', '@PokerRoom')}
- Recurring Cast:
{u_chars_summary}

---
### EPISODE CONTEXT & BIBLE:
- Episode ID: {state.get('episode_id')}
- Title: {state.get('title')} ({state.get('english_title', '')})
- Bible Summary: {json.dumps(bible_data.get('concept_summary', {}), ensure_ascii=False)}
- Hand Details: {json.dumps(bible_data.get('hand_details', {}), ensure_ascii=False)}
- Comedy Beats & Jokes: {json.dumps(bible_data.get('comedy_beats', []), ensure_ascii=False)}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object with `"script_title"` and `"segments"` array matching the schema in the skill file.
"""
        return {
            "episode_id": episode_id,
            "stage": stage,
            "skill_file": skill_filename,
            "stage_desc": "نگارش سناریو دو متنی (زیرنویس + TTS اعراب‌گذاری‌شده)",
            "prompt": prompt
        }

    elif stage_key in ["4", "characters"]:
        skill_filename = "03-character-anchor.md"
        skill_content = read_skill_file(skill_filename)
        
        prompt = f"""You are the Lead Visual Character Designer & Style Anchor Director.
Generate character visual prompts for this episode's cast in STRICT JSON format following the instructions in {skill_filename}.

---
### PERSISTENT UNIVERSE ENVIRONMENT:
{u_env.get('flow_tag', '@PokerRoom')}: {u_env.get('visual_prompt_en', '')}

### EPISODE CAST & RECURRING CHARACTERS:
{u_chars_summary}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object with key `"characters"` containing character definitions with strict needle-felted stop-motion prompts.
"""
        return {
            "episode_id": episode_id,
            "stage": stage,
            "skill_file": skill_filename,
            "stage_desc": "مدل‌شیت و لنگر استایل کاراکترها",
            "prompt": prompt
        }

    elif stage_key in ["6", "scenes"]:
        skill_filename = "04-scene-director.md"
        skill_content = read_skill_file(skill_filename)
        
        script_segments = state.get("script", {}).get("segments", [])
        ep_characters = state.get("characters", [])
        
        try:
            roster = merge_roster(ep_characters, universe.get("characters", []))
        except RosterError:
            roster = {}
        
        camera_angles = universe.get("environment", {}).get("camera_angles", [])
        seating_summary = format_seating_summary(roster, camera_angles)

        # Build Character DNA blocks summary
        dna_summary_lines = []
        source_chars = list(roster.values()) if roster else (ep_characters if ep_characters else universe.get("characters", []))
        for c in source_chars:
            c_tag = c.get("flow_tag") or c.get("name_en") or c.get("id")
            dna = c.get("dna_block_en", "")
            if not dna:
                u_char = next((x for x in universe.get("characters", []) if x.get("id") == c.get("id") or x.get("flow_tag") == c.get("flow_tag")), {})
                dna = u_char.get("dna_block_en", "")
            if dna:
                dna_summary_lines.append(f"- {c_tag}: \"{dna}\"")
        character_dna_summary = "\n".join(dna_summary_lines)
        
        hand_details = state.get("bible", {}).get("hand_details", {})
        
        prompt = f"""You are the Lead Storyboard Director for an Iranian animated poker comedy series.
Follow {skill_filename} to generate the complete storyboard in STRICT JSON format with top-level keys `"hand_timeline"` and `"scenes"`.

---
### RECURRING UNIVERSE & SPATIAL ENVIRONMENT:
- Fixed Poker Room: {u_env.get('flow_tag', '@PokerRoom')}
- Visual Environment: {u_env.get('visual_prompt_en') or u_env.get('description_fa', '')}
- 6-Max Table Seating & Neighbors:
{seating_summary}

---
### CHARACTER VISUAL DNA BLOCKS:
{character_dna_summary}

---
### BIBLE HAND DETAILS (FOR BUILDING HAND TIMELINE):
{json.dumps(hand_details, ensure_ascii=False, indent=2)}

---
### EPISODE SCRIPT SEGMENTS (Total {len(script_segments)} segments):
{json.dumps(script_segments, ensure_ascii=False, indent=2)}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object with top-level keys `"hand_timeline"` and `"scenes"` matching the schema in {skill_filename}:
1. `"hand_timeline"`: Convert Bible hand details into ordered chronological betting/dealing steps in big blinds (BB).
2. `"scenes"`: Array of scene objects. Every scene MUST define:
   - `"scene_id"`, `"beat_index"`, `"segment_ids"`, `"duration_sec"`, `"scene_title_fa"`, `"media_type"`
   - `"scene_spec"`: defines `"shot_type"`, `"focal"` (required except for wide_master, isometric_overview, topdown_pot), `"emotion"`, `"mood"`, `"timeline_step"`, `"extra_action_en"`
   - `"sfx_cue"`: sound effect identifier
   - `"camera_direction"`: required for `"static_image"` (motion_type, camera_prompt_en, zoom_intensity)
   - `"motion_prompt_en"`: required for `"ai_video"` (must include 'mouth closed' for silent acting)
3. Scene 1 (`scene_01`) MUST have shot_type `"wide_master"`.
4. FORBIDDEN keys (assembled deterministically by code; NEVER write them):
   DO NOT write `visual_prompt_en`, `image_prompt_en`, `table_blueprint`, `table_state_en`, `adjacent_players`, `poker_table_state`, `poker_hud_overlay`, `image_references`, `camera_angle`, `focal_character`, or `characters_present`.
"""
        return {
            "episode_id": episode_id,
            "stage": stage,
            "skill_file": skill_filename,
            "stage_desc": "استوری‌بورد و کارگردانی یکپارچه نماها و حرکت",
            "prompt": prompt
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported stage '{stage}' for prompt generation")


class ImportJsonRequest(BaseModel):
    json_content: Union[str, Dict[str, Any], List[Any]]


@app.post("/api/projects/{episode_id}/import-json/{stage}")
def import_ai_studio_json(episode_id: str, stage: str, req: ImportJsonRequest):
    state = load_state(episode_id)
    parsed = clean_and_parse_json(req.json_content)
    stage_key = stage.lower().strip()
    
    stages = state.get("stages", [])
    validation_issues: List[Any] = []
    
    def mark_stage_waiting_approval(num: int, notes: str = ""):
        for s in stages:
            if s.get("stage_number") == num:
                if s.get("status") != "approved":
                    s["status"] = "waiting_approval"
                if notes:
                    s["notes"] = notes

    if stage_key in ["1", "2", "bible", "idea"]:
        state["bible"] = state.get("bible", {})
        if "concept_summary" in parsed:
            state["bible"]["concept_summary"] = parsed["concept_summary"]
            if isinstance(parsed["concept_summary"], dict):
                theme = parsed["concept_summary"].get("theme")
                lesson = parsed["concept_summary"].get("poker_lesson")
                if theme:
                    state["idea"]["theme"] = theme
                if lesson:
                    state["idea"]["core_lesson"] = lesson
                    
        if "hand_details" in parsed:
            state["bible"]["hand_details"] = parsed["hand_details"]
        if "archetypes" in parsed:
            state["bible"]["archetypes"] = parsed["archetypes"]
        if "comedy_beats" in parsed:
            state["bible"]["comedy_beats"] = parsed["comedy_beats"]

        mark_stage_waiting_approval(1, "ایده و دست با موفقیت ذخیره شد")
        mark_stage_waiting_approval(2, "کتابچه استراتژی و جوک‌ها ذخیره شد")

    elif stage_key in ["3", "script"]:
        segments = parsed.get("segments", [])
        if not segments and isinstance(parsed, list):
            segments = parsed
            
        if not segments:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه segments نیست")
            
        state["script"] = state.get("script", {})
        if "script_title" in parsed:
            state["script"]["title"] = parsed["script_title"]
        state["script"]["segments"] = segments
        
        tracks = []
        audio_dir = get_project_path(episode_id) / "audio"
        for s in segments:
            seg_id = s.get("id") or f"seg_{len(tracks)+1:02d}"
            wav_file = audio_dir / f"{seg_id}.wav"
            if wav_file.exists():
                audio_file = f"/media/{episode_id}/audio/{seg_id}.wav"
                track_status = "ready"
            else:
                audio_file = ""
                track_status = "pending_audio"
            tracks.append({
                "segment_id": seg_id,
                "speaker": s.get("speaker") or "NARRATOR",
                "tts_text": s.get("tts_fa", s.get("subtitle_fa", "")),
                "subtitle_text": s.get("subtitle_fa", ""),
                "audio_file": audio_file,
                "status": track_status,
                "duration_sec": float(s.get("estimated_duration_sec", 5.0))
            })
        state["audio"] = state.get("audio", {})
        state["audio"]["tracks"] = tracks

        mark_stage_waiting_approval(3, "سناریوی دو متنی با اعراب TTS ذخیره شد")

    elif stage_key in ["4", "characters"]:
        char_list = parsed.get("characters", [])
        if not char_list and isinstance(parsed, list):
            char_list = parsed
            
        if not char_list:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه characters نیست")

        if isinstance(parsed, dict) and parsed.get("style_bible_en"):
            state.setdefault("bible", {})["visual_style"] = parsed["style_bible_en"]
            
        enriched = []
        for idx, c in enumerate(char_list, 1):
            char_id = c.get("id") or f"char_{idx:02d}"
            c_name_fa = c.get("name_fa", f"کاراکتر {idx}")
            is_anchor = c.get("is_style_anchor", idx == 1)
            clean_name_en = (c.get("flow_tag") or "").replace("@", "").strip() or c.get("name_en", "Character")
            flow_tag = c.get("flow_tag") or f"@{clean_name_en}"
            default_seat = c.get("default_seat", "seat_1")
            assigned_seat = c.get("assigned_seat") or default_seat or "seat_1"
            
            avatar_url = c.get("avatar_url") or c.get("face_sheet_image_path") or ""
            turnaround_sheet = c.get("turnaround_sheet") or c.get("body_sheet_image_path") or c.get("reference_image_path") or ""
            
            face_p = c.get("face_expressions_prompt_en", "")
            body_p = c.get("full_body_prompt_en") or c.get("character_sheet_prompt_en", "")
            persona_p = c.get("persona_behavior_prompt", "")
            
            enriched.append({
                "id": char_id,
                "name_fa": c_name_fa,
                "name_en": c.get("name_en", clean_name_en),
                "role": c.get("role", "Poker Player"),
                "flow_tag": flow_tag,
                "default_seat": default_seat,
                "assigned_seat": assigned_seat,
                "is_style_anchor": is_anchor,
                "status": "waiting_approval",
                "avatar_url": avatar_url,
                "turnaround_sheet": turnaround_sheet,
                "reference_image_path": turnaround_sheet,
                "face_sheet_image_path": c.get("face_sheet_image_path", avatar_url),
                "body_sheet_image_path": c.get("body_sheet_image_path", turnaround_sheet),
                "face_expressions_prompt_en": face_p,
                "full_body_prompt_en": body_p,
                "persona_behavior_prompt": persona_p,
                "voice_description_fa": c.get("voice_description_fa", ""),
                "dna_block_en": c.get("dna_block_en", ""),
                "short_look_en": c.get("short_look_en", ""),
                "acting_beats_en": c.get("acting_beats_en", {}),
                "style_prompt": c.get("character_sheet_prompt_en") or body_p,
                "character_sheet_prompt_en": c.get("character_sheet_prompt_en") or body_p,
                "consistency_tags": c.get("consistency_tags", flow_tag),
                "voice_id": c.get("voice_id", "eleven_persian_narrator"),
                "tagline": c.get("tagline", persona_p)
            })
            
        state["characters"] = enriched
        mark_stage_waiting_approval(4, "مدل شیت و لنگر استایل کاراکترها ذخیره شد")

    elif stage_key in ["6", "scenes"]:
        scene_list = parsed.get("scenes", [])
        if not scene_list and isinstance(parsed, list):
            scene_list = parsed
            
        if not scene_list:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه scenes نیست")
            
        if isinstance(parsed, dict) and "hand_timeline" in parsed:
            state["hand_timeline"] = parsed["hand_timeline"]

        existing_scenes_map = {s.get("id") or s.get("scene_id"): s for s in state.get("scenes", [])}
        enriched_scenes = []
        for idx, sc in enumerate(scene_list, 1):
            norm = normalize_scene(sc, idx - 1, episode_id)
            sc_id = norm["id"]
            old_sc = existing_scenes_map.get(sc_id, {})
            
            # Preserve existing uploaded video_path/image_path from existing_scenes_map
            if old_sc.get("video_path"):
                norm["video_path"] = old_sc["video_path"]
            if old_sc.get("video_asset"):
                norm["video_asset"] = old_sc["video_asset"]
            if old_sc.get("image_path"):
                norm["image_path"] = old_sc["image_path"]
                norm["visual_asset"] = old_sc.get("visual_asset", old_sc["image_path"])

            # Map title and scene_title_fa
            if not norm.get("title") and norm.get("scene_title_fa"):
                norm["title"] = norm["scene_title_fa"]
            elif not norm.get("title"):
                norm["title"] = f"صحنه #{idx}"
            norm.setdefault("scene_title_fa", norm["title"])

            norm["status"] = "ready_for_review"
            enriched_scenes.append(norm)

        state["scenes"] = enriched_scenes
        mark_stage_waiting_approval(6, "بیت‌های بصری استوری‌بورد و حرکت ذخیره شد")
        snap_path = snapshot_state(episode_id, "state.json.pre_import.bak")
        save_state(episode_id, state)

        try:
            has_specs = any(isinstance(sc.get("scene_spec"), dict) for sc in enriched_scenes)
            if has_specs:
                build_res = build_episode_prompts(episode_id, write=True)
                if build_res.get("errors"):
                    raise HTTPException(status_code=422, detail="\n".join(build_res["errors"][:10]))
                state = load_state(episode_id)

            scene_errors = validate_scenes(state.get("scenes", []))
            hard_errors = [e for e in scene_errors if "must match scene_NN" in e or "duplicate scene_id" in e or "non-empty list" in e]
            if hard_errors:
                raise HTTPException(status_code=422, detail="\n".join(hard_errors))
            validation_issues = [{"scene_id": "", "field": "scenes", "severity": "warning", "message": e} for e in scene_errors]
        except Exception:
            restore_state_from(episode_id, snap_path)
            try:
                if snap_path.exists():
                    snap_path.unlink()
            except OSError:
                pass
            raise

        try:
            if snap_path.exists():
                snap_path.unlink()
        except OSError:
            pass

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported stage '{stage}' for JSON import")

    if stage_key not in ["6", "scenes"]:
        save_state(episode_id, state)
    if stage_key in ["3", "script"]:
        validation_issues = validate_segments(state.get("script", {}).get("segments", []))

    return {
        "status": "success",
        "message": f"داده‌های مرحله {stage} با موفقیت ذخیره شد",
        "current_stage": state.get("current_stage"),
        "state": state,
        "validation_issues": validation_issues
    }


class UpdateSceneDetailsRequest(BaseModel):
    shot_mode: Optional[str] = None
    media_type: Optional[str] = None
    camera_effect: Optional[str] = None
    camera_direction: Optional[Dict[str, Any]] = None
    motion_prompt_en: Optional[str] = None
    duration_sec: Optional[float] = None
    title: Optional[str] = None
    table_state_en: Optional[str] = None
    adjacent_players: Optional[List[str]] = None
    visual_prompt_en: Optional[str] = None
    scene_spec: Optional[Dict[str, Any]] = None


@app.post("/api/projects/{episode_id}/scenes/{scene_id}/update")
def update_scene_details(episode_id: str, scene_id: str, req: UpdateSceneDetailsRequest):
    validate_scene_id(scene_id)
    state = load_state(episode_id)
    scenes = state.get("scenes", [])
    found_scene = None
    for sc in scenes:
        if sc.get("id") == scene_id or sc.get("scene_id") == scene_id:
            found_scene = sc
            break
            
    if not found_scene:
        raise HTTPException(status_code=404, detail=f"Scene '{scene_id}' not found")
        
    if req.media_type is not None:
        found_scene["media_type"] = req.media_type
        found_scene["shot_mode"] = "ai_video" if req.media_type == "ai_video" else "static_zoom"
    if req.shot_mode is not None:
        found_scene["shot_mode"] = req.shot_mode
        found_scene["media_type"] = "ai_video" if req.shot_mode == "ai_video" else "static_image"
    if req.camera_direction is not None:
        found_scene["camera_direction"] = req.camera_direction
    if req.camera_effect is not None:
        found_scene["camera_effect"] = req.camera_effect
    if req.motion_prompt_en is not None:
        found_scene["motion_prompt_en"] = req.motion_prompt_en
    if req.duration_sec is not None:
        found_scene["duration_sec"] = req.duration_sec
    if req.title is not None:
        found_scene["title"] = req.title
    if req.table_state_en is not None:
        found_scene["table_state_en"] = req.table_state_en
    if req.adjacent_players is not None:
        found_scene["adjacent_players"] = req.adjacent_players
    if req.visual_prompt_en is not None:
        found_scene["visual_prompt_en"] = req.visual_prompt_en
        found_scene["visual_prompt"] = req.visual_prompt_en
    if req.scene_spec is not None:
        found_scene["scene_spec"] = req.scene_spec
        
    save_state(episode_id, state)
    return {"status": "success", "scene": found_scene}


@app.get("/api/skills")
def list_skills():
    skills = []
    if SKILLS_DIR.exists():
        for file in sorted(SKILLS_DIR.iterdir()):
            if file.is_file() and file.suffix == ".md":
                skills.append({
                    "filename": file.name,
                    "title": file.stem.replace("-", " ").title(),
                    "size_bytes": file.stat().st_size
                })
    return {"skills": skills}


@app.get("/api/skills/{skill_name}")
def get_skill_content(skill_name: str):
    if "/" in skill_name or "\\" in skill_name or ".." in skill_name:
        raise HTTPException(status_code=400, detail="Invalid skill name")
    if not skill_name.endswith(".md"):
        skill_name = f"{skill_name}.md"
    skill_path = (SKILLS_DIR / skill_name).resolve()
    if skill_path.parent != SKILLS_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid skill path")
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill file not found")
    with open(skill_path, "r", encoding="utf-8") as f:
        return {"filename": skill_name, "content": f.read()}


class SubtitleGenerateRequest(BaseModel):
    include_tts: bool = False


@app.post("/api/projects/{episode_id}/generate_subtitles")
def generate_subtitles(episode_id: str, req: SubtitleGenerateRequest = SubtitleGenerateRequest()):
    state = load_state(episode_id)
    segments = state.get("script", {}).get("segments", [])
    
    srt_lines = []
    current_time_sec = 0.0
    
    for idx, seg in enumerate(segments, 1):
        duration = float(seg.get("estimated_duration_sec") or seg.get("duration_est_sec") or 4.0)
        start_time = current_time_sec
        end_time = start_time + duration
        current_time_sec = end_time
        
        def fmt_time(s: float) -> str:
            hours = int(s // 3600)
            minutes = int((s % 3600) // 60)
            seconds = int(s % 60)
            millis = int((s - int(s)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
            
        text = seg.get("tts_fa") if req.include_tts else seg.get("subtitle_fa")
        speaker = seg.get("speaker", "Narration")
        if speaker not in ["Narration", "NARRATOR"]:
            text = f"[{speaker}]: {text}"
            
        srt_lines.append(f"{idx}\n{fmt_time(start_time)} --> {fmt_time(end_time)}\n{text}\n")
        
    srt_content = "\n".join(srt_lines)
    
    exports_dir = get_project_path(episode_id) / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    srt_file = exports_dir / "persian_subtitles.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    return {
        "status": "success",
        "file": str(srt_file),
        "srt_content": srt_content,
        "segment_count": len(segments)
    }


@app.post("/api/projects/{episode_id}/render_ffmpeg_preview")
def get_ffmpeg_render_command(episode_id: str):
    state = load_state(episode_id)
    edit_config = state.get("edit", {})
    sub_settings = edit_config.get("subtitle_settings", {})
    
    font_name = sub_settings.get("font", "Vazirmatn")
    font_size = sub_settings.get("font_size", 42)
    primary_color = sub_settings.get("primary_color", "&H00FFFFFF")
    outline_color = sub_settings.get("outline_color", "&H00000000")
    outline_width = sub_settings.get("outline_width", 3)
    margin_v = sub_settings.get("margin_v", 110)
    
    srt_path = f"projects/{episode_id}/exports/persian_subtitles.srt"
    output_path = f"projects/{episode_id}/exports/{episode_id}_final_preview.mp4"
    input_video = f"projects/{episode_id}/exports/raw_sequence.mp4"
    
    cmd = (
        f'ffmpeg -y -i "{input_video}" '
        f'-vf "subtitles=\'{srt_path}\':force_style=\'FontName={font_name},FontSize={font_size},'
        f'PrimaryColour={primary_color},OutlineColour={outline_color},Outline={outline_width},'
        f'Alignment=2,MarginV={margin_v}\'" '
        f'-c:v libx264 -preset fast -crf 20 -c:a aac -b:a 192k "{output_path}"'
    )
    
    scene_clip_commands = []
    for sc in state.get("scenes", []):
        if sc.get("media_type", "static_image") == "static_image":
            sid = sc.get("scene_id") or sc.get("id") or "scene_01"
            img_in = f"projects/{episode_id}/assets/images/{sid}.png"
            clip_out = f"projects/{episode_id}/exports/clips/{sid}.mp4"
            cmd_list = build_scene_clip_command(
                img_in,
                clip_out,
                sc.get("camera_direction"),
                sc.get("duration_sec", 2.0),
            )
            scene_clip_commands.append({
                "scene_id": sid,
                "command": shlex.join(cmd_list)
            })

    return {
        "status": "ready",
        "ffmpeg_command": cmd,
        "font": font_name,
        "rtl_shaping_engine": "libass with HarfBuzz enabled",
        "output_expected": output_path,
        "scene_clip_commands": scene_clip_commands
    }


@app.post("/api/episodes/{episode_id}/build-image-prompts")
@app.post("/api/projects/{episode_id}/build-image-prompts")
def build_image_prompts(episode_id: str, scene_id: Optional[str] = None):
    result = build_episode_prompts(episode_id, scene_id=scene_id, write=True)
    if result["errors"]:
        raise HTTPException(status_code=422, detail="\n".join(result["errors"][:10]))
    return {"status": "success", "built": result["built"], "warnings": result["warnings"]}


# ---------------------------------------------------------
# Antigravity CLI Execution Endpoints
# ---------------------------------------------------------

@app.post("/api/episodes/{episode_id}/generate-storyboard")
@app.post("/api/projects/{episode_id}/generate-storyboard")
async def api_generate_storyboard(episode_id: str):
    get_project_path(episode_id)
    task = await start_storyboard_generation(episode_id)
    return task.to_dict()


@app.post("/api/episodes/{episode_id}/generate-images")
@app.post("/api/projects/{episode_id}/generate-images")
async def api_generate_images(episode_id: str):
    get_project_path(episode_id)
    task = await start_images_generation(episode_id)
    return task.to_dict()


@app.post("/api/episodes/{episode_id}/scenes/{scene_id}/regenerate-image")
@app.post("/api/projects/{episode_id}/scenes/{scene_id}/regenerate-image")
async def api_regenerate_scene_image(episode_id: str, scene_id: str):
    validate_scene_id(scene_id)
    get_project_path(episode_id)
    task = await start_scene_regeneration(episode_id, scene_id)
    return task.to_dict()


@app.get("/api/episodes/{episode_id}/task-status")
@app.get("/api/projects/{episode_id}/task-status")
def api_get_task_status(episode_id: str):
    get_project_path(episode_id)
    task = get_task_for_episode(episode_id)
    return task.to_dict()


@app.post("/api/episodes/{episode_id}/cancel-task")
@app.post("/api/projects/{episode_id}/cancel-task")
async def cancel_episode_task(episode_id: str):
    import backend.antigravity_cli as cli
    return cli.cancel_task(episode_id).to_dict()


# Mount frontend dist static files at the end
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
