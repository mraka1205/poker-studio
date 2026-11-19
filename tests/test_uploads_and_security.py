import io
import json
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app, _sanitize_token, load_state, get_skill_content, _default_universe
from backend.services.paths import projects_dir
from backend.services.state_store import compute_etag, read_state, write_state


@pytest.fixture
def client():
    return TestClient(app)


def _create_test_episode(ep_id="ep98-upload-test"):
    ep_dir = projects_dir() / ep_id
    ep_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "episode_id": ep_id,
        "title": "Upload Test Episode",
        "scenes": [
            {
                "id": "scene_01",
                "scene_id": "scene_01",
                "title": "Intro Scene",
                "image_path": "",
                "visual_asset": "",
                "video_path": "",
                "shot_mode": "static_zoom",
                "media_type": "static_image",
            }
        ],
        "script": {"segments": []},
    }
    write_state(ep_id, state)
    return ep_id, ep_dir


def test_sanitize_token():
    assert _sanitize_token(None) == ""
    assert _sanitize_token("") == ""
    assert _sanitize_token("valid_token-123") == "valid_token-123"
    assert _sanitize_token("  trimmed_id  ") == "trimmed_id"

    for bad in ["   ", "id with spaces", "../traversal", "a/b", "a\\b", "bad$char"]:
        with pytest.raises(HTTPException) as exc_info:
            _sanitize_token(bad)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid identifier"


def test_get_skill_content_security(client):
    for bad in ["../secret", "..\\secret", "folder/skill", "folder\\skill", ".."]:
        with pytest.raises(HTTPException) as exc_info:
            get_skill_content(bad)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid skill name"

    res_traversal1 = client.get("/api/skills/..%2Fsecret")
    assert res_traversal1.status_code in (400, 404)

    res_slash = client.get("/api/skills/sub%2Ftest")
    assert res_slash.status_code in (400, 404)


def test_upload_universe_asset_security_and_flow(client):
    # Bad asset type
    res_bad_type = client.post(
        "/api/universe/upload/invalid_type",
        files={"file": ("test.png", b"fake image bytes", "image/png")},
    )
    assert res_bad_type.status_code == 400

    # Path traversal in angle_id
    res_bad_angle = client.post(
        "/api/universe/upload/angle",
        data={"angle_id": "../evil"},
        files={"file": ("test.png", b"fake image bytes", "image/png")},
    )
    assert res_bad_angle.status_code == 400

    # Valid angle upload
    res_angle = client.post(
        "/api/universe/upload/angle",
        data={"angle_id": "angle_closeup"},
        files={"file": ("test.png", b"fake image bytes", "image/png")},
    )
    assert res_angle.status_code == 200
    assert "angle_angle_closeup_test.png" in res_angle.json()["filename"]


def test_upload_scene_image_and_no_etag_drift(client):
    ep_id, ep_dir = _create_test_episode("ep97-scene-image")
    etag_before = compute_etag(ep_id)

    # Invalid file type
    res_bad = client.post(
        f"/api/projects/{ep_id}/upload/scene_image",
        data={"scene_id": "scene_01"},
        files={"file": ("test.txt", b"plain text", "text/plain")},
    )
    assert res_bad.status_code == 400

    # Valid image upload
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    res_ok = client.post(
        f"/api/projects/{ep_id}/upload/scene_image",
        data={"scene_id": "scene_01"},
        files={"file": ("test.png", fake_png, "image/png")},
    )
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["status"] == "success"
    assert data["scene_id"] == "scene_01"
    assert data["image_url"] == f"/media/{ep_id}/assets/images/scene_01.png"
    assert data["image_path"] == f"/media/{ep_id}/assets/images/scene_01.png"
    assert "image_version" in data
    assert "absolute_path" in data

    # State file should reflect updated scene image
    saved_state = read_state(ep_id)
    scene = saved_state["scenes"][0]
    assert scene["image_path"] == data["image_url"]
    assert scene["visual_asset"] == data["image_url"]
    assert scene["image_version"] == data["image_version"]

    # Verify that GET load_state DOES NOT rewrite state.json or change ETag
    etag_after_upload = compute_etag(ep_id)
    loaded = load_state(ep_id)
    assert loaded["scenes"][0]["image_path"] == data["image_url"]
    assert compute_etag(ep_id) == etag_after_upload

    # Call GET /api/projects/{ep_id} multiple times and ensure ETag is completely stable
    res_get1 = client.get(f"/api/projects/{ep_id}")
    assert res_get1.status_code == 200
    res_get2 = client.get(f"/api/projects/{ep_id}")
    assert res_get2.status_code == 200
    assert compute_etag(ep_id) == etag_after_upload


