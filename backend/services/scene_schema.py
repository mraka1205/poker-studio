import re
from typing import Any, Dict, List

ALLOWED_MEDIA_TYPES = {"static_image", "ai_video"}
MOTION_TYPES = {
    "slow_zoom_in", "fast_punch_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left",
    "tilt_up", "tilt_down", "subtle_tilt_shake", "static_hold",
}
STAGES = {"preflop", "flop", "turn", "river"}
SCENE_ID_RE = re.compile(r"^scene_\d{2,3}$")
_FLAG_RE = re.compile(r"\s--[a-zA-Z]+(?:\s+[0-9.:]+)?")
MIN_WORDS, MAX_WORDS = 80, 220


def strip_flags(text: str) -> str:
    return _FLAG_RE.sub("", text or "").strip()


def normalize_scene(scene: Dict[str, Any], index: int, episode_id: str) -> Dict[str, Any]:
    s = dict(scene)
    sid = s.get("scene_id") or s.get("id") or f"scene_{index + 1:02d}"
    s["scene_id"] = sid
    s["id"] = sid
    s.setdefault("beat_index", index + 1)
    if s.get("media_type") not in ALLOWED_MEDIA_TYPES:
        s["media_type"] = "ai_video" if s.get("shot_mode") == "ai_video" else "static_image"
    s["motion_prompt_en"] = strip_flags(s.get("motion_prompt_en") or "")
    if not isinstance(s.get("duration_sec"), (int, float)):
        try:
            s["duration_sec"] = float(s.get("target_video_sec") or 2.0)
        except (TypeError, ValueError):
            s["duration_sec"] = 2.0
    s.setdefault("image_path", f"/media/{episode_id}/assets/images/{sid}.png")
    s.setdefault("visual_asset", s["image_path"])
    return s


def validate_scenes(scenes: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    if not isinstance(scenes, list) or not scenes:
        return ["scenes must be a non-empty list"]
    seen = set()
    for i, s in enumerate(scenes):
        sid = s.get("scene_id")
        tag = f"[{sid or i}]"
        if not isinstance(sid, str) or not SCENE_ID_RE.fullmatch(sid):
            errors.append(f"{tag} scene_id must match scene_NN")
        elif sid in seen:
            errors.append(f"{tag} duplicate scene_id")
        seen.add(sid)
        prompt = s.get("visual_prompt_en") or ""
        words = len(prompt.split())
        if words < MIN_WORDS or words > MAX_WORDS:
            errors.append(f"{tag} visual_prompt_en has {words} words (need {MIN_WORDS}-{MAX_WORDS})")
        if "9:16" not in prompt:
            errors.append(f"{tag} visual_prompt_en must mention 9:16")
        if i > 0 and "maintain exact visual continuity" not in prompt.lower():
            errors.append(f"{tag} visual_prompt_en must start the continuity lock (scene 2+)")
        dur = s.get("duration_sec")
        if not isinstance(dur, (int, float)) or not 0.5 <= dur <= 8:
            errors.append(f"{tag} duration_sec must be a number in [0.5, 8]")
        media = s.get("media_type")
        if media == "static_image":
            cd = s.get("camera_direction")
            if not isinstance(cd, dict):
                errors.append(f"{tag} static_image requires camera_direction object")
            else:
                if cd.get("motion_type") not in MOTION_TYPES:
                    errors.append(f"{tag} camera_direction.motion_type invalid")
                zi = cd.get("zoom_intensity")
                if not isinstance(zi, (int, float)) or not 1.0 <= zi <= 1.6:
                    errors.append(f"{tag} camera_direction.zoom_intensity must be in [1.0, 1.6]")
                if not (cd.get("camera_prompt_en") or "").strip():
                    errors.append(f"{tag} camera_direction.camera_prompt_en is empty")
        elif media == "ai_video":
            mp = (s.get("motion_prompt_en") or "")
            if not mp.strip():
                errors.append(f"{tag} ai_video requires motion_prompt_en")
            elif "mouth closed" not in mp.lower():
                errors.append(f"{tag} motion_prompt_en must contain 'mouth closed' (silent acting)")
        else:
            errors.append(f"{tag} media_type must be static_image or ai_video")
        tb = s.get("table_blueprint")
        if not isinstance(tb, dict):
            errors.append(f"{tag} table_blueprint object is required")
        else:
            if (tb.get("community_cards") or {}).get("stage") not in STAGES:
                errors.append(f"{tag} table_blueprint.community_cards.stage invalid")
            if not isinstance((tb.get("pot") or {}).get("total_bb"), (int, float)):
                errors.append(f"{tag} table_blueprint.pot.total_bb must be a number")
        if not (s.get("sfx_cue") or "").strip():
            errors.append(f"{tag} sfx_cue is required")
    return errors
