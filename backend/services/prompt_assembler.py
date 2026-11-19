"""scene_spec + universe + table snapshots -> final image prompt (deterministic)."""
from typing import Any, Callable, Dict, List, Optional

from backend.services import table_state as ts
from backend.services import visual_canon as vc
from backend.services.seat_geometry import SEAT_ORDER, frame_neighbors

MAX_REFS = 4
SOFT_MAX_WORDS = 350
REF_TEXT = {
    "angle": "angle and set (copy room and props, not framing)",
    "face": "{name} face sheet (copy face exactly)",
    "body": "{name} body sheet (copy wardrobe and proportions exactly)",
    "master": "master frame (copy felt, chips, lamp, palette only)",
}


class SpecError(ValueError):
    pass


def plain(tag: Any) -> str:
    return str(tag or "").lstrip("@")


def _s(text: str) -> str:
    t = " ".join(str(text).split()).strip()
    return t if t[-1:] in ".!?" else t + "."


def validate_spec(spec: Any) -> List[str]:
    if not isinstance(spec, dict):
        return ["scene_spec must be an object"]
    errors: List[str] = []
    shot = spec.get("shot_type")
    if shot not in vc.SHOT_LIBRARY:
        errors.append(f"shot_type {shot!r} not in {sorted(vc.SHOT_LIBRARY)}")
    else:
        mode = vc.SHOT_LIBRARY[shot]["mode"]
        if mode in ("single", "props", "duel") and not spec.get("focal"):
            errors.append(f"focal is required for shot_type {shot}")
        if mode == "duel" and not spec.get("ots_from"):
            errors.append("ots_from is required for ots_duel")
    emo = spec.get("emotion", "neutral")
    if vc.EMOTION_ALIASES.get(emo, emo) not in vc.EMOTION_KEYS:
        errors.append(f"emotion {emo!r} invalid; use one of {list(vc.EMOTION_KEYS)}")
    if spec.get("mood") is not None and spec["mood"] not in vc.LIGHTING_MOODS:
        errors.append(f"mood {spec['mood']!r} invalid; use one of {sorted(vc.LIGHTING_MOODS)}")
    return errors


def _char(roster: Dict[str, Dict[str, Any]], tag: str) -> Dict[str, Any]:
    for rec in roster.values():
        if rec.get("flow_tag") == tag:
            return rec
    raise SpecError(f"{tag} is not seated in this episode (sync characters first)")


def _dna(rec: Dict[str, Any]) -> str:
    d = (rec.get("dna_block_en") or "").strip().rstrip(".")
    if not d:
        raise SpecError(f"{rec.get('flow_tag')} has no dna_block_en; run scripts/apply_visual_anchors.py")
    return d


def _look(rec: Dict[str, Any], warnings: List[str]) -> str:
    look = (rec.get("short_look_en") or "").strip()
    if not look:
        warnings.append(f"{rec.get('flow_tag')} has no short_look_en")
        return "its usual outfit"
    return look


def _acting(rec: Dict[str, Any], emotion: str, extra: Optional[str]) -> str:
    key = vc.EMOTION_ALIASES.get(emotion, emotion)
    beats = rec.get("acting_beats_en") or {}
    text = beats.get(key) or beats.get("neutral") or "sits calmly at the table"
    return f"{text}, and {extra.strip().rstrip('.')}" if extra else text


