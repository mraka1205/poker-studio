"""Usage: python scripts/verify_frames.py <episode_id>   (exit 1 when any ERROR)"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageStat

from backend.services.paths import get_project_dir
from backend.services.state_store import read_state, write_json_atomic

MIN_BYTES = 50 * 1024
ASPECT = 9 / 16
FELT_SHOTS = {"wide_master", "topdown_pot", "chips_macro", "ots_duel", "medium_seat"}


def _small(img: Image.Image) -> Image.Image:
    return img.convert("RGB").resize((64, 112))


def _pixels(img: Image.Image):
    return img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()


def histogram(img: Image.Image) -> List[float]:
    h = [0] * 512
    for r, g, b in _pixels(_small(img)):
        h[(r >> 5) * 64 + (g >> 5) * 8 + (b >> 5)] += 1
    n = float(sum(h))
    return [x / n for x in h]


def intersection(a: List[float], b: List[float]) -> float:
    return sum(min(x, y) for x, y in zip(a, b))


def felt_fraction(img: Image.Image) -> float:
    px = list(_pixels(_small(img)))
    return sum(1 for r, g, b in px if g > 60 and g > r * 1.2 and g > b * 1.1) / len(px)


def check_image(path: Path, shot_type: Optional[str], master_hist: Optional[List[float]], min_bytes: int = MIN_BYTES) -> Dict[str, Any]:
    out = {"file": path.name, "errors": [], "warnings": []}
    if not path.exists():
        out["errors"].append("file missing")
        return out
    if path.stat().st_size < min_bytes:
        out["errors"].append(f"file smaller than {min_bytes // 1024} KB")
    img = Image.open(path)
    w, h = img.size
    if abs(w / h - ASPECT) > 0.01:
        out["errors"].append(f"aspect ratio {w}x{h} is not 9:16")
    if w < 720:
        out["warnings"].append(f"width {w}px < 720px (Ken Burns zoom will look soft)")
    if sum(ImageStat.Stat(img.convert("L")).stddev) < 8:
        out["errors"].append("image is nearly uniform (blank or failed generation)")
    if shot_type in FELT_SHOTS and felt_fraction(img) < 0.02:
        out["warnings"].append("almost no green felt visible")
    if master_hist is not None:
        sim = intersection(histogram(img), master_hist)
        out["palette_similarity"] = round(sim, 3)
        if sim < 0.35:
            out["warnings"].append(f"palette differs strongly from master frame (similarity {sim:.2f})")
    return out


def main() -> int:
    ep = sys.argv[1]
    scenes = read_state(ep).get("scenes", [])
    img_dir = get_project_dir(ep) / "assets" / "images"
    ids = [s.get("scene_id") or s.get("id") for s in scenes]
    master_path = img_dir / f"{ids[0]}.png" if ids else None
    master_hist = histogram(Image.open(master_path)) if master_path and master_path.exists() else None
    report = []
    for s, sid in zip(scenes, ids):
        shot = (s.get("scene_spec") or {}).get("shot_type")
        report.append({"scene_id": sid, **check_image(img_dir / f"{sid}.png", shot, None if sid == ids[0] else master_hist)})
    write_json_atomic(get_project_dir(ep) / "assets" / "frame_report.json", report)
    errs = sum(len(r["errors"]) for r in report)
    warns = sum(len(r["warnings"]) for r in report)
    for r in report:
        for e in r["errors"]:
            print("ERROR", r["scene_id"], e)
        for w in r["warnings"]:
            print("WARN ", r["scene_id"], w)
    print(f"SUMMARY frames={len(report)} errors={errs} warnings={warns}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
