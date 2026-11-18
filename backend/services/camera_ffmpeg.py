from typing import Any, Dict, List, Optional

from backend.services.scene_schema import MOTION_TYPES


def build_zoompan_filter(camera_direction: Optional[Dict[str, Any]], duration_sec: float,
                         fps: int = 30, out_w: int = 1080, out_h: int = 1920) -> str:
    """Return an ffmpeg -vf string (wrap it in double quotes in a shell)."""
    cd = camera_direction or {}
    motion = cd.get("motion_type")
    if motion not in MOTION_TYPES:
        motion = "static_hold"
    try:
        zi = float(cd.get("zoom_intensity", 1.15))
    except (TypeError, ValueError):
        zi = 1.15
    zi = max(1.0, min(zi, 1.6))
    zp = max(zi, 1.1)  # pans/tilts need some zoom headroom
    n = max(1, int(round(float(duration_sec) * fps)))
    d = max(n - 1, 1)
    easing = cd.get("easing") or ("dramatic_punch" if motion == "fast_punch_in" else "smooth")
    p = f"pow(on/{d},3)" if easing == "dramatic_punch" else f"(on/{d})"
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    if motion in ("slow_zoom_in", "fast_punch_in"):
        z, x, y = f"1+({zi}-1)*{p}", cx, cy
    elif motion == "slow_zoom_out":
        z, x, y = f"{zi}-({zi}-1)*{p}", cx, cy
    elif motion == "pan_left_to_right":
        z, x, y = f"{zp}", f"(iw-iw/zoom)*{p}", cy
    elif motion == "pan_right_to_left":
        z, x, y = f"{zp}", f"(iw-iw/zoom)*(1-{p})", cy
    elif motion == "tilt_up":
        z, x, y = f"{zp}", cx, f"(ih-ih/zoom)*(1-{p})"
    elif motion == "tilt_down":
        z, x, y = f"{zp}", cx, f"(ih-ih/zoom)*{p}"
    elif motion == "subtle_tilt_shake":
        z, x, y = "1.06", f"{cx}+8*sin(on*0.9)", f"{cy}+8*cos(on*1.3)"
    else:  # static_hold
        z, x, y = "1", cx, cy

    return (f"scale={out_w * 2}:{out_h * 2}:force_original_aspect_ratio=increase,"
            f"crop={out_w * 2}:{out_h * 2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={out_w}x{out_h}:fps={fps},format=yuv420p")


def build_scene_clip_command(image_path: str, out_path: str, camera_direction: Optional[Dict[str, Any]],
                             duration_sec: float, fps: int = 30) -> List[str]:
    vf = build_zoompan_filter(camera_direction, duration_sec, fps)
    return ["ffmpeg", "-y", "-i", image_path, "-vf", vf, "-t", f"{float(duration_sec):.3f}",
            "-r", str(fps), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", out_path]
