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


def test_render_ffmpeg_preview_endpoint():
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services.state_store import write_state
    from backend.services.paths import projects_dir

    client = TestClient(app)
    ep_id = "ep99-ffmpeg-test"
    (projects_dir() / ep_id / "exports").mkdir(parents=True, exist_ok=True)
    state = {
        "episode_id": ep_id,
        "title": "FFmpeg Test",
        "edit": {
            "subtitle_settings": {
                "font": "Vazirmatn",
                "font_size": 42
            }
        },
        "scenes": [
            {
                "id": "scene_01",
                "scene_id": "scene_01",
                "media_type": "static_image",
                "duration_sec": 2.0,
                "camera_direction": {"motion_type": "slow_zoom_in", "zoom_intensity": 1.2}
            },
            {
                "id": "scene_02",
                "scene_id": "scene_02",
                "media_type": "ai_video",
                "duration_sec": 3.0,
                "motion_prompt_en": "silent acting (mouth closed)"
            }
        ]
    }
    write_state(ep_id, state)

    res = client.post(f"/api/projects/{ep_id}/render_ffmpeg_preview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "ready"
    assert "ffmpeg_command" in data
    assert "scene_clip_commands" in data
    # Only scene_01 is static_image
    assert len(data["scene_clip_commands"]) == 1
    clip_01 = data["scene_clip_commands"][0]
    assert clip_01["scene_id"] == "scene_01"
    assert "ffmpeg" in clip_01["command"]
    assert "zoompan" in clip_01["command"]