def test_upload_scene_video(client):
    ep_id, ep_dir = _create_test_episode("ep96-scene-video")

    fake_mp4 = b"\x00\x00\x00 ftypisom" + b"\x00" * 32
    res = client.post(
        f"/api/projects/{ep_id}/upload/scene_video",
        data={"scene_id": "scene_01"},
        files={"file": ("motion.mp4", fake_mp4, "video/mp4")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["scene_id"] == "scene_01"
    assert data["video_url"].endswith("scene_01_motion_motion.mp4")
    assert data["video_path"] == data["video_url"]

    # Check state mutation
    saved_state = read_state(ep_id)
    scene = saved_state["scenes"][0]
    assert scene["video_path"] == data["video_url"]
    assert scene["video_asset"] == data["video_url"]
    assert scene["shot_mode"] == "ai_video"
    assert scene["media_type"] == "ai_video"


def test_upload_asset_audio_segment_isolation(client):
    ep_id, ep_dir = _create_test_episode("ep95-audio-upload")

    fake_mp3 = b"ID3" + b"\x00" * 32
    # Upload voice for seg_1
    res1 = client.post(
        f"/api/projects/{ep_id}/upload/audio",
        data={"segment_id": "seg_1"},
        files={"file": ("voice.mp3", fake_mp3, "audio/mpeg")},
    )
    assert res1.status_code == 200
    assert res1.json()["filename"] == "seg_1_voice.mp3"

    # Upload voice with same filename for seg_2 without collision
    res2 = client.post(
        f"/api/projects/{ep_id}/upload/audio",
        data={"segment_id": "seg_2"},
        files={"file": ("voice.mp3", fake_mp3, "audio/mpeg")},
    )
    assert res2.status_code == 200
    assert res2.json()["filename"] == "seg_2_voice.mp3"

    # Bad segment_id with traversal
    res_bad = client.post(
        f"/api/projects/{ep_id}/upload/audio",
        data={"segment_id": "../evil"},
        files={"file": ("voice.mp3", fake_mp3, "audio/mpeg")},
    )
    assert res_bad.status_code == 400


def test_transcript_step_index_handling():
    entries = [
        {"type": "USER_INPUT", "content": "start"},
        {"step_index": 0, "type": "PLANNER_RESPONSE"},
        {"type": "TOOL_RESULT", "tool": "render"},
        {"step_index": 1, "type": "PLANNER_RESPONSE"},
    ]
    processed = []
    last_step = -1
    for entry in entries:
        idx = entry.get("step_index")
        if isinstance(idx, int):
            if idx <= last_step:
                continue
            last_step = idx
        processed.append(entry)

    assert len(processed) == 4
    assert processed[0]["type"] == "USER_INPUT"
    assert processed[2]["type"] == "TOOL_RESULT"


def test_default_universe_schema():
    u = _default_universe()
    assert u["version"] == "1.2.0"
    assert "camera_angles" not in u
    assert isinstance(u["environment"]["camera_angles"], list)
    assert "canon_en" in u["environment"]
    assert "table_en" in u["environment"]["canon_en"]


def test_upload_universe_angle(client):
    from backend.services.state_store import write_universe, read_universe
    u = _default_universe()
    u["environment"]["camera_angles"] = [
        {"id": "seat_1", "flow_tag": "@Seat_1", "reference_image_path": ""}
    ]
    write_universe(u)

    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    res = client.post(
        "/api/universe/upload/angle",
        data={"angle_id": "seat_1"},
        files={"file": ("angle_1.png", fake_png, "image/png")},
    )
    assert res.status_code == 200, res.text
    saved = read_universe()
    ang = saved["environment"]["camera_angles"][0]
    assert ang["id"] == "seat_1"
    assert ang["reference_image_path"] == "/media/universe/angle_seat_1_angle_1.png"

