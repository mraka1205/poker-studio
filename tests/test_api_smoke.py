import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.state_store import read_state, read_universe, write_state, write_universe, update_state


@pytest.fixture
def client():
    return TestClient(app)


def test_api_smoke_pipeline(client):
    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"
    assert "Poker Studio" in res_health.json()["app"]

    # 2. Universe endpoint
    res_uni = client.get("/api/universe")
    assert res_uni.status_code == 200
    uni_data = res_uni.json()
    assert "environment" in uni_data
    assert "characters" in uni_data

    # 3. Verify removed external endpoints return 404
    for dead_endpoint in ["/api/settings", "/api/gemini/models", "/api/openrouter/models"]:
        res_dead = client.get(dead_endpoint)
        assert res_dead.status_code in (404, 405)

    # 4. Create episode via POST /api/projects
    create_payload = {
        "title": "Smoke Test Episode",
        "english_title": "Smoke Test",
        "raw_hand_or_concept": "Hero holds pocket Aces against villain bluff",
    }
    res_create = client.post("/api/projects", json=create_payload)
    assert res_create.status_code == 200
    ep_id = res_create.json()["episode_id"]
    assert ep_id

    # 5. Build prompt for stage 1 (bible / idea)
    res_prompt_bible = client.post(f"/api/projects/{ep_id}/build-prompt/bible")
    assert res_prompt_bible.status_code == 200
    data_prompt = res_prompt_bible.json()
    assert "prompt" in data_prompt and len(data_prompt["prompt"]) > 100

    # 6. Import JSON for bible (HITL check: stage 1 must become waiting_approval, not approved)
    import_payload = {
        "json_content": {
            "concept_summary": {
                "theme": "Aces Cracked",
                "poker_lesson": "Do not marry your hand",
            },
            "hand_details": {"blinds": "50/100", "pot": "1200"},
            "comedy_beats": ["Arash celebrates too early"],
        }
    }
    res_import = client.post(f"/api/projects/{ep_id}/import-json/bible", json=import_payload)
    assert res_import.status_code == 200
    state_after_import = read_state(ep_id)
    assert state_after_import["current_stage"] == 1
    stage_1 = next(s for s in state_after_import["stages"] if s["stage_number"] == 1)
    assert stage_1["status"] == "waiting_approval"
    assert stage_1["approved_at"] is None

    # 7. Upload scene image via POST /api/projects/{ep_id}/upload/scene_image
    def _add_scene(st):
        st["scenes"] = [
            {
                "id": "scene_01",
                "scene_id": "scene_01",
                "media_type": "static_image",
                "title": "Opening Shot",
            }
        ]
    update_state(ep_id, _add_scene)

    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    res_upload_img = client.post(
        f"/api/projects/{ep_id}/upload/scene_image",
        data={"scene_id": "scene_01"},
        files={"file": ("frame_01.png", fake_png, "image/png")},
    )
    assert res_upload_img.status_code == 200
    assert res_upload_img.json()["status"] == "success"
    assert res_upload_img.json()["scene_id"] == "scene_01"
    assert res_upload_img.json()["image_url"] == f"/media/{ep_id}/assets/images/scene_01.png"

    # 8. Upload universe angle image via POST /api/universe/upload/angle
    u = read_universe()
    u["environment"]["camera_angles"] = [
        {"id": "seat_1", "flow_tag": "@Seat_1", "reference_image_path": ""}
    ]
    write_universe(u)

    res_upload_angle = client.post(
        "/api/universe/upload/angle",
        data={"angle_id": "seat_1"},
        files={"file": ("angle_1.png", fake_png, "image/png")},
    )
    assert res_upload_angle.status_code == 200
    assert res_upload_angle.json()["status"] == "success"

    # 9. Build prompt for scenes (stage 5)
    res_prompt_scenes = client.post(f"/api/projects/{ep_id}/build-prompt/scenes")
    assert res_prompt_scenes.status_code == 200
    prompt_scenes = res_prompt_scenes.json()["prompt"]
    assert "hand_timeline" in prompt_scenes
    assert "scenes" in prompt_scenes

    # 10. Load state via GET /api/projects/{ep_id}
    res_get_state = client.get(f"/api/projects/{ep_id}")
    assert res_get_state.status_code == 200
    loaded = res_get_state.json()
    assert loaded["episode_id"] == ep_id
    assert "_etag" in loaded
    assert len(loaded["scenes"]) == 1
    assert loaded["scenes"][0]["image_path"] == f"/media/{ep_id}/assets/images/scene_01.png"


