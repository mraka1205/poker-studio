"""Idempotent repair of projects/universe.json.  Usage: python scripts/repair_universe.py [--dry-run]"""
import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.services.paths import projects_dir
from backend.services.state_store import write_json_atomic

TABLET = "Holding a tiny miniature electronic tablet prop with poker ranges in one felted hand."
NOTEBOOK = "Holding a small crumpled pocket notebook and a chewed pen in one hand (no tablets or high-tech gadgets)."
MEDIA_KEYS = ("reference_image_path", "face_sheet_image_path", "body_sheet_image_path")


def _is_placeholder(value) -> bool:
    return (not isinstance(value, str)) or (not value.strip()) or "..." in value or "…" in value


def repair(universe: dict):
    notes = []
    chars = universe.get("characters", [])
    for c in chars:
        cid = c.get("id")
        for key, val in list(c.items()):
            if isinstance(val, str) and TABLET in val:
                c[key] = val.replace(TABLET, NOTEBOOK)
                notes.append(f"{cid}: replaced tablet sentence in {key}")
        persona = c.get("persona_behavior_prompt")
        if isinstance(persona, str) and persona.strip() and c.get("personality_and_catchphrases_fa") != persona and _is_placeholder(c.get("personality_and_catchphrases_fa")):
            c["personality_and_catchphrases_fa"] = persona
            notes.append(f"{cid}: personality_and_catchphrases_fa <- persona_behavior_prompt")
        if c.get("visual_prompt_en") != c.get("full_body_prompt_en") and _is_placeholder(c.get("visual_prompt_en")) and c.get("full_body_prompt_en"):
            c["visual_prompt_en"] = c["full_body_prompt_en"]
            notes.append(f"{cid}: visual_prompt_en <- full_body_prompt_en")
    if chars and not any(c.get("is_style_anchor") for c in chars):
        chars[0]["is_style_anchor"] = True
        notes.append(f"{chars[0].get('id')}: set as style anchor")
    return universe, notes


def audit(universe: dict, root: Optional[Path] = None) -> list:
    if root is None:
        root = projects_dir()
    problems = []
    tags = [c.get("flow_tag") for c in universe.get("characters", [])]
    for t in set(tags):
        if tags.count(t) > 1:
            problems.append(f"duplicate flow_tag: {t}")
    paths = []
    env = universe.get("environment", {})
    paths.append(("environment", env.get("reference_image_path")))
    for a in env.get("camera_angles", []):
        paths.append((a.get("id"), a.get("reference_image_path")))
    for c in universe.get("characters", []):
        for k in MEDIA_KEYS:
            paths.append((f"{c.get('id')}.{k}", c.get(k)))
    for owner, p in paths:
        if not p:
            continue
        rel = p.replace("/media/universe/", "")
        if "…" in rel:
            problems.append(f"{owner}: filename contains '…' (rename file): {rel}")
        target = root / "universe" / rel if (root.name == "projects" or (root / "universe").exists()) else root / "projects" / "universe" / rel
        if not target.exists():
            problems.append(f"{owner}: missing file projects/universe/{rel}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    path = projects_dir() / "universe.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data, notes = repair(data)
    for n in notes:
        print("FIX  ", n)
    problems = audit(data, projects_dir())
    for p in problems:
        print("AUDIT", p)
    if not args.dry_run and notes:
        bak = path.with_name("universe.json.bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        write_json_atomic(path, data)
        print(f"Wrote {path}")
    return 2 if any("duplicate flow_tag" in p for p in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
