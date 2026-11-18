import pytest
from backend.services.camera_ffmpeg import build_zoompan_filter, build_scene_clip_command
from backend.services.scene_schema import MOTION_TYPES


@pytest.mark.parametrize("motion", sorted(MOTION_TYPES))
def test_every_motion_type_builds(motion):
    vf = build_zoompan_filter({"motion_type": motion, "zoom_intensity": 1.2}, 2.0)
    assert "zoompan=" in vf and ":d=60:" in vf and vf.endswith("format=yuv420p")


def test_unknown_motion_falls_back_and_zoom_is_clamped():
    assert "z='1'" in build_zoompan_filter({"motion_type": "nope"}, 2.0)
    assert "1.6-" in build_zoompan_filter({"motion_type": "slow_zoom_out", "zoom_intensity": 9}, 1.0)


def test_command_shape():
    cmd = build_scene_clip_command("a.png", "o.mp4", None, 2.5)
    assert cmd[0] == "ffmpeg" and "-t" in cmd and cmd[-1] == "o.mp4"
