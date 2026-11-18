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
import httpx
from dotenv import dotenv_values, set_key
from backend.services.gemini_client import list_gemini_models, call_gemini_generate_content

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
SKILLS_DIR = BASE_DIR / ".agent" / "skills"
ENV_FILE = BASE_DIR / ".env"

app = FastAPI(title="Poker Studio API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# Mount media directory for images, audio, exports
app.mount("/media", StaticFiles(directory=str(PROJECTS_DIR)), name="media")


def get_env_config() -> Dict[str, str]:
    if not ENV_FILE.exists():
        ENV_FILE.touch()
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("OPENROUTER_API_KEY=\nOPENROUTER_MODEL=google/gemini-2.5-flash\n")
    return dotenv_values(ENV_FILE)


def set_env_config(key: str, val: str):
    if not ENV_FILE.exists():
        ENV_FILE.touch()
    set_key(str(ENV_FILE), key, val)


def get_project_path(episode_id: str) -> Path:
    proj_path = PROJECTS_DIR / episode_id
    if not proj_path.exists() or not proj_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found")
    return proj_path


def load_state(episode_id: str) -> Dict[str, Any]:
    state_file = get_project_path(episode_id) / "state.json"
    if not state_file.exists():
        raise HTTPException(status_code=404, detail="state.json not found in episode folder")
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


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
                "flow_tag": "@PokerRoom",
                "name": "میز همیشگی کلوپ زیرزمینی پوکر",
                "description_fa": "اتاق اختصاصی و دنج زیرزمینی پوکر در تهران با نورپردازی متمرکز نئونی ملایم، میز بیضی شکل با نمد سبز یشمی مخملی، چیپ‌های سرامیکی کلاسیک، لیوان‌های کمرباریک چای قندپهلو، زیرسیگاری کریستال قدیمی و تابلوهای طنز پوکر روی دیوارهای آجری دکوراتیو.",
                "visual_prompt_en": "Establishing shot of the underground Persian poker club room (@PokerRoom). A classic oval poker table in the center covered in premium emerald-green velvet felt with wooden chip rails and designated betting lines. Empty padded dark leather chairs around the table. Scattered neat stacks of ceramic chips resting flat on the felt, and a traditional Persian glass of hot black tea on a coaster. Warm directional pendant lamp overhead illuminating the table, moody dark brick walls with subtle neon blue and amber accent rim lighting. Modern stylized 2D cartoon adult animation aesthetic, Rick and Morty meets Archer comic style, crisp bold dark vector outlines, rich saturated colors, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16 --v 6.1",
                "reference_image_path": "",
                "style_note_en": "Bold 2D adult cartoon animation style, Rick and Morty meets Archer aesthetic, thick clean vector outlines, vibrant dramatic rim lighting, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16"
            },
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
    """Strips Markdown fences and parses JSON strictly."""
    if isinstance(raw_input, dict):
        return raw_input
    if not isinstance(raw_input, str):
        raise HTTPException(status_code=400, detail="JSON input must be string or object")
        
    cleaned = raw_input.strip()
    # Strip ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()
        
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"فرمت JSON ارسالی نامعتبر است: {str(e)}"
        )


@app.get("/api/health")
def health_check():
    return {
        "status": "ok", 
        "app": "Poker Studio Backend", 
        "version": "1.1.0",
        "time": datetime.now().isoformat()
    }


# ==========================================
# SETTINGS ENDPOINTS (Gemini & OpenRouter)
# ==========================================

class SettingsRequest(BaseModel):
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None


@app.get("/api/settings")
def get_settings():
    env = get_env_config()
    openrouter_key = env.get("OPENROUTER_API_KEY", "") or ""
    gemini_key = env.get("GEMINI_API_KEY", "") or ""
    
    masked_openrouter = (openrouter_key[:8] + "..." + openrouter_key[-4:]) if len(openrouter_key) > 12 else ("****" if openrouter_key else "")
    masked_gemini = (gemini_key[:8] + "..." + gemini_key[-4:]) if len(gemini_key) > 12 else ("****" if gemini_key else "")
    
    return {
        "has_key": bool(openrouter_key.strip()),
        "has_openrouter_key": bool(openrouter_key.strip()),
        "openrouter_api_key_masked": masked_openrouter,
        "openrouter_model": env.get("OPENROUTER_MODEL", "google/gemini-2.5-flash"),
        "has_gemini_key": bool(gemini_key.strip()),
        "gemini_api_key_masked": masked_gemini,
        "gemini_model": env.get("GEMINI_MODEL", "gemini-2.5-flash")
    }


@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    if req.openrouter_api_key is not None and req.openrouter_api_key.strip():
        val = req.openrouter_api_key.strip()
        set_env_config("OPENROUTER_API_KEY", val)
        os.environ["OPENROUTER_API_KEY"] = val
    if req.openrouter_model is not None and req.openrouter_model.strip():
        val = req.openrouter_model.strip()
        set_env_config("OPENROUTER_MODEL", val)
        os.environ["OPENROUTER_MODEL"] = val
    if req.gemini_api_key is not None and req.gemini_api_key.strip():
        val = req.gemini_api_key.strip()
        set_env_config("GEMINI_API_KEY", val)
        os.environ["GEMINI_API_KEY"] = val
    if req.gemini_model is not None and req.gemini_model.strip():
        val = req.gemini_model.strip()
        set_env_config("GEMINI_MODEL", val)
        os.environ["GEMINI_MODEL"] = val
    return {
        "status": "success", 
        "message": "تنظیمات با موفقیت در .env ذخیره شد",
        "settings": get_settings()
    }


@app.get("/api/gemini/models")
async def get_gemini_models_endpoint(key: Optional[str] = None):
    env = get_env_config()
    api_key = key or env.get("GEMINI_API_KEY", "")
    models = await list_gemini_models(api_key)
    return {"models": models}


@app.get("/api/openrouter/models")
async def get_openrouter_models_endpoint(key: Optional[str] = None):
    env = get_env_config()
    api_key = key or env.get("OPENROUTER_API_KEY", "")
    headers = {
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Poker Animation Studio"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get("https://openrouter.ai/api/v1/models", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"خطای سرور OpenRouter: {resp.text}")
            data = resp.json()
            models = []
            for m in data.get("data", []):
                models.append({
                    "id": m.get("id"),
                    "name": m.get("name") or m.get("id"),
                    "context_length": m.get("context_length"),
                    "pricing": m.get("pricing", {})
                })
            return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت لیست مدل‌های OpenRouter: {str(e)}")


# ==========================================
# CHANNEL UNIVERSE (Fixed Poker Room & Global Cast)
# ==========================================

@app.get("/api/universe")
def get_universe():
    return load_universe()


@app.put("/api/universe")
def update_universe(data: Dict[str, Any]):
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="داده‌های ارسالی باید یک شیء معتبر JSON باشند")
    save_universe(data)
    return {
        "status": "success",
        "message": "اطلاعات دنیای کانال (میز و کاراکترها) با موفقیت ذخیره شد",
        "universe": data
    }


