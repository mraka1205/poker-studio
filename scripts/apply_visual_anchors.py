"""Idempotently write canonical visual anchors into projects/universe.json.  Usage: python scripts/apply_visual_anchors.py [--dry-run]"""
import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.services.paths import projects_dir
from backend.services.state_store import write_json_atomic
from backend.services.visual_canon import SEED_CHARACTERS, SEED_ENV_CANON

VERSION = "1.0"
CHAR_KEYS = ("dna_block_en", "short_look_en", "acting_beats_en")


def apply(universe: dict):
    changes = []
    env = universe.setdefault("environment", {})
    if env.get("canon_en") != SEED_ENV_CANON:
        env["canon_en"] = copy.deepcopy(SEED_ENV_CANON)
        changes.append("environment.canon_en set")
    for c in universe.get("characters", []):
        seed = SEED_CHARACTERS.get(c.get("flow_tag"))
        if not seed:
            continue
        for k in CHAR_KEYS:
            if c.get(k) != seed[k]:
                changes.append(f"{c['flow_tag']}: {k} updated (old: {str(c.get(k))[:90]!r})")
                c[k] = copy.deepcopy(seed[k])
    if changes or universe.get("visual_canon_version") != VERSION:
        universe["visual_canon_version"] = VERSION
    return universe, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    path = projects_dir() / "universe.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data, changes = apply(data)
    for ch in changes:
        print("CHANGE", ch)
    missing = [t for t in SEED_CHARACTERS if t not in {c.get("flow_tag") for c in data.get("characters", [])}]
    for t in missing:
        print("NOTE  seed character not in universe.json:", t)
    if changes and not args.dry_run:
        bak = path.with_name("universe.json.visual.bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        write_json_atomic(path, data)
        print("Wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