def test_episode_auto_numbering_collision(client, tmp_path, monkeypatch):
    from backend.services.paths import projects_dir
    p_dir = projects_dir()
    # Create a sparse episode directory structure: ep01 and ep05
    dummy_ep05 = p_dir / "ep05-sparse"
    dummy_ep05.mkdir(parents=True, exist_ok=True)
    try:
        res = client.post("/api/projects", json={"title": "Collision Test", "english_title": "Collision Test"})
        assert res.status_code == 200
        new_ep_id = res.json()["episode_id"]
        # Must be ep06 because max(1, 5) + 1 = 6, not len([dirs]) + 1
        assert new_ep_id.startswith("ep06-")
    finally:
        import shutil
        if dummy_ep05.exists():
            shutil.rmtree(dummy_ep05, ignore_errors=True)
        if 'new_ep_id' in locals():
            created_dir = p_dir / new_ep_id
            if created_dir.exists():
                shutil.rmtree(created_dir, ignore_errors=True)


def test_legacy_9_stage_normalization_in_memory(client, tmp_path):
    from backend.services.paths import projects_dir
    p_dir = projects_dir()
    ep_id = "ep99-legacy-test"
    ep_dir = p_dir / ep_id
    ep_dir.mkdir(parents=True, exist_ok=True)

    legacy_stages = [
        {"id": f"stage_{i}", "stage_number": i, "name_fa": f"فارسی {i}", "name_en": f"Stage {i}", "status": "pending", "approved_at": None, "notes": ""}
        for i in range(1, 10)
    ]
    legacy_stages[0]["status"] = "approved"
    legacy_stages[1]["status"] = "in_progress"

    raw_state = {
        "episode_id": ep_id,
        "title": "Legacy 9-Stage Episode",
        "english_title": "Legacy 9-Stage",
        "version": "1.0.0",
        "current_stage": 5,
        "stages": legacy_stages,
        "idea": {"theme": "Legacy Theme"},
        "bible": {"visual_style": "Legacy Style"},
        "characters": [],
        "script": {"title": "Legacy Script", "segments": []},
        "scenes": [],
        "audio": {"tracks": []},
    }

    try:
        write_state(ep_id, raw_state)

        # GET request must return normalized 8-stage state
        res = client.get(f"/api/projects/{ep_id}")
        assert res.status_code == 200
        resp_data = res.json()

        assert len(resp_data["stages"]) == 8
        assert resp_data["stages"][0]["id"] == "stage_1"
        assert resp_data["stages"][0]["name_fa"] == "ایده و کتابچه"
        assert resp_data["stages"][0]["name_en"] == "Idea & Bible"
        assert resp_data["current_stage"] == 4
        stage_nums = [s["stage_number"] for s in resp_data["stages"]]
        assert stage_nums == list(range(1, 9))

        # Strict SSOT Guardrail: File on disk MUST NOT have been mutated by GET!
        disk_data = read_state(ep_id)
        assert len(disk_data["stages"]) == 9
        assert disk_data["current_stage"] == 5
        assert disk_data["stages"][0]["name_fa"] == "فارسی 1"
    finally:
        import shutil
        if ep_dir.exists():
            shutil.rmtree(ep_dir, ignore_errors=True)