def assemble_scene_prompt(spec: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    errs = validate_spec(spec)
    if errs:
        raise SpecError("; ".join(errs))
    universe, roster = ctx["universe"], ctx["roster"]
    exists: Callable[[str], bool] = ctx.get("path_exists") or (lambda p: bool(p))
    env_all = universe.get("environment", {})
    env = env_all.get("canon_en")
    if not env:
        raise SpecError("universe.environment.canon_en missing; run scripts/apply_visual_anchors.py")
    angles = {a.get("id"): a for a in env_all.get("camera_angles", [])}
    shot_key = spec["shot_type"]
    shot = vc.SHOT_LIBRARY[shot_key]
    mode = shot["mode"]
    warnings: List[str] = []
    focal = _char(roster, spec["focal"]) if spec.get("focal") else None
    other = _char(roster, spec["ots_from"]) if mode == "duel" else None
    angle_id = spec.get("camera_angle_id") or (focal["seat"] if shot["angle"] == "seat" else shot["angle"])
    angle = angles.get(angle_id)
    if angle is None:
        raise SpecError(f"camera angle {angle_id!r} not found in universe.environment.camera_angles")
    landmarks = (angle.get("background_landmarks_en") or "").strip().rstrip(".")
    emotion = spec.get("emotion", "neutral")
    emo_key = vc.EMOTION_ALIASES.get(emotion, emotion)
    acting = _acting(focal, emotion, spec.get("extra_action_en")) if focal else ""

    visible: List[str] = []
    neighbor_lines: List[str] = []
    neighbor_meta: List[str] = []
    required: List[str] = []
    fname = plain(focal["flow_tag"]) if focal else ""

    if mode == "single":
        dna = _dna(focal)
        required.append(dna)
        subject = f"{fname} is a {dna}. {fname} {_s(acting)}"
        visible = [focal["seat"]]
        if shot["neighbors"]:
            nb = frame_neighbors(focal["seat"])
            for side in ("left", "right"):
                seat = nb[side]
                rec = roster.get(seat)
                if rec:
                    neighbor_lines.append(f"{side.capitalize()} edge of the frame: the soft out-of-focus shoulder of "
                                          f"{plain(rec['flow_tag'])} in {_look(rec, warnings)}.")
                    visible.append(seat)
                else:
                    neighbor_lines.append(f"{side.capitalize()} edge of the frame: an empty dark leather chair.")
                neighbor_meta.append(f"{rec['flow_tag'] if rec else 'empty'} ({seat}, {side} edge)")
    elif mode == "props":
        subject = f"Behind the chips, {fname} in {_look(focal, warnings)} is softly blurred. {fname} {_s(acting)}"
        visible = [focal["seat"]]
    elif mode == "duel":
        dna = _dna(focal)
        required.append(dna)
        subject = (f"Foreground: the dark slightly blurred shoulder and hand of {plain(other['flow_tag'])} in "
                   f"{_look(other, warnings)}. Sharp focus across the table: {fname} is a {dna}. {fname} {_s(acting)}")
        visible = [focal["seat"], other["seat"]]
    elif mode == "wide":
        seated = [f"{plain(roster[s]['flow_tag'])} at {s.replace('_', ' ')} in {_look(roster[s], warnings)}"
                  for s in SEAT_ORDER if s in roster]
        empty = [s.replace("_", " ") for s in SEAT_ORDER if s not in roster]
        subject = "Seated around the table: " + "; ".join(seated) + "."
        if empty:
            subject += " Empty dark leather chairs at: " + ", ".join(empty) + "."
        if focal:
            subject += f" {fname} {_s(acting)}"
        visible = [s for s in SEAT_ORDER if s in roster]
    else:  # topdown
        subject = "Only felt-wool hands of the players reach in from the table edge; no faces are visible."
        visible = [s for s in SEAT_ORDER if s in roster]

    snaps = ctx.get("snapshots")
    snap = None
    step = spec.get("timeline_step")
    if snaps:
        if isinstance(step, int) and 0 <= step < len(snaps):
            snap = snaps[step]
        elif isinstance(step, str):
            snap = next((x for x in snaps if x["id"] == step), None)
    if snap:
        table_clause = ts.render_table_clause(snap, visible, roster)
    else:
        warnings.append("no table snapshot for this scene (missing hand_timeline or timeline_step)")
        table_clause = "The felt shows a few scattered chips and no community cards."

    chips = env["chips_en"]
    if shot_key == "reaction_insert":
        setting = f"Behind the subject: {landmarks}."
    elif mode == "single":
        setting = f"Behind the subject: {landmarks}. Foreground: {env['table_short_en']}."
    elif mode == "props":
        setting = f"{env['table_short_en']}; background: {landmarks}. {chips}."
    elif mode == "wide":
        setting = f"The room has {env['room_en']}, with {env['lamp_en']}. The table is {env['table_en']}. {chips}."
    elif mode == "topdown":
        setting = f"The table is {env['table_en']}. {chips}."
    else:
        setting = f"Behind the focal puppet: {env['room_en']}. Table: {env['table_short_en']}. {chips}."

    mood = spec.get("mood") or vc.DEFAULT_MOOD_FOR_EMOTION[emo_key]
    lighting = vc.LIGHTING_MOODS[mood]

    # ---- references (priority order, capped) ----
    def face(rec): return ("face", rec.get("face_sheet_image_path"), REF_TEXT["face"].format(name=plain(rec["flow_tag"])))
    def body(rec): return ("body", rec.get("body_sheet_image_path") or rec.get("reference_image_path"),
                           REF_TEXT["body"].format(name=plain(rec["flow_tag"])))
    cands = [("angle", angle.get("reference_image_path"), REF_TEXT["angle"])]
    master = ("master", ctx.get("master_path"), REF_TEXT["master"]) if ctx.get("master_path") and ctx.get("scene_index", 0) > 0 else None
    if mode == "wide":
        if master:
            cands.append(master)
        cands += [body(roster[s]) for s in SEAT_ORDER if s in roster]
    else:
        if mode == "single":
            if shot_key in ("closeup_seat", "reaction_insert", "low_angle_hero"):
                cands.append(face(focal))
            cands.append(body(focal))
        elif mode == "props":
            cands.append(body(focal))
        elif mode == "duel":
            cands += [body(focal), body(other)]
        if master:
            cands.append(master)
    refs: List[Dict[str, str]] = []
    for role, path, text in cands:
        if path and exists(path):
            refs.append({"role": role, "path": path, "text": text})
        else:
            warnings.append(f"missing reference image for {role}: {path!r}")
    refs = refs[:MAX_REFS]
    preamble = "References: " + " ".join(f"Image {i} = {r['text']}." for i, r in enumerate(refs, 1)) if refs else ""

    parts = [preamble, f"Generate a {shot['framing']}, {shot['lens']}.", subject] + neighbor_lines + [
        table_clause, setting, lighting, vc.STYLE_LOCK, vc.COMPOSITION_RULE, vc.NEGATIVE_BLOCK]
    prompt = " ".join(_s(p) for p in parts if p)
    words = len(prompt.split())
    if words > SOFT_MAX_WORDS:
        warnings.append(f"prompt has {words} words (> {SOFT_MAX_WORDS}); dilution risk")
    return {
        "image_prompt_en": prompt, "word_count": words, "references": [{"role": r["role"], "path": r["path"]} for r in refs],
        "warnings": warnings, "required_substrings": required + [vc.STYLE_LOCK, vc.NEGATIVE_BLOCK],
        "meta": {"shot_type": shot_key, "camera_angle_id": angle_id, "camera_angle_tag": angle.get("flow_tag") or f"@{angle_id}",
                 "visible_seats": visible, "neighbors": neighbor_meta, "table_clause": table_clause, "snapshot": snap,
                 "lighting": lighting, "focal": spec.get("focal")},
    }
