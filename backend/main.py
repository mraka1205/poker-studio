import os
import json
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.antigravity_cli import (
    get_task_for_episode,
    start_storyboard_generation,
    start_images_generation,
    start_scene_regeneration,
)

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
SKILLS_DIR = BASE_DIR / ".agent" / "skills"

app = FastAPI(title="Poker Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure core directories exist
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# Mount media directory for images, audio, exports
app.mount("/media", StaticFiles(directory=str(PROJECTS_DIR)), name="media")


def get_project_path(episode_id: str) -> Path:
    proj_path = PROJECTS_DIR / episode_id
    if not proj_path.exists() or not proj_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found")
    return proj_path


def load_state(episode_id: str) -> Dict[str, Any]:
    proj_dir = get_project_path(episode_id)
    state_file = proj_dir / "state.json"
    if not state_file.exists():
        raise HTTPException(status_code=404, detail="state.json not found in episode folder")
    with open(state_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Automatically resolve scene image paths if files exist on disk
    assets_img_dir = proj_dir / "assets" / "images"
    scenes_dir = proj_dir / "scenes"

    scenes = data.get("scenes", [])
    updated = False
    for scene in scenes:
        s_id = scene.get("id") or scene.get("scene_id")
        if not s_id:
            continue
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

        if found_path and (scene.get("image_path") != found_path or scene.get("visual_asset") != found_path):
            scene["image_path"] = found_path
            scene["visual_asset"] = found_path
            updated = True

    if updated:
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    return data


def save_state(episode_id: str, data: Dict[str, Any]):
    state_file = get_project_path(episode_id) / "state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# CHANNEL UNIVERSE (Fixed Poker Room & Global Cast)
# ==========================================

UNIVERSE_FILE = PROJECTS_DIR / "universe.json"
UNIVERSE_MEDIA_DIR = PROJECTS_DIR / "universe"
UNIVERSE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def load_universe() -> Dict[str, Any]:
    if not UNIVERSE_FILE.exists():
        default_universe = {
            "version": "1.0.0",
            "environment": {
                "id": "env_poker_room",
                "flow_tag": "@PokerRoom",
                "name": "میز زیرزمینی پوکر (The Underground Poker Room)",
                "description_fa": "اتاق اختصاصی پوکر زیرزمینی در تهران. میز بیضی ۶ نفره با نمد سبز تیره، صندلی‌های چرمی قهوه‌ای، دیوار آجری تیره با قفسه کتاب چوبی و تابلوهای هنری مدرن.",
                "visual_prompt_en": "Handcrafted needle-felted stop-motion animation style, miniature underground poker room, 6-max oval poker table with rich emerald green wool felt, dark mahogany wood trim, plush brown leather armrests. In background, dark needle-felted exposed brick walls with warm LED-lit wooden bookshelves holding antique trophies and old books, dark velvet curtains. Warm focused overhead brass chandelier casting soft glow on felt, subtle volumetric dust motes, rich tactile textures, vertical 9:16 composition --ar 9:16",
                "reference_image_path": ""
            },
            "camera_angles": {},
            "characters": []
        }
        with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
            json.dump(default_universe, f, ensure_ascii=False, indent=2)
        return default_universe

    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_universe(data: Dict[str, Any]):
    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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

    safe_filename = file.filename.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    if asset_type == "environment":
        dest_filename = f"environment_{safe_filename}"
    elif asset_type == "angle" and angle_id:
        dest_filename = f"angle_{angle_id}_{safe_filename}"
    elif asset_type == "character" and character_id:
        st = f"_{sheet_type}" if sheet_type else ""
        dest_filename = f"char_{character_id}{st}_{safe_filename}"
    else:
        dest_filename = f"{asset_type}_{timestamp}_{safe_filename}"

    file_path = UNIVERSE_MEDIA_DIR / dest_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_url = f"/media/universe/{dest_filename}"

    universe = load_universe()
    if asset_type == "environment":
        universe["environment"]["reference_image_path"] = relative_url
        save_universe(universe)
    elif asset_type == "angle" and angle_id:
        if "camera_angles" not in universe:
            universe["camera_angles"] = {}
        if angle_id in universe["camera_angles"]:
            universe["camera_angles"][angle_id]["reference_image_path"] = relative_url
            save_universe(universe)
    elif asset_type == "character" and character_id:
        for c in universe.get("characters", []):
            if c.get("id") == character_id:
                if sheet_type == "face":
                    c["face_sheet_image_path"] = relative_url
                    if not c.get("reference_image_path"):
                        c["reference_image_path"] = relative_url
                elif sheet_type == "body":
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
            
            ref_img = u_c.get("body_sheet_image_path") or u_c.get("reference_image_path") or u_c.get("face_sheet_image_path") or f"/media/{episode_id}/characters/kambiz.svg"
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
    for item in PROJECTS_DIR.iterdir():
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
    return load_state(episode_id)


@app.put("/api/projects/{episode_id}")
def update_project_state(episode_id: str, new_state: Dict[str, Any]):
    save_state(episode_id, new_state)
    return {"status": "success", "message": "State updated successfully"}


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
                s["approved_at"] = datetime.utcnow().isoformat() + "Z"
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


class SetCurrentStageRequest(BaseModel):
    current_stage: int


@app.post("/api/projects/{episode_id}/set_stage")
def set_current_stage(episode_id: str, req: SetCurrentStageRequest):
    state = load_state(episode_id)
    state["current_stage"] = req.current_stage
    save_state(episode_id, state)
    return {"status": "success", "current_stage": req.current_stage}


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
        existing = [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]
        ep_count = len([d for d in existing if d.startswith("ep")]) + 1
        ascii_slug = re.sub(r'[^a-zA-Z0-9]+', '-', req.english_title or "").strip('-').lower()
        if not ascii_slug:
            ascii_slug = "poker-hand"
        folder_name = f"ep{ep_count:02d}-{ascii_slug}"
    else:
        folder_name = req.episode_id.strip().lower().replace(" ", "-")
        folder_name = re.sub(r'[^a-z0-9_-]', '', folder_name)
        if not folder_name:
            folder_name = f"ep-{datetime.now().strftime('%m%d%H%M')}"

    proj_dir = PROJECTS_DIR / folder_name
    if proj_dir.exists():
        folder_name = f"{folder_name}-{datetime.now().strftime('%H%M%S')}"
        proj_dir = PROJECTS_DIR / folder_name
        
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
    
    with open(proj_dir / "state.json", "w", encoding="utf-8") as f:
        json.dump(new_state, f, ensure_ascii=False, indent=2)
        
    return {"status": "success", "episode_id": folder_name}


# ==========================================
# ASSET UPLOADS (Characters, Scenes, Audio)
# ==========================================

@app.post("/api/projects/{episode_id}/upload/{asset_type}")
@app.post("/api/projects/{episode_id}/upload")
async def upload_asset(
    episode_id: str,
    asset_type: Optional[str] = None,
    target_type: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    chosen_type = asset_type or target_type
    if not chosen_type or chosen_type not in ["characters", "scenes", "audio", "exports", "assets/images"]:
        raise HTTPException(status_code=400, detail="Invalid target/asset type.")
        
    project_path = get_project_path(episode_id)
    target_dir = project_path / chosen_type
    target_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = file.filename.replace(" ", "_")
    file_path = target_dir / safe_filename
    
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


def compute_seated_neighbors_context(characters: List[Dict[str, Any]], camera_angles_map: Dict[str, Any]):
    seat_order = ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6"]
    seat_to_char = {}
    for c in characters:
        s_id = c.get("assigned_seat") or c.get("default_seat")
        if s_id in seat_order:
            seat_to_char[s_id] = c

    neighbors_map = {}
    lines = []
    for idx, s_id in enumerate(seat_order):
        c = seat_to_char.get(s_id)
        left_seat = seat_order[(idx - 1) % 6]
        right_seat = seat_order[(idx + 1) % 6]
        
        left_char = seat_to_char.get(left_seat)
        right_char = seat_to_char.get(right_seat)
        
        left_desc = f"{left_char.get('name_en', left_char.get('id'))} ({left_char.get('flow_tag', '')})" if left_char else "Empty Chair"
        right_desc = f"{right_char.get('name_en', right_char.get('id'))} ({right_char.get('flow_tag', '')})" if right_char else "Empty Chair"
        
        ang = camera_angles_map.get(s_id, {})
        ang_tag = ang.get("flow_tag", f"@{s_id.title()}")
        landmarks = ang.get("background_landmarks_en", "distinct room background")
        
        neighbors_map[s_id] = {
            "current_seat": s_id,
            "occupant": c.get("name_en") if c else None,
            "occupant_tag": c.get("flow_tag") if c else None,
            "left_seat": left_seat,
            "left_player": left_char.get("name_en") if left_char else None,
            "left_tag": left_char.get("flow_tag") if left_char else None,
            "right_seat": right_seat,
            "right_player": right_char.get("name_en") if right_char else None,
            "right_tag": right_char.get("flow_tag") if right_char else None,
            "landmarks": landmarks,
        }
        
        if c:
            c_tag = c.get("flow_tag", "")
            lines.append(
                f"- Seat {s_id} ({ang_tag}): {c.get('name_en', c.get('id'))} ({c_tag}) | "
                f"Left neighbor: {left_desc} ({left_seat}) | "
                f"Right neighbor: {right_desc} ({right_seat}) | "
                f"Background behind: {landmarks}"
            )
        else:
            lines.append(f"- Seat {s_id} ({ang_tag}): [Empty Chair] | Left: {left_desc} | Right: {right_desc} | Background behind: {landmarks}")
            
    summary_text = "\n".join(lines)
    return neighbors_map, summary_text


@app.post("/api/projects/{episode_id}/build-prompt/{stage}")
def build_ai_studio_prompt(episode_id: str, stage: str):
    state = load_state(episode_id)
    stage_key = stage.lower().strip()
    universe = load_universe()
    u_env = universe.get("environment", {})
    u_chars = universe.get("characters", [])
    u_chars_summary = "\n".join([
        f"  - {c.get('flow_tag', '')} ({c.get('name_fa', '')} - {c.get('archetype', '')}):\n    Behavioral & Physical Profile: {c.get('persona_behavior_prompt') or c.get('personality_and_catchphrases_fa', '')}"
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
- Fixed Poker Room: {u_env.get('flow_tag', '@PokerRoom')} - {u_env.get('name', 'میز زیرزمینی پوکر')}
  Description: {u_env.get('description_fa', '')}
- Recurring Characters Roster:
{u_chars_summary}
NOTE: By default, use the channel's recurring stars (@Arash and @Bijan) for the core hand archetypes (Hero / Villain) to maintain story continuity across episodes.

---
### EPISODE CONTEXT:
- Episode ID: {state.get('episode_id')}
- Title (FA): {state.get('title')}
- English Title: {state.get('english_title', 'Persian Poker Comedy')}
- Raw Poker Hand / Idea Description (ایده خام و شرح دست پوکر):
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
        camera_angles_map = universe.get("camera_angles", {})
        
        neighbors_map, seating_summary = compute_seated_neighbors_context(ep_characters, camera_angles_map)
        
        prompt = f"""You are the Lead Storyboard, Motion & Continuity Director for an Iranian animated poker comedy series.
Follow {skill_filename} to generate the complete, exhaustive storyboard array (`scenes`) in STRICT JSON format.

---
### RECURRING UNIVERSE & SPATIAL ENVIRONMENT:
- Fixed Poker Room: {u_env.get('flow_tag', '@PokerRoom')}
- Description: {u_env.get('description_fa', '')}
- 6-Max Table Seating & Neighbors:
{seating_summary}

---
### EPISODE SCRIPT SEGMENTS (Total {len(script_segments)} segments):
{json.dumps(script_segments, ensure_ascii=False, indent=2)}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Return ONLY a valid JSON object with key `"scenes"` containing cinema-grade, richly detailed visual prompts (80-120 words minimum), motion prompts for ai_video shots, automated camera_direction objects for static_image shots, persistent table states, seated neighbors, and Scene 1 master continuity locks.
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
    
    def approve_stage_num(num: int, notes: str = ""):
        for s in stages:
            if s.get("stage_number") == num:
                s["status"] = "approved"
                s["approved_at"] = datetime.utcnow().isoformat() + "Z"
                if notes:
                    s["notes"] = notes
        if state.get("current_stage") == num and num < 9:
            state["current_stage"] = num + 1

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

        approve_stage_num(1, "ایده و دست با موفقیت ذخیره شد")
        approve_stage_num(2, "کتابچه استراتژی و جوک‌ها ذخیره شد")

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
        for s in segments:
            seg_id = s.get("id") or f"seg_{len(tracks)+1:02d}"
            tracks.append({
                "segment_id": seg_id,
                "speaker": s.get("speaker", "Narration"),
                "tts_text": s.get("tts_fa", s.get("subtitle_fa", "")),
                "subtitle_text": s.get("subtitle_fa", ""),
                "audio_file": f"/media/{episode_id}/audio/{seg_id}.wav",
                "status": "ready",
                "duration_sec": float(s.get("estimated_duration_sec", 5.0))
            })
        state["audio"] = state.get("audio", {})
        state["audio"]["tracks"] = tracks

        approve_stage_num(3, "سناریوی دو متنی با اعراب TTS ذخیره شد")

    elif stage_key in ["4", "characters"]:
        char_list = parsed.get("characters", [])
        if not char_list and isinstance(parsed, list):
            char_list = parsed
            
        if not char_list:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه characters نیست")
            
        enriched = []
        for idx, c in enumerate(char_list, 1):
            char_id = c.get("id") or f"char_{idx:02d}"
            c_name_fa = c.get("name_fa", f"کاراکتر {idx}")
            is_anchor = c.get("is_style_anchor", idx == 1)
            
            avatar_url = c.get("avatar_url") or f"/media/{episode_id}/characters/kambiz.svg"
            turnaround_sheet = c.get("turnaround_sheet") or f"/media/{episode_id}/characters/kambiz_sheet.svg"
            
            enriched.append({
                "id": char_id,
                "name_fa": c_name_fa,
                "name_en": c.get("name_en", "Character"),
                "role": c.get("role", "Poker Player"),
                "is_style_anchor": is_anchor,
                "status": "approved",
                "avatar_url": avatar_url,
                "turnaround_sheet": turnaround_sheet,
                "style_prompt": c.get("character_sheet_prompt_en", c.get("style_prompt", "")),
                "character_sheet_prompt_en": c.get("character_sheet_prompt_en", ""),
                "consistency_tags": c.get("consistency_tags", ""),
                "voice_id": c.get("voice_id", "eleven_persian_narrator"),
                "tagline": c.get("tagline", "")
            })
            
        state["characters"] = enriched
        approve_stage_num(4, "مدل شیت و لنگر استایل کاراکترها تایید شد")

    elif stage_key in ["6", "scenes"]:
        scene_list = parsed.get("scenes", [])
        if not scene_list and isinstance(parsed, list):
            scene_list = parsed
            
        if not scene_list:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه scenes نیست")
            
        existing_scenes_map = {s.get("id"): s for s in state.get("scenes", [])}
        enriched_scenes = []
        for idx, sc in enumerate(scene_list, 1):
            sc_id = sc.get("scene_id") or sc.get("id") or f"scene_{idx:02d}"
            old_sc = existing_scenes_map.get(sc_id, {})
            
            hud = sc.get("poker_hud_overlay", {})
            if isinstance(hud, str):
                hud = {"action_badge": hud}
                
            motion_p = sc.get("motion_prompt_en") or old_sc.get("motion_prompt_en", "")
            media_type = sc.get("media_type") or ("ai_video" if motion_p.strip() or sc.get("shot_mode") == "ai_video" else "static_image")
            mode = "ai_video" if media_type == "ai_video" else "static_zoom"
            effect = sc.get("camera_effect") or old_sc.get("camera_effect", "zoom_in")
            dur = float(sc.get("duration_sec") or old_sc.get("duration_sec") or 2.0)
            table_state_text = sc.get("table_state_en") or old_sc.get("table_state_en", "")
            adjacent = sc.get("adjacent_players") or old_sc.get("adjacent_players", [])

            # Automated FFmpeg Camera Direction for static_image
            cam_direction = sc.get("camera_direction") or old_sc.get("camera_direction")
            if not cam_direction and media_type == "static_image":
                cam_direction = {
                    "motion_type": "slow_zoom_in",
                    "start_focus_region": f"chest-up framing on {(sc.get('characters_present') or ['Hero'])[0]}",
                    "end_focus_region": f"tight macro push towards {(sc.get('characters_present') or ['Hero'])[0]} and table felt",
                    "zoom_intensity": 1.15,
                    "easing": "smooth",
                    "camera_prompt_en": "Cinematic slow zoom in focusing on the character's reaction and the table chips"
                }

            # Determine best image asset URL
            img_asset = old_sc.get("visual_asset") or old_sc.get("image_path") or sc.get("visual_asset") or sc.get("image_path") or f"/media/{episode_id}/assets/images/{sc_id}.png"

            enriched_scenes.append({
                "id": sc_id,
                "beat_index": idx,
                "time_range": f"00:{(idx-1)*2:02d} - 00:{idx*2:02d}",
                "title": sc.get("scene_title_fa", f"صحنه #{idx}"),
                "duration_sec": dur,
                "segment_ids": sc.get("segment_ids", []),
                "characters_present": sc.get("characters_present", []),
                "adjacent_players": adjacent,
                "table_state_en": table_state_text,
                "camera": sc.get("camera_angle", "Medium Shot"),
                "media_type": media_type,
                "shot_mode": mode,
                "camera_effect": effect,
                "camera_direction": cam_direction,
                "visual_prompt": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "visual_prompt_en": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "motion_prompt_en": motion_p,
                "target_video_sec": float(sc.get("target_video_sec") or dur or 2.0),
                "poker_table_state": hud,
                "sfx_cue": sc.get("sfx_cue", "chip_splash"),
                "visual_asset": img_asset,
                "image_path": img_asset,
                "video_path": old_sc.get("video_path") or sc.get("video_path"),
                "video_asset": old_sc.get("video_asset") or sc.get("video_asset"),
                "status": "approved"
            })
            
        state["scenes"] = enriched_scenes
        approve_stage_num(6, "بیت‌های بصری استوری‌بورد و حرکت ذخیره شد")

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported stage '{stage}' for JSON import")

    save_state(episode_id, state)
    return {
        "status": "success",
        "message": f"داده‌های مرحله {stage} با موفقیت ذخیره شد",
        "current_stage": state.get("current_stage"),
        "state": state
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


@app.post("/api/projects/{episode_id}/scenes/{scene_id}/update")
def update_scene_details(episode_id: str, scene_id: str, req: UpdateSceneDetailsRequest):
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
        
    save_state(episode_id, state)
    return {"status": "success", "scene": found_scene}


@app.post("/api/projects/{episode_id}/upload/scene_video")
async def upload_scene_video(
    episode_id: str,
    scene_id: str = Form(...),
    file: UploadFile = File(...)
):
    project_path = get_project_path(episode_id)
    target_dir = project_path / "scenes"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = f"{scene_id}_motion_{file.filename.replace(' ', '_')}"
    file_path = target_dir / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    video_url = f"/media/{episode_id}/scenes/{safe_filename}"
    
    state = load_state(episode_id)
    for sc in state.get("scenes", []):
        if sc.get("id") == scene_id or sc.get("scene_id") == scene_id:
            sc["video_path"] = video_url
            sc["video_asset"] = video_url
            sc["shot_mode"] = "ai_video"
            break
            
    save_state(episode_id, state)
    return {
        "status": "success",
        "scene_id": scene_id,
        "video_url": video_url,
        "absolute_path": str(file_path)
    }


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
    if not skill_name.endswith(".md"):
        skill_name = f"{skill_name}.md"
    skill_path = SKILLS_DIR / skill_name
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
    
    return {
        "status": "ready",
        "ffmpeg_command": cmd,
        "font": font_name,
        "rtl_shaping_engine": "libass with HarfBuzz enabled",
        "output_expected": output_path
    }


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
    get_project_path(episode_id)
    task = await start_scene_regeneration(episode_id, scene_id)
    return task.to_dict()


@app.get("/api/episodes/{episode_id}/task-status")
@app.get("/api/projects/{episode_id}/task-status")
def api_get_task_status(episode_id: str):
    get_project_path(episode_id)
    task = get_task_for_episode(episode_id)
    try:
        load_state(episode_id)
    except Exception:
        pass
    return task.to_dict()


# Mount frontend dist static files at the end
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