@app.post("/api/universe/upload/{asset_type}")
async def upload_universe_asset(
    asset_type: str,
    character_id: Optional[str] = Form(None),
    angle_id: Optional[str] = Form(None),
    sheet_type: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    if asset_type not in ["environment", "character", "camera_angle"]:
        raise HTTPException(status_code=400, detail="نوع فایل نامعتبر است. فقط 'environment', 'character' یا 'camera_angle' مجاز است.")

    UNIVERSE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    clean_name = file.filename.replace(" ", "_")
    if asset_type == "camera_angle" and angle_id:
        safe_filename = f"angle_{angle_id}_{clean_name}"
    elif asset_type == "character" and character_id:
        prefix = f"char_{character_id}"
        if sheet_type:
            prefix += f"_{sheet_type}"
        safe_filename = f"{prefix}_{clean_name}"
    else:
        safe_filename = f"{asset_type}_{clean_name}"
    file_path = UNIVERSE_MEDIA_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_url = f"/media/universe/{safe_filename}"
    universe = load_universe()

    if asset_type == "environment":
        universe.setdefault("environment", {})
        universe["environment"]["reference_image_path"] = relative_url
    elif asset_type == "camera_angle":
        if angle_id:
            universe.setdefault("environment", {})
            c_angles = universe["environment"].get("camera_angles", [])
            if isinstance(c_angles, list):
                for ang in c_angles:
                    if ang.get("id") == angle_id or ang.get("flow_tag") == angle_id:
                        ang["reference_image_path"] = relative_url
                        break
            elif isinstance(c_angles, dict):
                if angle_id in c_angles:
                    c_angles[angle_id]["reference_image_path"] = relative_url
    elif asset_type == "character":
        if character_id:
            for c in universe.get("characters", []):
                if c.get("id") == character_id or c.get("flow_tag") == character_id:
                    if sheet_type == "face":
                        c["face_sheet_image_path"] = relative_url
                        if not c.get("reference_image_path"):
                            c["reference_image_path"] = relative_url
                    elif sheet_type == "body":
                        c["body_sheet_image_path"] = relative_url
                        c["reference_image_path"] = relative_url
                    else:
                        c["reference_image_path"] = relative_url
                        c["body_sheet_image_path"] = relative_url
                    break

    save_universe(universe)
    return {
        "status": "success",
        "asset_type": asset_type,
        "character_id": character_id,
        "angle_id": angle_id,
        "sheet_type": sheet_type,
        "url": relative_url,
        "universe": universe
    }


class GenerateCharacterPromptsRequest(BaseModel):
    concept_fa: Optional[str] = None
    name_fa: Optional[str] = None
    archetype: Optional[str] = None
    flow_tag: Optional[str] = None
    model: Optional[str] = None


@app.post("/api/universe/characters/{character_id}/generate-prompts")
async def generate_character_prompts(
    character_id: str,
    req: GenerateCharacterPromptsRequest = GenerateCharacterPromptsRequest()
):
    universe = load_universe()
    chars = universe.get("characters", [])
    target_char = None
    for c in chars:
        if c.get("id") == character_id or c.get("flow_tag") == character_id:
            target_char = c
            break

    name_fa = (req.name_fa or (target_char.get("name_fa") if target_char else "") or "کاراکتر").strip()
    archetype = (req.archetype or (target_char.get("archetype") if target_char else "") or "Poker Player").strip()
    flow_tag = (req.flow_tag or (target_char.get("flow_tag") if target_char else "") or f"@{character_id}").strip()
    concept = (req.concept_fa or (target_char.get("persona_behavior_prompt") if target_char else "") or (target_char.get("personality_and_catchphrases_fa") if target_char else "") or "").strip()

    env = get_env_config()
    openrouter_key = env.get("OPENROUTER_API_KEY", "").strip()
    gemini_key = env.get("GEMINI_API_KEY", "").strip()

    if not openrouter_key and not gemini_key:
        raise HTTPException(
            status_code=400,
            detail="هیچ کلید API (OpenRouter یا Gemini) تنظیم نشده است. لطفاً از طریق آیکون چرخ‌دنده (Settings) کلید خود را وارد کنید."
        )

    system_prompt = """You are the Lead Visual Art Director & Character Designer for an Iranian animated poker comedy series.
The channel's visual identity is strictly:
HANDCRAFTED NEEDLE-FELTED STOP-MOTION ANIMATION STYLE
- Tactile fuzzy wool and miniature textile textures, visible delicate fibers, wire armature puppet feel.
- Soft warm studio macro lighting, shallow depth of field.
- Vertical 9:16 composition for YouTube Shorts and Instagram Reels.

Given the character's Iranian poker context, you must generate exactly THREE distinct, specialized prompts in STRICT JSON format:

1. `face_expressions_prompt_en`:
   - Head-and-shoulders close-up portraits ONLY of the needle-felted character from multiple angles (front view, three-quarter view, profile view).
   - Displaying 4 distinct core stop-motion facial expressions:
     1) Neutral analytical gaze / poker face;
     2) Smug confident smirk;
     3) Panicked/stressed wide bead-eyes with tiny felt sweat drop;
     4) Suspicious squint or wink calculating bluff probabilities.
   - Solid neutral light-gray studio background, macro lens capturing fine wool fibers.
   - Must include: "Handcrafted needle-felted stop-motion animation aesthetic, tactile fuzzy wool textures, visible fine fiber fuzz, miniature fabric details, soft warm studio macro lighting, solid neutral light-gray studio background, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16 --v 6.1"

2. `full_body_prompt_en`:
   - Full-body character turnaround sheet ONLY showing the puppet from head to toe.
   - Multi-angle views: front view, three-quarter view, side profile view, and back view.
   - Detailing slender or stout puppet proportions, miniature fabric clothing (hoodies, retro shirts, vests with miniature functional stitching/buttons), footwear, and signature handheld props (e.g. tablet, tea glass, prayer beads, chips).
   - Solid flat neutral light-gray studio background.
   - Must include: "Handcrafted needle-felted stop-motion animation aesthetic, tactile fuzzy wool and miniature textile textures, visible fine fibers, soft warm studio macro lighting, solid flat neutral light-gray studio background, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16 --v 6.1"

3. `persona_behavior_prompt`:
   - Rich Persian text describing the character's psychology, poker strategy/weaknesses, Iranian slang/catchphrases, speech tempo/rhythm, and signature physical mannerisms / silent acting body language (e.g. adjusting glasses, twirling beads, tapping felt, nervous foot tapping).

Output strictly a JSON object with keys:
{
  "face_expressions_prompt_en": "...",
  "full_body_prompt_en": "...",
  "persona_behavior_prompt": "..."
}"""

    user_prompt = f"""Character Name (FA): {name_fa}
Flow Tag: {flow_tag}
Archetype: {archetype}
User Concept / Behavior Idea:
{concept if concept else f"یک بازیکن پوکر ایرانی با تیپ {archetype}"}
"""

    parsed = None
    if openrouter_key:
        model = req.model or env.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.4
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در تماس با OpenRouter: {str(e)}")

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"OpenRouter Error: {res.text}")
        reply_content = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(reply_content)
    else:
        # Fallback to Gemini API
        model = req.model or env.get("GEMINI_MODEL", "gemini-2.5-flash")
        parsed = await call_gemini_generate_content(gemini_key, model, system_prompt, user_prompt, 0.4)

    face_p = parsed.get("face_expressions_prompt_en", "")
    body_p = parsed.get("full_body_prompt_en", "")
    persona_p = parsed.get("persona_behavior_prompt", "")

    if target_char is not None:
        target_char["face_expressions_prompt_en"] = face_p
        target_char["full_body_prompt_en"] = body_p
        target_char["persona_behavior_prompt"] = persona_p
        target_char["visual_prompt_en"] = body_p
        target_char["personality_and_catchphrases_fa"] = persona_p
        save_universe(universe)

    return {
        "status": "success",
        "character_id": character_id,
        "character": target_char,
        "face_expressions_prompt_en": face_p,
        "full_body_prompt_en": body_p,
        "persona_behavior_prompt": persona_p
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
        if item.is_dir():
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
        # Append unique suffix if needed
        folder_name = f"{folder_name}-{datetime.now().strftime('%H%M%S')}"
        proj_dir = PROJECTS_DIR / folder_name
        
    for sub in ["audio", "characters", "scenes", "exports"]:
        (proj_dir / sub).mkdir(parents=True, exist_ok=True)
        
    raw_idea = (req.raw_hand_or_concept or req.theme or "").strip()
    theme_text = (req.theme or raw_idea or req.title).strip()

    new_state = {
        "episode_id": folder_name,
        "title": req.title,
        "english_title": req.english_title or "",
        "version": "1.1.0",
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
            "visual_style": "Modern stylized 2D cartoon, Rick & Morty meets Archer aesthetic",
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
    if not chosen_type or chosen_type not in ["characters", "scenes", "audio", "exports"]:
        raise HTTPException(status_code=400, detail="Invalid target/asset type. Allowed: characters, scenes, audio, exports")
        
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
# AI STUDIO BRIDGE: BUILD PROMPT & IMPORT JSON
# =========================================================

def read_skill_file(filename: str) -> str:
    path = SKILLS_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def compute_seated_neighbors_context(characters: List[Dict[str, Any]], camera_angles_map: Dict[str, Any]):
    """
    Given the episode characters and the camera angles map,
    maps seat_1..seat_6 to assigned characters and calculates
    left (counter-clockwise) and right (clockwise) neighbors.
    Returns (neighbors_map, seating_summary_text).
    """
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
    """
    Builds a bundled, ready-to-copy mega prompt for Google AI Studio / Gemini flagship models.
    Stages supported: bible, script, characters, scenes.
    """
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
- Target Platform: 9:16 Vertical Video (YouTube Shorts & Instagram Reels)

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Generate ONLY a valid JSON object matching the requested schema (`concept_summary`, `hand_details`, `archetypes`, `comedy_beats`). Do not include any explanations or commentary outside of the JSON object.
"""
        return {
            "episode_id": episode_id,
            "stage": "bible",
            "skill_file": skill_filename,
            "prompt": prompt
        }

    elif stage_key in ["3", "script"]:
        skill_filename = "02-persian-script-writer.md"
        skill_content = read_skill_file(skill_filename)
        bible_data = state.get("bible", {})
        
        prompt = f"""You are an elite Persian Comedy Scriptwriter & Voice Director for an animated poker YouTube channel.
Convert the approved Episode Bible below into a fast-paced, hilarious 60-70 second script in STRICT JSON format.

CRITICAL DUAL-TEXT RULE:
Every single item in `segments` MUST include BOTH:
1. `subtitle_fa`: Clean, colloquial Persian for subtitles.
2. `tts_fa`: Phonetic Persian with COMPLETE DIACRITICS (اعراب: فَتْحَه، کَسْرَه، ضَمَّه، تَشْدید) and Persianized poker terms (فِلاپ، تِریبِت، چِک‌رِیز، آل‌آین، سوتِد، کانِکتور) for ElevenLabs AI voice generation.

---
### RECURRING CAST PERSONALITIES & CATCHPHRASES:
{u_chars_summary}
NOTE: When dialogue involves Arash or Bijan, strictly weave in their signature catchphrases and distinct speech rhythms.

---
### EPISODE BIBLE CONTEXT:
- Title: {state.get('title')}
- Concept Summary: {json.dumps(bible_data.get('concept_summary', state.get('idea', {})), ensure_ascii=False, indent=2)}
- Hand Details: {json.dumps(bible_data.get('hand_details', {}), ensure_ascii=False, indent=2)}
- Archetypes: {json.dumps(bible_data.get('archetypes', state.get('characters', [])), ensure_ascii=False, indent=2)}
- Comedy Beats & Punchlines: {json.dumps(bible_data.get('comedy_beats', []), ensure_ascii=False, indent=2)}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Generate ONLY a valid JSON object matching the schema (`script_title`, `total_estimated_duration_sec`, `segments`). Do not include markdown code fence formatting or commentary outside the JSON object.
"""
        return {
            "episode_id": episode_id,
            "stage": "script",
            "skill_file": skill_filename,
            "prompt": prompt
        }

    elif stage_key in ["4", "characters"]:
        skill_filename = "03-character-anchor.md"
        skill_content = read_skill_file(skill_filename)
        bible_data = state.get("bible", {})
        
        prompt = f"""You are the Visual Art Director for an Iranian stylized 2D/3D poker animation channel.
Generate character sheet turnaround prompts in English.

MANDATORY FORMAT RULE:
All character turnaround prompts and style_bible_en MUST target vertical 9:16 format (`vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`). Never use 16:9 widescreen.

KEY INSTRUCTIONS:
- Channel Universe Anchor: Arash (@Arash) is designated as `is_style_anchor: true`.
- Other recurring cast (@Bijan) and secondary characters must strictly inherit the style anchor.
- Output English model turnaround sheet prompts in vertical 9:16 format (front, side, 3/4 view, 3 expressive faces, neutral background).

---
### PERSISTENT UNIVERSE CAST:
{u_chars_summary}

---
### CONTEXT:
- Episode Title: {state.get('title')}
- Archetypes: {json.dumps(bible_data.get('archetypes', state.get('characters', [])), ensure_ascii=False, indent=2)}
- Visual Style Bible: {state.get('bible', {}).get('visual_style', u_env.get('style_note_en', 'Modern 2D stylized cartoon adult animation'))}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Generate ONLY a valid JSON object matching the schema (`style_bible_en`, `characters`).
"""
        return {
            "episode_id": episode_id,
            "stage": "characters",
            "skill_file": skill_filename,
            "prompt": prompt
        }

    elif stage_key in ["6", "scenes"]:
        skill_filename = "04-scene-director.md"
        skill_content = read_skill_file(skill_filename)
        
        # Build 6-Max spatial seating summary & neighbors
        raw_angles = u_env.get("camera_angles", [])
        if isinstance(raw_angles, list):
            camera_angles_map = {a.get("id"): a for a in raw_angles if isinstance(a, dict)}
        elif isinstance(raw_angles, dict):
            camera_angles_map = raw_angles
        else:
            camera_angles_map = {}
        _, seating_summary = compute_seated_neighbors_context(state.get('characters', []), camera_angles_map)

        prompt = f"""You are the Lead Storyboard, Motion & Continuity Director.
Break the approved script segments and character roster into snappy, rapid-fire cuts for vertical 9:16 Shorts/Reels in a SINGLE UNIFIED PASS with strict Episode Master-Shot Continuity.

6-MAX POKER TABLE 3D SPATIAL CONTINUITY & SEATED NEIGHBORS:
{seating_summary}

EPISODE MASTER-SHOT CONTINUITY & PERSISTENT TABLE STATE RULES:
1. SCENE 1 IS ALWAYS THE EPISODE MASTER REFERENCE (@Room_Master):
   - Scene 1 MUST ALWAYS be the wide establishing master shot (@Room_Master) of the entire 6-max needle-felted table.
   - It visually establishes all active seated characters at their assigned seats (seat_1..seat_6), the initial preflop table state (pot size, green wool felt, signature props like Bijan's tea estekan and amber tasbih), and chandelier macro lighting.
   - This frame serves as [Episode_Scene_1_Master] for the entire episode.
2. SCENE 2+ REFERENCE LOCK:
   - In EVERY subsequent scene (Scene 2, Scene 3, etc.), visual_prompt_en MUST explicitly start with:
     "Maintain exact visual continuity, character seating positions, chip stack colors, and table prop placement matching [Episode_Scene_1_Master]."
3. SEATED NEIGHBORS INJECTION (adjacent_players):
   - Using the clockwise order (seat_1 -> seat_2 -> seat_3 -> seat_4 -> seat_5 -> seat_6 -> seat_1), calculate and specify adjacent left and right seated neighbors.
   - Never leave adjacent chairs empty if an active character is seated there.
   - TIGHT MEDIUM CLOSE-UP FRAMING: Frame character dialogue/reaction cuts chest-up (@Seat_1..@Seat_6). Center the focal character with table rail/chips in immediate foreground, specific seat wall landmarks behind, and soft out-of-focus shoulders or side profiles of neighboring seated puppets at the frame edges. Avoid wide shots that re-randomize the center table!
4. PERSISTENT TABLE STATE (table_state_en):
   - Explicitly track and output "table_state_en" for every scene: evolving pot size (empty / small / massive chip tower), community cards on green felt (none / flop 3 / turn 4 / river 5), and player signature props (Bijan's tea glass & tasbih, Arash's notebook/tablet, chip stacks).
   - Embed these table state details directly into visual_prompt_en.

UNIFIED FAST-PACED ~2s PACING & SHOT MODE RULES:
1. FAST-PACED CUTS (1.5s to 2.5s, average ~2.0s): ALL scenes—both static_zoom and ai_video—must target 1.5s to 2.5s duration. Never generate 4s-5s scenes. Break long script segments into multiple ~2s cuts.
2. ~70% "shot_mode": "static_zoom" (1.5s-2.5s): Fast dialogue, connective cuts, explanations. Animated via FFmpeg camera movement. Provide "camera_effect": "zoom_in" | "zoom_out" | "pan_left" | "shake". Leave "motion_prompt_en": "" (strictly empty string).
3. ~30% "shot_mode": "ai_video" (1.5s-2.5s): ONLY for the funniest punchlines, extreme emotional reactions (rage, sweating, tilt, smug grin), and showdown climaxes. Provide a punchy single-action "motion_prompt_en" designed for a 2s highlight cut.
   - Reference @Arash, @Bijan, @PokerRoom tags.
   - Strictly silent acting: "tactile 12fps stop-motion puppet animation, subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking)".
   - Grounded props only: chips/cards flat on felt or held steadily (no airborne physics).
   - CRITICAL: NO duration (e.g. 2s) or aspect-ratio flags (e.g. --ar 9:16) inside the "motion_prompt_en" text!
4. MANDATORY GOOGLE FLOW @TAGS: Always specify the room/table as `{u_env.get('flow_tag', '@PokerRoom')}` and characters by their Flow tags (e.g. `@Arash`, `@Bijan`) in visual_prompt_en and motion_prompt_en.
5. MANDATORY FORMAT: All `visual_prompt_en` must strictly include `vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`.

For each scene, output:
- `scene_id`, `segment_ids`, `duration_sec` (1.5 to 2.5, e.g. 2.0), `scene_title_fa`, `shot_mode` ("static_zoom" or "ai_video"), `camera_effect` ("zoom_in", "zoom_out", "pan_left", "shake"), `camera_angle`, `characters_present`.
- `adjacent_players`: array of neighboring players string (e.g. ["@Bijan (seat_5, right edge)"]).
- `table_state_en`: string describing persistent table state and props.
- `visual_prompt_en`: Detailed English image prompt referencing `{u_env.get('flow_tag', '@PokerRoom')}`, `@Character` tags, [Episode_Scene_1_Master] reference lock for Scene 2+, adjacent puppet shoulder, landmarks, and `vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`.
- `motion_prompt_en`: string ("" for static_zoom; punchy 2-second single-action highlight prompt without duration/ar flags for ai_video).
- `target_video_sec`: float (e.g. 2.0).
- `poker_hud_overlay`: On-screen HUD notes (hero_hand, board, pot_bb, action_badge).
- `sfx_cue`: Specific audio SFX tag (chip_splash, card_deal, record_scratch, heartbeat, all_in_alarm, etc.).

---
### SCRIPT SEGMENTS:
{json.dumps(state.get('script', {}).get('segments', []), ensure_ascii=False, indent=2)}

### CHARACTERS:
{json.dumps(state.get('characters', []), ensure_ascii=False, indent=2)}

---
### SKILL GUIDELINES ({skill_filename}):
{skill_content}

---
### OUTPUT REQUIREMENT:
Generate ONLY a valid JSON object matching the schema (`scenes`).
"""
        return {
            "episode_id": episode_id,
            "stage": "scenes",
            "skill_file": skill_filename,
            "prompt": prompt
        }

    else:
        raise HTTPException(status_code=400, detail=f"Stage '{stage}' not supported for AI Studio prompt generation")


class ImportJsonRequest(BaseModel):
    json_content: Union[str, Dict[str, Any]]


@app.post("/api/projects/{episode_id}/import-json/{stage}")
def import_ai_studio_json(episode_id: str, stage: str, req: ImportJsonRequest):
    """
    Parses and validates pasted JSON from Google AI Studio / Gemini, saves it into
    the corresponding section of state.json, and advances/updates stage status.
    """
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
        # Update Bible & Idea
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

        approve_stage_num(1, "ایده و دست با موفقیت از هوش مصنوعی ثبت شد")
        approve_stage_num(2, "کتابچه استراتژی و جوک‌ها ذخیره شد")

    elif stage_key in ["3", "script"]:
        # Update Script
        segments = parsed.get("segments", [])
        if not segments and isinstance(parsed, list):
            segments = parsed
            
        if not segments:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه segments نیست")
            
        state["script"] = state.get("script", {})
        if "script_title" in parsed:
            state["script"]["title"] = parsed["script_title"]
        state["script"]["segments"] = segments
        
        # Synchronize audio tracks
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

        approve_stage_num(3, "سناریوی دو متنی با اعراب TTS تایید و ذخیره شد")

    elif stage_key in ["4", "characters"]:
        # Update Characters
        char_list = parsed.get("characters", [])
        if not char_list and isinstance(parsed, list):
            char_list = parsed
            
        if not char_list:
            raise HTTPException(status_code=400, detail="ورودی حاوی آرایه characters نیست")
            
        # Enrich characters with placeholders/defaults
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
        # Update Scenes
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
            
            # Format HUD overlay
            hud = sc.get("poker_hud_overlay", {})
            if isinstance(hud, str):
                hud = {"action_badge": hud}
                
            motion_p = sc.get("motion_prompt_en") or old_sc.get("motion_prompt_en", "")
            mode = sc.get("shot_mode") or ("ai_video" if motion_p.strip() else "static_zoom")
            effect = sc.get("camera_effect") or old_sc.get("camera_effect", "zoom_in")
            dur = float(sc.get("duration_sec") or old_sc.get("duration_sec") or 2.0)
            table_state_text = sc.get("table_state_en") or old_sc.get("table_state_en", "")
            adjacent = sc.get("adjacent_players") or old_sc.get("adjacent_players", [])

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
                "shot_mode": mode,
                "camera_effect": effect,
                "visual_prompt": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "visual_prompt_en": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "motion_prompt_en": motion_p,
                "target_video_sec": float(sc.get("target_video_sec") or dur or 2.0),
                "poker_table_state": hud,
                "sfx_cue": sc.get("sfx_cue", "chip_splash"),
                "visual_asset": old_sc.get("visual_asset") or sc.get("visual_asset") or f"/media/{episode_id}/scenes/scene_{min(idx, 3):02d}.svg",
                "video_path": old_sc.get("video_path") or sc.get("video_path"),
                "video_asset": old_sc.get("video_asset") or sc.get("video_asset"),
                "status": "approved"
            })
            
        state["scenes"] = enriched_scenes
        approve_stage_num(6, "بیت‌های بصری استوری‌بورد و حرکت تایید و ذخیره شد")

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported stage '{stage}' for JSON import")

    save_state(episode_id, state)
    return {
        "status": "success",
        "message": f"داده‌های مرحله {stage} با موفقیت تایید و در state.json ذخیره شد",
        "current_stage": state.get("current_stage"),
        "state": state
    }


# =========================================================
# OPENROUTER AUTOMATION: GENERATE SCENES & REGENERATE TTS
# =========================================================

class OpenRouterTaskRequest(BaseModel):
    model: Optional[str] = None
    task_data: Optional[Dict[str, Any]] = None


@app.post("/api/projects/{episode_id}/run-openrouter/{task}")
async def run_openrouter_task(episode_id: str, task: str, req: OpenRouterTaskRequest = OpenRouterTaskRequest()):
    """
    Executes automated tasks via OpenRouter API with json_object response format.
    Supported tasks:
    1. generate_scenes: Uses 04-scene-director.md to generate scenes from state.json
    2. regenerate_tts_fa: Re-generates diacritic-heavy tts_fa for a Persian subtitle line
    """
    env = get_env_config()
    api_key = env.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="کلید OpenRouter API تنظیم نشده است. لطفاً از طریق آیکون چرخ‌دنده (Settings) در هدر، کلید خود را وارد کنید."
        )

    model = req.model or env.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    state = load_state(episode_id)
    
    if task == "generate_scenes":
        skill_content = read_skill_file("04-scene-director.md")
        segments = state.get("script", {}).get("segments", [])
        characters = state.get("characters", [])
        universe = load_universe()
        u_env = universe.get("environment", {})
        
        # Build 6-Max spatial seating summary & neighbors
        raw_angles = u_env.get("camera_angles", [])
        if isinstance(raw_angles, list):
            camera_angles_map = {a.get("id"): a for a in raw_angles if isinstance(a, dict)}
        elif isinstance(raw_angles, dict):
            camera_angles_map = raw_angles
        else:
            camera_angles_map = {}
        _, seating_summary = compute_seated_neighbors_context(characters, camera_angles_map)
        
        if not segments:
            raise HTTPException(
                status_code=400, 
                detail="سناریویی در این اپیزود ثبت نشده است. لطفاً ابتدا در مرحله ۳ سناریو را وارد یا تایید کنید."
            )

        system_prompt = f"""{skill_content}

You are the Lead Storyboard, Motion & Continuity Director.
Generate a complete, fast-paced vertical 9:16 storyboard with selective motion prompting in a SINGLE PASS with strict Episode Master-Shot Continuity.

6-MAX POKER TABLE 3D SPATIAL CONTINUITY & SEATED NEIGHBORS:
{seating_summary}

EPISODE MASTER-SHOT CONTINUITY & PERSISTENT TABLE STATE RULES:
1. SCENE 1 IS ALWAYS THE EPISODE MASTER REFERENCE (@Room_Master):
   - Scene 1 MUST ALWAYS be the wide establishing master shot (@Room_Master) of the entire 6-max needle-felted table.
   - It visually establishes all active seated characters at their assigned seats (seat_1..seat_6), the initial preflop table state (pot size, green wool felt, signature props like Bijan's tea estekan and amber tasbih), and chandelier macro lighting.
   - This frame serves as [Episode_Scene_1_Master] for the entire episode.
2. SCENE 2+ REFERENCE LOCK:
   - In EVERY subsequent scene (Scene 2, Scene 3, etc.), visual_prompt_en MUST explicitly start with:
     "Maintain exact visual continuity, character seating positions, chip stack colors, and table prop placement matching [Episode_Scene_1_Master]."
3. SEATED NEIGHBORS INJECTION (adjacent_players):
   - Using the clockwise order (seat_1 -> seat_2 -> seat_3 -> seat_4 -> seat_5 -> seat_6 -> seat_1), calculate and specify adjacent left and right seated neighbors.
   - Never leave adjacent chairs empty if an active character is seated there.
   - TIGHT MEDIUM CLOSE-UP FRAMING: Frame character dialogue/reaction cuts chest-up (@Seat_1..@Seat_6). Center the focal character with table rail/chips in immediate foreground, specific seat wall landmarks behind, and soft out-of-focus shoulders or side profiles of neighboring seated puppets at the frame edges. Avoid wide shots that re-randomize the center table!
4. PERSISTENT TABLE STATE (table_state_en):
   - Explicitly track and output "table_state_en" for every scene: evolving pot size (empty / small / massive chip tower), community cards on green felt (none / flop 3 / turn 4 / river 5), and player signature props (Bijan's tea glass & tasbih, Arash's notebook/tablet, chip stacks).
   - Embed these table state details directly into visual_prompt_en.

UNIFIED FAST-PACED ~2s PACING & SHOT MODE RULES:
1. FAST-PACED CUTS (1.5s to 2.5s, average ~2.0s): ALL scenes must target 1.5s to 2.5s duration. Never generate 4s-5s scenes. Break long script segments into snappy cuts.
2. ~70% "shot_mode": "static_zoom" (1.5s-2.5s): Fast dialogue, connective cuts, explanations. Animated via FFmpeg camera movement. Provide "camera_effect": "zoom_in" | "zoom_out" | "pan_left" | "shake". Leave "motion_prompt_en": "" (strictly empty string).
3. ~30% "shot_mode": "ai_video" (1.5s-2.5s): ONLY for the funniest punchlines, extreme emotional reactions (rage, sweating, tilt, smug grin), and showdown climaxes. Provide a punchy single-action "motion_prompt_en" designed for a 2s highlight cut.
   - Reference @Arash, @Bijan, @PokerRoom tags.
   - Strictly silent acting: "tactile 12fps stop-motion puppet animation, subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking)".
   - Grounded props only: chips/cards flat on felt or held steadily (no airborne physics).
   - CRITICAL: NO duration (e.g. 2s) or aspect-ratio flags (e.g. --ar 9:16) inside the "motion_prompt_en" text!
4. MANDATORY GOOGLE FLOW @TAGS: Always specify the room/table as `{u_env.get('flow_tag', '@PokerRoom')}` and characters by their Flow tags (e.g. `@Arash`, `@Bijan`) in visual_prompt_en and motion_prompt_en.
5. MANDATORY FORMAT: All `visual_prompt_en` must strictly target vertical 9:16 format (`vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`).

Output ONLY a strict JSON object with a single key "scenes" containing the array of 1.5-to-2.5-second visual scenes matching the schema with adjacent_players and table_state_en.
Do not wrap with markdown codeblocks or output any text outside the JSON."""

        user_content = f"""Break this Persian poker script and character roster into visual scenes:
Episode Title: {state.get('title')}
Channel Fixed Room: {u_env.get('flow_tag', '@PokerRoom')} - {u_env.get('name', 'Poker Room')}

Script Segments:
{json.dumps(segments, ensure_ascii=False, indent=2)}

Characters:
{json.dumps(characters, ensure_ascii=False, indent=2)}
"""

        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در ارتباط با سرور OpenRouter: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter Error ({response.status_code}): {response.text}"
            )

        result_data = response.json()
        raw_reply = result_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(raw_reply)
        scene_list = parsed.get("scenes", [])
        
        # Enrich and update state while preserving existing assets
        existing_scenes_map = {s.get("id"): s for s in state.get("scenes", [])}
        enriched_scenes = []
        for idx, sc in enumerate(scene_list, 1):
            sc_id = sc.get("scene_id") or sc.get("id") or f"scene_{idx:02d}"
            old_sc = existing_scenes_map.get(sc_id, {})
            
            hud = sc.get("poker_hud_overlay", {})
            if isinstance(hud, str):
                hud = {"action_badge": hud}
                
            motion_p = sc.get("motion_prompt_en") or old_sc.get("motion_prompt_en", "")
            mode = sc.get("shot_mode") or ("ai_video" if motion_p.strip() else "static_zoom")
            effect = sc.get("camera_effect") or old_sc.get("camera_effect", "zoom_in")
            dur = float(sc.get("duration_sec") or old_sc.get("duration_sec") or 2.0)
            table_state_text = sc.get("table_state_en") or old_sc.get("table_state_en", "")
            adjacent = sc.get("adjacent_players") or old_sc.get("adjacent_players", [])
            
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
                "shot_mode": mode,
                "camera_effect": effect,
                "visual_prompt": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "visual_prompt_en": sc.get("visual_prompt_en", sc.get("visual_prompt", old_sc.get("visual_prompt", ""))),
                "motion_prompt_en": motion_p,
                "target_video_sec": float(sc.get("target_video_sec") or dur or 2.0),
                "poker_table_state": hud,
                "sfx_cue": sc.get("sfx_cue", "chip_splash"),
                "visual_asset": old_sc.get("visual_asset") or sc.get("visual_asset") or f"/media/{episode_id}/scenes/scene_{min(idx, 3):02d}.svg",
                "video_path": old_sc.get("video_path") or sc.get("video_path"),
                "video_asset": old_sc.get("video_asset") or sc.get("video_asset"),
                "status": "ready_for_review"
            })
            
        state["scenes"] = enriched_scenes
        save_state(episode_id, state)
        return {"status": "success", "scenes": enriched_scenes}

    elif task == "regenerate_tts_fa":
        task_data = req.task_data or {}
        subtitle_fa = task_data.get("subtitle_fa", "").strip()
        if not subtitle_fa:
            raise HTTPException(status_code=400, detail="متن subtitle_fa ارسال نشده است")
            
        speaker = task_data.get("speaker", "Narration")
        emotion = task_data.get("emotion", "conversational")
        
        system_prompt = """You are an expert Persian Voice Director & Phonetician for AI voice generation (such as ElevenLabs).
Your job is to convert colloquial Persian poker lines into phonetic Persian text with COMPLETE DIACRITICS (فَتْحَه، کَسْرَه، ضَمَّه، تَشْدید، سُکون) so the AI voice pronounces every word smoothly without foreign accent glitches.
Also replace poker terms with standard Persianized phonetic spelling (فِلاپ، تِریبِت، چِک‌رِیز، آل‌آین، سوتِد، کانِکتور، بوردِ خُشک، سی‌بِت، بْلَف، فولد، کال).

Output STRICT JSON with a single key "tts_fa":
{"tts_fa": "..."}"""

        user_content = f"Speaker: {speaker}\nEmotion: {emotion}\nPersian Subtitle:\n{subtitle_fa}"

        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در ارتباط با سرور OpenRouter: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter Error ({response.status_code}): {response.text}"
            )

        result_data = response.json()
        raw_reply = result_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(raw_reply)
        tts_fa = parsed.get("tts_fa", subtitle_fa)
        
        return {"status": "success", "tts_fa": tts_fa}

    elif task == "generate_motion_prompts":
        skill_content = read_skill_file("05-motion-director.md")
        scenes = state.get("scenes", [])
        segments = state.get("script", {}).get("segments", [])
        universe = load_universe()
        u_env = universe.get("environment", {})
        
        if not scenes:
            raise HTTPException(
                status_code=400,
                detail="صحنه‌ای در این اپیزود ثبت نشده است. ابتدا مرحله ۶ را اجرا یا ثبت کنید."
            )
            
        system_prompt = f"""{skill_content}

You are an expert Animation & Cinematography Director for Google Flow (Veo) targeting vertical 9:16 videos.
CRITICAL ANTI-MORPHING & ANTI-MELTING RULES:
1. SHORT CLIPS ONLY (4s or 5s): `target_video_sec` must be strictly '4s' or '5s'. Never generate 8s or 10s clips.
2. ONE PRIMARY ACTION PER SHOT: Never chain multiple complex hand movements (e.g. do NOT slide chips AND adjust glasses AND flick coins). Limit each clip to ONE simple physical action + ONE smooth camera move (mouth closed, silent expressive acting).
3. AVOID MID-AIR SMALL OBJECT PHYSICS: Strictly avoid airborne spinning chips, flying cards, or individual moving prayer beads. All props must remain flat on table felt or held steadily in hands.
4. MANDATORY GOOGLE FLOW @TAGS: In every motion_prompt_en, reference the poker room as `{u_env.get('flow_tag', '@PokerRoom')}` and characters with their Google Flow tags (e.g. `@Arash`, `@Bijan`) so Google Flow links their reference sheets.
5. MANDATORY FORMAT: Every `motion_prompt_en` MUST explicitly include: `vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`.
Output STRICT JSON with key "scenes_motion":
{{"scenes_motion": [{{"scene_id": "...", "target_video_sec": "5s", "motion_prompt_en": "...", "camera_notes": "..."}}]}}"""

        scenes_brief = []
        for idx, sc in enumerate(scenes):
            scenes_brief.append({
                "scene_id": sc.get("id") or sc.get("scene_id") or f"scene_{idx+1:02d}",
                "title": sc.get("title") or sc.get("scene_title_fa"),
                "visual_prompt": sc.get("visual_prompt") or sc.get("visual_prompt_en"),
                "duration_sec": sc.get("duration_sec", 4.5),
                "camera": sc.get("camera"),
                "segment_ids": sc.get("segment_ids", [])
            })

        user_content = f"""Scenes to direct for Google Flow:
Episode Title: {state.get('title')}

Script Segments:
{json.dumps(segments, ensure_ascii=False, indent=2)}

Existing Scenes:
{json.dumps(scenes_brief, ensure_ascii=False, indent=2)}
"""

        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در ارتباط با سرور OpenRouter: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter Error ({response.status_code}): {response.text}"
            )

        result_data = response.json()
        raw_reply = result_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(raw_reply)
        motions_list = parsed.get("scenes_motion", [])
        
        # Merge motion prompts into existing scenes without erasing existing visual_asset / video_path
        motion_map = {m.get("scene_id"): m for m in motions_list if isinstance(m, dict)}
        for idx, sc in enumerate(scenes):
            sc_id = sc.get("id") or sc.get("scene_id") or f"scene_{idx+1:02d}"
            m_data = motion_map.get(sc_id) or (motions_list[idx] if idx < len(motions_list) else None)
            if m_data:
                sc["motion_prompt_en"] = m_data.get("motion_prompt_en", sc.get("motion_prompt_en", ""))
                raw_sec = m_data.get("target_video_sec", sc.get("target_video_sec", "5s"))
                sc["target_video_sec"] = raw_sec if raw_sec in ["4s", "5s"] else ("4s" if float(sc.get("duration_sec", 5.0) or 5.0) <= 4.2 else "5s")
                if "camera_notes" in m_data:
                    sc["camera_notes"] = m_data["camera_notes"]
                    
        state["scenes"] = scenes
        save_state(episode_id, state)
        return {"status": "success", "scenes": scenes}

    else:
        raise HTTPException(status_code=400, detail=f"Task '{task}' not recognized. Allowed: generate_scenes, regenerate_tts_fa, generate_motion_prompts")


# =========================================================
# SCENE-LEVEL FEEDBACK & REWRITE (Human-in-the-Loop)
# =========================================================

class RewriteScenePromptRequest(BaseModel):
    target: str  # "image" or "motion"
    feedback: str
    model: Optional[str] = None


@app.post("/api/projects/{episode_id}/scenes/{scene_id}/rewrite-prompt")
async def rewrite_scene_prompt(
    episode_id: str,
    scene_id: str,
    req: RewriteScenePromptRequest
):
    target = req.target.lower().strip()
    if target not in ["image", "motion"]:
        raise HTTPException(status_code=400, detail="Target must be 'image' or 'motion'")

    feedback = req.feedback.strip()
    if not feedback:
        raise HTTPException(status_code=400, detail="متن فیدبک یا دستور اصلاح پرامپت ارسال نشده است")

    env = get_env_config()
    api_key = env.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="کلید OpenRouter API تنظیم نشده است. لطفاً از طریق آیکون تنظیمات (چرخ‌دنده) کلید خود را وارد کنید."
        )

    model = req.model or env.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    state = load_state(episode_id)
    scenes = state.get("scenes", [])

    target_scene = None
    for sc in scenes:
        if sc.get("id") == scene_id or sc.get("scene_id") == scene_id:
            target_scene = sc
            break

    if not target_scene:
        raise HTTPException(status_code=404, detail=f"صحنه با شناسه '{scene_id}' یافت نشد")

    # Contextual script lines
    seg_ids = target_scene.get("segment_ids", [])
    all_segments = state.get("script", {}).get("segments", [])
    linked_segments = [s for s in all_segments if s.get("id") in seg_ids]

    if target == "image":
        current_prompt = target_scene.get("visual_prompt_en") or target_scene.get("visual_prompt", "")
        is_scene_1 = (target_scene.get("beat_index") == 1 or scene_id in ["scene_01", "scene_1"])
        continuity_rule = (
            "This is Scene 1 (Episode Master Establishing Reference Shot at @Room_Master). It must establish all seated players, signature props, and initial table state."
            if is_scene_1
            else "This is Scene 2 or later. You MUST preserve the reference lock '[Episode_Scene_1_Master]', seated neighbor soft shoulders, and table state while applying the user's feedback."
        )

        system_prompt = f"""You are an expert Animation Storyboard Director for a handcrafted needle-felted stop-motion comedy poker animation.
Your task is to rewrite/refine the visual keyframe image prompt (`visual_prompt_en`) for a single scene according to the user's specific feedback (which may be in Persian or English).

CRITICAL ANTI-GLITCH & CONTINUITY RULES:
1. CONTINUITY LOCK: {continuity_rule}
2. ONE PRIMARY ACTION: Focus on one clear visual pose or reaction of the needle-felted puppet. No complex multi-action clutter.
3. AVOID MID-AIR SMALL OBJECT PHYSICS: No airborne spinning chips or flying cards; miniature props must stay flat on felt or held steadily in felted hands.
4. TIGHT MEDIUM CLOSE-UP FRAMING: For seat shots (@Seat_1..@Seat_6), frame chest-up with focal character, table rail/chips in foreground, specific seat wall landmarks behind, and soft out-of-focus shoulder of adjacent seated puppets at frame edges.
5. Precisely incorporate all details from the user's feedback.
6. Keep the handcrafted needle-felted stop-motion animation aesthetic (tactile fuzzy wool and miniature fabric textures, visible delicate fibers, soft warm studio macro lighting, rich saturated colors).
7. MANDATORY GOOGLE FLOW @TAGS: Strictly identify the room/table as @PokerRoom and characters with their Google Flow tags (e.g. @Arash, @Bijan).
8. MANDATORY FORMAT: Must strictly specify vertical 9:16 composition: "vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16". Never use 16:9 widescreen.
9. Output ONLY a valid JSON object with the single key "visual_prompt_en":
{{"visual_prompt_en": "..."}}"""

        user_content = f"""Episode Title: {state.get('title')}
Scene ID: {scene_id}
Scene Title: {target_scene.get('title') or target_scene.get('scene_title_fa')}
Camera: {target_scene.get('camera', 'Medium Shot')}
Characters Present: {json.dumps(target_scene.get('characters_present', []), ensure_ascii=False)}
Adjacent Players: {json.dumps(target_scene.get('adjacent_players', []), ensure_ascii=False)}
Table State: {target_scene.get('table_state_en', '')}

Linked Script Segments:
{json.dumps(linked_segments, ensure_ascii=False, indent=2)}

Current Visual Image Prompt:
{current_prompt}

User Feedback / Modification Instructions:
{feedback}
"""

        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در ارتباط با سرور OpenRouter: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter Error ({response.status_code}): {response.text}"
            )

        raw_reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(raw_reply)
        rewritten = parsed.get("visual_prompt_en") or parsed.get("prompt")
        if not rewritten:
            raise HTTPException(status_code=500, detail="خروجی هوش مصنوعی حاوی visual_prompt_en معتبر نبود.")

        target_scene["visual_prompt_en"] = rewritten
        target_scene["visual_prompt"] = rewritten
        save_state(episode_id, state)

        return {
            "status": "success",
            "scene_id": scene_id,
            "target": "image",
            "rewritten_prompt": rewritten,
            "scene": target_scene
        }

    else:  # target == "motion"
        current_prompt = target_scene.get("motion_prompt_en", "")
        visual_prompt = target_scene.get("visual_prompt_en") or target_scene.get("visual_prompt", "")
        target_sec = float(target_scene.get("target_video_sec") or target_scene.get("duration_sec") or 2.0)

        system_prompt = """You are an expert Animation & Cinematography Director for Google Flow (Veo) and Vidu.
Your task is to write/refine the motion prompt (`motion_prompt_en`) for a single scene according to the user's specific feedback (which may be in Persian or English).

CRITICAL FAST-PACED HIGHLIGHT RULES:
1. PUNCHY 2-SECOND HIGHLIGHT: Focus on ONE simple physical action or expressive facial reaction tailored for a snappy ~2-second cut.
2. ONE PRIMARY ACTION PER SHOT: Never chain multiple complex hand movements.
3. AVOID MID-AIR SMALL OBJECT PHYSICS: Chips and cards must stay flat on felt or held steadily in hands (no flying/spinning airborne props).
4. TACTILE 12FPS STOP-MOTION & SILENT ACTING: The puppet character must NOT talk or lip-sync ("tactile 12fps stop-motion puppet animation, subtle wool fiber texture movement, silent expressive acting, mouth closed, no talking") because Persian voiceover is synced separately.
5. MANDATORY GOOGLE FLOW @TAGS: Strictly reference the room/table as @PokerRoom and characters with their Google Flow tags (e.g. @Arash, @Bijan).
6. NO FLAGS OR DURATION IN PROMPT TEXT: DO NOT include --ar 9:16, aspect ratios, or duration tags (e.g. 2s) in the motion prompt text.
7. Precisely incorporate all details from the user's feedback.
8. Output ONLY a valid JSON object with the single key "motion_prompt_en":
{"motion_prompt_en": "..."}"""

        user_content = f"""Episode Title: {state.get('title')}
Scene ID: {scene_id}
Scene Title: {target_scene.get('title') or target_scene.get('scene_title_fa')}
Target Cut Duration: ~{target_sec}s

Keyframe Image Prompt:
{visual_prompt}

Linked Script Segments:
{json.dumps(linked_segments, ensure_ascii=False, indent=2)}

Current Motion Prompt:
{current_prompt}

User Feedback / Modification Instructions:
{feedback}
"""

        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Poker Animation Studio"
                    },
                    json=payload
                )
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"خطا در ارتباط با سرور OpenRouter: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter Error ({response.status_code}): {response.text}"
            )

        raw_reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = clean_and_parse_json(raw_reply)
        rewritten = parsed.get("motion_prompt_en") or parsed.get("prompt")
        if not rewritten:
            raise HTTPException(status_code=500, detail="خروجی هوش مصنوعی حاوی motion_prompt_en معتبر نبود.")

        target_scene["motion_prompt_en"] = rewritten
        target_scene["shot_mode"] = "ai_video"
        if not target_scene.get("target_video_sec"):
            target_scene["target_video_sec"] = 2.0
        save_state(episode_id, state)

        return {
            "status": "success",
            "scene_id": scene_id,
            "target": "motion",
            "rewritten_prompt": rewritten,
            "scene": target_scene
        }


class UpdateSceneDetailsRequest(BaseModel):
    shot_mode: Optional[str] = None
    camera_effect: Optional[str] = None
    motion_prompt_en: Optional[str] = None
    duration_sec: Optional[float] = None
    title: Optional[str] = None
    table_state_en: Optional[str] = None
    adjacent_players: Optional[List[str]] = None


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
        
    if req.shot_mode is not None:
        found_scene["shot_mode"] = req.shot_mode
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
        
    save_state(episode_id, state)
    return {"status": "success", "scene": found_scene}


# =========================================================
# DIRECT GEMINI API INTEGRATION (Stages 1 to 3)
# =========================================================

class GeminiRunRequest(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = 0.4


@app.post("/api/projects/{episode_id}/run-gemini/{stage}")
async def run_gemini_stage(episode_id: str, stage: str, req: GeminiRunRequest = GeminiRunRequest()):
    env = get_env_config()
    api_key = env.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="کلید Google Gemini API تنظیم نشده است. لطفاً از طریق آیکون چرخ‌دنده (تنظیمات) کلید خود را وارد کنید."
        )

    model = req.model or env.get("GEMINI_MODEL", "gemini-2.5-flash")
    state = load_state(episode_id)
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

    universe = load_universe()
    u_env = universe.get("environment", {})
    u_chars = universe.get("characters", [])
    u_chars_summary = "\n".join([
        f"  - {c.get('flow_tag', '')} ({c.get('name_fa', '')} - {c.get('archetype', '')}):\n    Behavioral & Physical Profile: {c.get('persona_behavior_prompt') or c.get('personality_and_catchphrases_fa', '')}"
        for c in u_chars
    ])

    if stage_key in ["1", "2", "bible", "idea"]:
        skill_content = read_skill_file("01-bible-and-jokes.md")
        idea_data = state.get("idea", {})
        raw_idea = (idea_data.get("raw_hand_or_concept") or idea_data.get("theme") or "").strip()
        
        system_prompt = f"""{skill_content}

Output strictly a valid JSON object matching the schema:
concept_summary, hand_details, archetypes, comedy_beats.
Do not wrap with markdown code blocks."""

        user_prompt = f"""Episode Title: {state.get('title')}
Channel Fixed Environment: {u_env.get('flow_tag', '@PokerRoom')} - {u_env.get('name', '')}
Recurring Cast Roster:
{u_chars_summary}
NOTE: By default, use recurring stars @Arash and @Bijan for the core hand archetypes (Hero / Villain) to maintain story continuity.

Raw Poker Hand & Idea (ایده خام و شرح دست پوکر):
{raw_idea}

Concept/Theme: {idea_data.get('theme', '')}
Core Lesson: {idea_data.get('core_lesson', '')}
"""

        parsed = await call_gemini_generate_content(api_key, model, system_prompt, user_prompt, req.temperature or 0.4)

        state["bible"] = state.get("bible", {})
        if "concept_summary" in parsed:
            state["bible"]["concept_summary"] = parsed["concept_summary"]
            if isinstance(parsed["concept_summary"], dict):
                theme = parsed["concept_summary"].get("theme")
                lesson = parsed["concept_summary"].get("poker_lesson")
                if theme and not state["idea"].get("theme"):
                    state["idea"]["theme"] = theme
                if lesson:
                    state["idea"]["core_lesson"] = lesson

        if "hand_details" in parsed:
            state["bible"]["hand_details"] = parsed["hand_details"]
        if "archetypes" in parsed:
            state["bible"]["archetypes"] = parsed["archetypes"]
        if "comedy_beats" in parsed:
            state["bible"]["comedy_beats"] = parsed["comedy_beats"]

        approve_stage_num(1, "ایده و دست توسط Gemini API تایید شد")
        approve_stage_num(2, "کتابچه استراتژی و جوک‌ها توسط Gemini API تولید شد")
        save_state(episode_id, state)
        return {
            "status": "success",
            "stage": "bible",
            "message": "کتابچه استراتژی و جوک‌ها با موفقیت توسط Gemini API تولید و ثبت شد",
            "state": state
        }

    elif stage_key in ["3", "script"]:
        skill_content = read_skill_file("02-persian-script-writer.md")
        bible_data = state.get("bible", {})
        
        system_prompt = f"""{skill_content}

CRITICAL: Every item in `segments` MUST have both `subtitle_fa` and diacritic-heavy `tts_fa` with Persianized poker terms.
Output strictly a valid JSON object with `script_title`, `total_estimated_duration_sec`, and `segments`.
Do not wrap with markdown code blocks."""

        user_prompt = f"""Episode Title: {state.get('title')}
Channel Fixed Table: {u_env.get('flow_tag', '@PokerRoom')}
Recurring Cast Personalities & Catchphrases:
{u_chars_summary}
NOTE: If dialogue involves Arash or Bijan, strictly weave in their signature catchphrases and distinct speech rhythms.

Episode Bible Context:
- Concept: {json.dumps(bible_data.get('concept_summary', state.get('idea', {})), ensure_ascii=False)}
- Hand Details: {json.dumps(bible_data.get('hand_details', {}), ensure_ascii=False)}
- Archetypes: {json.dumps(bible_data.get('archetypes', []), ensure_ascii=False)}
- Comedy Beats: {json.dumps(bible_data.get('comedy_beats', []), ensure_ascii=False)}
"""

        parsed = await call_gemini_generate_content(api_key, model, system_prompt, user_prompt, req.temperature or 0.4)

        segments = parsed.get("segments", [])
        if not segments and isinstance(parsed, list):
            segments = parsed
        if not segments:
            raise HTTPException(status_code=500, detail="خروجی Gemini حاوی آرایه segments نبود.")

        state["script"] = state.get("script", {})
        if "script_title" in parsed:
            state["script"]["title"] = parsed["script_title"]
        state["script"]["segments"] = segments

        # Synchronize audio tracks while preserving any existing audio recordings
        existing_tracks = {t.get("segment_id"): t for t in state.get("audio", {}).get("tracks", [])}
        new_tracks = []
        for s in segments:
            seg_id = s.get("id") or f"seg_{len(new_tracks)+1:02d}"
            old_track = existing_tracks.get(seg_id, {})
            new_tracks.append({
                "segment_id": seg_id,
                "speaker": s.get("speaker", "Narration"),
                "tts_text": s.get("tts_fa", s.get("subtitle_fa", "")),
                "subtitle_text": s.get("subtitle_fa", ""),
                "audio_file": old_track.get("audio_file") or f"/media/{episode_id}/audio/{seg_id}.wav",
                "status": old_track.get("status", "ready"),
                "duration_sec": float(s.get("estimated_duration_sec") or s.get("duration_est_sec") or 5.0)
            })
        state["audio"] = state.get("audio", {})
        state["audio"]["tracks"] = new_tracks

        approve_stage_num(3, "سناریوی دو متنی توسط Gemini API تولید شد")
        save_state(episode_id, state)
        return {
            "status": "success",
            "stage": "script",
            "message": "سناریو و اعراب تلفظی TTS با موفقیت توسط Gemini API تولید شد",
            "state": state
        }

    elif stage_key in ["4", "characters"]:
        skill_content = read_skill_file("03-character-anchor.md")
        bible_data = state.get("bible", {})
        script_data = state.get("script", {})
        
        system_prompt = f"""{skill_content}

MANDATORY FORMAT: All character turnaround prompts and style_bible_en MUST target vertical 9:16 format (`vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16`).
Designate Arash (@Arash) as `is_style_anchor: true`. Provide turnaround sheet prompts in English.
Output strictly a valid JSON object with `style_bible_en` and `characters`.
Do not wrap with markdown code blocks."""

        user_prompt = f"""Episode Title: {state.get('title')}
Channel Recurring Cast:
{u_chars_summary}

Archetypes: {json.dumps(bible_data.get('archetypes', []), ensure_ascii=False)}
Script Segments: {json.dumps(script_data.get('segments', []), ensure_ascii=False)}
Visual Style: {state.get('bible', {}).get('visual_style', u_env.get('style_note_en', 'Modern 2D cartoon animation'))}
"""

        parsed = await call_gemini_generate_content(api_key, model, system_prompt, user_prompt, req.temperature or 0.4)

        char_list = parsed.get("characters", [])
        if not char_list and isinstance(parsed, list):
            char_list = parsed
        if not char_list:
            raise HTTPException(status_code=500, detail="خروجی Gemini حاوی آرایه characters نبود.")

        existing_chars = {c.get("id"): c for c in state.get("characters", [])}
        enriched = []
        for idx, c in enumerate(char_list, 1):
            char_id = c.get("id") or f"char_{idx:02d}"
            old_c = existing_chars.get(char_id, {})
            is_anchor = c.get("is_style_anchor", idx == 1)

            enriched.append({
                "id": char_id,
                "name_fa": c.get("name_fa", old_c.get("name_fa", f"کاراکتر {idx}")),
                "name_en": c.get("name_en", old_c.get("name_en", "Character")),
                "role": c.get("role", old_c.get("role", "Poker Player")),
                "is_style_anchor": is_anchor,
                "status": "approved",
                "avatar_url": old_c.get("avatar_url") or c.get("avatar_url") or f"/media/{episode_id}/characters/kambiz.svg",
                "turnaround_sheet": old_c.get("turnaround_sheet") or c.get("turnaround_sheet") or f"/media/{episode_id}/characters/kambiz_sheet.svg",
                "style_prompt": c.get("character_sheet_prompt_en", c.get("style_prompt", old_c.get("style_prompt", ""))),
                "character_sheet_prompt_en": c.get("character_sheet_prompt_en", ""),
                "consistency_tags": c.get("consistency_tags", ""),
                "voice_id": c.get("voice_id", old_c.get("voice_id", "eleven_persian_narrator")),
                "tagline": c.get("tagline", old_c.get("tagline", ""))
            })

        state["characters"] = enriched
        approve_stage_num(4, "مدل‌شیت و لنگر استایل کاراکترها توسط Gemini API تولید شد")
        save_state(episode_id, state)
        return {
            "status": "success",
            "stage": "characters",
            "message": "کاراکترها و لنگر استایل با موفقیت توسط Gemini API تولید شد",
            "state": state
        }

    else:
        raise HTTPException(status_code=400, detail=f"مرحله '{stage}' برای اجرای مستقیم با Gemini پشتیبانی نمی‌شود")


@app.post("/api/projects/{episode_id}/upload/scene_video")
async def upload_scene_video(
    episode_id: str,
    scene_id: str = Form(...),
    file: UploadFile = File(...)
):
    project_path = get_project_path(episode_id)
    target_dir = project_path / "scenes"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    clean_name = file.filename.replace(" ", "_")
    safe_filename = f"video_{scene_id}_{clean_name}"
    file_path = target_dir / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    relative_url = f"/media/{episode_id}/scenes/{safe_filename}"
    
    state = load_state(episode_id)
    scenes = state.get("scenes", [])
    found = False
    for sc in scenes:
        if sc.get("id") == scene_id or sc.get("scene_id") == scene_id:
            sc["video_path"] = relative_url
            sc["video_asset"] = relative_url
            found = True
            break
            
    if found:
        save_state(episode_id, state)
        
    return {
        "status": "success",
        "scene_id": scene_id,
        "video_url": relative_url,
        "filename": safe_filename,
        "state": state
    }


# ==========================================
# SKILLS & SUBTITLES / FFMPEG PREVIEWS
# ==========================================

@app.get("/api/skills")
def list_skills():
    skills = []
    for item in sorted(SKILLS_DIR.iterdir()):
        if item.is_file() and item.name.endswith(".md"):
            with open(item, "r", encoding="utf-8") as f:
                content = f.read()
            first_line = content.split("\n")[0].replace("#", "").strip() if content else item.name
            skills.append({
                "filename": item.name,
                "title": first_line,
                "size": item.stat().st_size
            })
    return {"skills": skills}


@app.get("/api/skills/{skill_name}")
def get_skill_content(skill_name: str):
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


# Mount frontend dist static files at the end
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
