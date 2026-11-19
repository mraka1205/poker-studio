"""Build final image prompts.  Usage: python scripts/build_scene_prompts.py <episode_id> [--scene scene_03] [--check] [--print]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.services.paths import get_project_dir
from backend.services.scene_prompt_builder import build_episode_prompts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode_id")
    ap.add_argument("--scene")
    ap.add_argument("--check", action="store_true", help="validate only, do not write")
    ap.add_argument("--print", dest="show", action="store_true")
    a = ap.parse_args()
    res = build_episode_prompts(a.episode_id, scene_id=a.scene, write=not a.check)
    for w in res["warnings"]:
        print("WARN ", w)
    for e in res["errors"]:
        print("ERROR", e)
    if a.show:
        for sid, p in res["prompts"].items():
            print(f"\n=== {sid} ({len(p.split())} words) ===\n{p}")
    if res["errors"]:
        return 1
    if a.check and not (get_project_dir(a.episode_id) / "assets" / "image_batch.json").exists():
        print("ERROR assets/image_batch.json is missing; run without --check first")
        return 1
    print(f"OK built={len(res['built'])} batch={res['batch_file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
