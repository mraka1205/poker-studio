import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.services import table_state as ts
from backend.services.paths import get_project_dir, projects_dir, validate_scene_id
from backend.services.prompt_assembler import SpecError, assemble_scene_prompt
from backend.services.prompt_lint import lint_prompt, lint_sequence
from backend.services.seat_geometry import RosterError, merge_roster
from backend.services.state_store import read_state, update_state, write_json_atomic


def _disk(url: Optional[str]) -> Optional[Path]:
    if not url or not str(url).startswith("/media/"):
        return None
    return projects_dir() / str(url)[len("/media/"):]


def _sid(scene: Dict[str, Any], i: int) -> str:
    return scene.get("scene_id") or scene.get("id") or f"scene_{i + 1:02d}"


def _blueprint(meta: Dict[str, Any], roster: Dict[str, Any]) -> Dict[str, Any]:
    snap = meta["snapshot"]
    if not snap:
        return {"community_cards": {"stage": "preflop", "cards": [], "layout": ""},
                "pot": {"total_bb": 0, "visual": "", "position": "center of the table"}, "player_zones": {}}
    zones = {}
    for seat in meta["visible_seats"]:
        if seat in roster and seat in snap["stacks_bb"]:
            zones[seat] = {"character": roster[seat]["flow_tag"],
                           "chip_stack": ts.stack_clause(snap["stacks_bb"][seat], snap["start_stacks_bb"][seat],
                                                         seat in snap["all_in"], seat in snap["folded"])}
    return {"community_cards": {"stage": snap["stage"], "cards": snap["board"], "layout": ts.board_clause(snap["board"], snap["stage"])},
            "pot": {"total_bb": snap["pot_bb"], "visual": ts.pot_tier(snap["pot_bb"]), "position": "center of the table"},
            "player_zones": zones}


def build_episode_prompts(episode_id: str, scene_id: Optional[str] = None, write: bool = True) -> Dict[str, Any]:
    res: Dict[str, Any] = {"status": "ok", "errors": [], "warnings": [], "built": [], "prompts": {}, "batch_file": None}

    def fail(msgs: List[str]) -> Dict[str, Any]:
        res["status"] = "error"
        res["errors"].extend(msgs)
        return res

    try:
        state = read_state(episode_id)
        universe = json.loads((projects_dir() / "universe.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return fail([f"Cannot load state.json / universe.json: {exc}"])
    scenes = state.get("scenes") or []
    if not scenes:
        return fail(["state.json has no scenes[]"])
    ids = [_sid(s, i) for i, s in enumerate(scenes)]
    if scene_id:
        validate_scene_id(scene_id)
        if scene_id not in ids:
            return fail([f"scene {scene_id} not found"])
    try:
        roster = merge_roster(state.get("characters"), universe.get("characters"))
        snaps = ts.compute_timeline(state["hand_timeline"]) if state.get("hand_timeline") else None
    except (RosterError, ts.TimelineError) as exc:
        return fail([str(exc)])
    specs = [s.get("scene_spec") for s in scenes]
    missing = [ids[i] for i, sp in enumerate(specs) if not isinstance(sp, dict)]
    if missing:
        return fail([f"{m}: scene_spec missing" for m in missing])
    res["errors"].extend(lint_sequence(specs))

    master_url = f"/media/{episode_id}/assets/images/{ids[0]}.png"

    def exists(p: str) -> bool:
        if p == master_url:
            return True  # planned: scene_01 is generated first
        d = _disk(p)
        return bool(d and d.exists())

    built: Dict[str, Dict[str, Any]] = {}
    for i, sc in enumerate(scenes):
        sid = ids[i]
        if scene_id and sid != scene_id:
            continue
        ctx = {"universe": universe, "roster": roster, "snapshots": snaps, "scene_index": i,
               "master_path": master_url, "path_exists": exists}
        try:
            out = assemble_scene_prompt(sc["scene_spec"], ctx)
        except SpecError as exc:
            res["errors"].append(f"{sid}: {exc}")
            continue
        for msg in lint_prompt(out["image_prompt_en"], out["required_substrings"]):
            res["errors"].append(f"{sid}: {msg}")
        res["warnings"].extend(f"{sid}: {w}" for w in out["warnings"])
        meta = out["meta"]
        snap = meta["snapshot"]
        visible_tags = [roster[s]["flow_tag"] for s in meta["visible_seats"] if s in roster]
        built[sid] = {"out": out, "fields": {
            "image_prompt_en": out["image_prompt_en"], "visual_prompt_en": out["image_prompt_en"],
            "image_references": out["references"], "prompt_warnings": out["warnings"],
            "camera_angle": f"{meta['camera_angle_tag']} {meta['shot_type']}", "focal_character": meta["focal"],
            "characters_present": visible_tags, "adjacent_players": meta["neighbors"],
            "table_state_en": meta["table_clause"], "table_blueprint": _blueprint(meta, roster),
            "poker_table_state": {"board": snap["board"] if snap else [], "pot_bb": snap["pot_bb"] if snap else 0,
                                  "action_badge": snap["label"] if snap else ""},
        }}
    if res["errors"]:
        res["status"] = "error"
        return res
    res["built"] = list(built)
    res["prompts"] = {sid: b["out"]["image_prompt_en"] for sid, b in built.items()}
    if not write:
        return res

    def entry(sid: str, out: Dict[str, Any]) -> Dict[str, Any]:
        return {"scene_id": sid, "ImageName": sid, "AspectRatio": "9:16",
                "ImagePaths": [_disk(r["path"]).resolve().as_posix() for r in out["references"]],
                "Prompt": out["image_prompt_en"]}

    def mutate(st: Dict[str, Any]) -> None:
        for i, sc in enumerate(st.get("scenes", [])):
            sid = _sid(sc, i)
            if sid in built:
                sc.update(built[sid]["fields"])

    update_state(episode_id, mutate)
    assets = get_project_dir(episode_id) / "assets"
    if scene_id:
        batch = assets / "image_batch_single.json"
        write_json_atomic(batch, [entry(scene_id, built[scene_id]["out"])])
    else:
        batch = assets / "image_batch.json"
        write_json_atomic(batch, [entry(sid, built[sid]["out"]) for sid in ids])
    res["batch_file"] = str(batch)
    return res
