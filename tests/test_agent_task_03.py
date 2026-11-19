import io
import json
from datetime import datetime
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.paths import projects_dir
from backend.services.state_store import read_state, write_state, write_universe


@pytest.fixture
def client():
    return TestClient(app)


def _init_episode(ep_id="ep01-hitl-test"):
    ep_dir = projects_dir() / ep_id
    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "audio").mkdir(parents=True, exist_ok=True)
    state = {
        "episode_id": ep_id,
        "title": "HITL Test Episode",
        "english_title": "HITL Test",
        "version": "2.0.0",
        "current_stage": 1,
        "stages": [
            {"id": f"stage_{i}", "stage_number": i, "name_fa": f"مرحله {i}", "name_en": f"Stage {i}", "status": "pending", "approved_at": None, "notes": ""}
            for i in range(1, 10)
        ],
        "idea": {"theme": "", "raw_hand_or_concept": "", "core_lesson": ""},
        "bible": {"visual_style": "default_style"},
        "characters": [],
        "script": {"title": "HITL Test Episode", "segments": []},
        "scenes": [],
        "audio": {"tracks": []},
    }
    state["stages"][0]["status"] = "in_progress"
    write_state(ep_id, state)
    return ep_id, ep_dir


def test_import_bible_hitl_and_propagation(client):
    ep_id, _ = _init_episode("ep01-bible-test")
    payload = {
        "json_content": {
            "concept_summary": {
                "theme": "Over-bluffing the River",
                "poker_lesson": "Know your fold equity",
            },
            "hand_details": {"blinds": "100/200", "pot": "4500"},
            "comedy_beats": ["Arash sweats nervously", "Bijan stares blankly"],
        }
    }

    res = client.post(f"/api/projects/{ep_id}/import-json/bible", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["current_stage"] == 1  # HITL Guardrail: MUST NOT auto-advance

    saved = read_state(ep_id)
    assert saved["current_stage"] == 1
    assert saved["idea"]["theme"] == "Over-bluffing the River"
    assert saved["idea"]["core_lesson"] == "Know your fold equity"
    assert saved["bible"]["hand_details"]["pot"] == "4500"

    # Stage 1 and 2 must be waiting_approval, NOT approved
    stage_1 = next(s for s in saved["stages"] if s["stage_number"] == 1)
    stage_2 = next(s for s in saved["stages"] if s["stage_number"] == 2)
    assert stage_1["status"] == "waiting_approval"
    assert stage_1["approved_at"] is None
    assert stage_2["status"] == "waiting_approval"
    assert stage_2["approved_at"] is None


def test_import_preserves_already_approved_stage(client):
    ep_id, _ = _init_episode("ep02-approved-preservation")
    # Manually approve stage 1 first
    state = read_state(ep_id)
    state["stages"][0]["status"] = "approved"
    state["stages"][0]["approved_at"] = "2026-11-19T12:00:00Z"
    write_state(ep_id, state)

    payload = {
        "json_content": {
            "concept_summary": {"theme": "Updated Theme"},
        }
    }
    res = client.post(f"/api/projects/{ep_id}/import-json/bible", json=payload)
    assert res.status_code == 200

    saved = read_state(ep_id)
    stage_1 = next(s for s in saved["stages"] if s["stage_number"] == 1)
    assert stage_1["status"] == "approved"
    assert stage_1["approved_at"] == "2026-11-19T12:00:00Z"


def test_import_script_speaker_and_audio_status(client):
    ep_id, ep_dir = _init_episode("ep03-script-test")
    # Create seg_01.wav on disk, seg_02.wav is missing
    audio_dir = ep_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "seg_01.wav").write_bytes(b"RIFFdummywavdata")

    payload = {
        "json_content": {
            "script_title": "Script Test",
            "segments": [
                {
                    "id": "seg_01",
                    "subtitle_fa": "سلام به همه",
                    "tts_fa": "سَلام بِه هَمِه",
                    # No speaker provided -> must default to NARRATOR
                },
                {
                    "id": "seg_02",
                    "speaker": "Arash",
                    "subtitle_fa": "من آل این می‌زنم",
                    "tts_fa": "مَن آل این می‌زَنَم",
                },
            ],
        }
    }

    res = client.post(f"/api/projects/{ep_id}/import-json/script", json=payload)
    assert res.status_code == 200, res.text
    saved = read_state(ep_id)

    stage_3 = next(s for s in saved["stages"] if s["stage_number"] == 3)
    assert stage_3["status"] == "waiting_approval"
    assert stage_3["approved_at"] is None
    assert saved["current_stage"] == 1

    tracks = saved["audio"]["tracks"]
    assert len(tracks) == 2

    # Track 1 has existing wav and default speaker
    assert tracks[0]["speaker"] == "NARRATOR"
    assert tracks[0]["status"] == "ready"
    assert tracks[0]["audio_file"] == f"/media/{ep_id}/audio/seg_01.wav"

    # Track 2 missing wav
    assert tracks[1]["speaker"] == "Arash"
    assert tracks[1]["status"] == "pending_audio"
    assert tracks[1]["audio_file"] == ""


def test_import_characters_preserves_v2_and_no_kambiz(client):
    ep_id, _ = _init_episode("ep04-characters-test")
    payload = {
        "json_content": {
            "style_bible_en": "Custom stop motion needle-felt style with rich felt textures",
            "characters": [
                {
                    "id": "char_01",
                    "name_fa": "آرش",
                    "flow_tag": "@Arash",
                    "default_seat": "seat_1",
                    "assigned_seat": "seat_2",
                    "dna_block_en": "Orange needle-felted wolf, wearing teal hoodie",
                    "short_look_en": "Fuzzy wolf with sharp expressive eyes",
                    "acting_beats_en": "Twitches left ear when bluffing",
                    "persona_behavior_prompt": "Aggressive maniac who overbets",
                    "voice_description_fa": "صدای تیز و پر انرژی",
                    "face_expressions_prompt_en": "Confident grin, sweat drops on forehead",
                    "full_body_prompt_en": "Full turnaround of orange wolf in hoodie",
                }
            ],
        }
    }

    res = client.post(f"/api/projects/{ep_id}/import-json/characters", json=payload)
    assert res.status_code == 200, res.text
    saved = read_state(ep_id)

    # Style bible updated
    assert saved["bible"]["visual_style"] == "Custom stop motion needle-felt style with rich felt textures"

    # Stage 4 waiting_approval, current_stage not incremented
    stage_4 = next(s for s in saved["stages"] if s["stage_number"] == 4)
    assert stage_4["status"] == "waiting_approval"
    assert saved["current_stage"] == 1

    chars = saved["characters"]
    assert len(chars) == 1
    c = chars[0]
    assert c["status"] == "waiting_approval"
    assert c["flow_tag"] == "@Arash"
    assert c["default_seat"] == "seat_1"
    assert c["assigned_seat"] == "seat_2"
    assert c["dna_block_en"] == "Orange needle-felted wolf, wearing teal hoodie"
    assert c["short_look_en"] == "Fuzzy wolf with sharp expressive eyes"
    assert c["acting_beats_en"] == "Twitches left ear when bluffing"
    assert c["voice_description_fa"] == "صدای تیز و پر انرژی"
    assert c["avatar_url"] == ""  # Absolutely NO kambiz.svg fallback
    assert c["turnaround_sheet"] == ""


def test_sync_universe_characters_v2_fields_and_no_kambiz(client):
    ep_id, _ = _init_episode("ep05-sync-universe-test")

    # Set up universe
    universe_data = {
        "characters": [
            {
                "id": "char_bijan",
                "name_fa": "بیژن",
                "flow_tag": "@Bijan",
                "default_seat": "seat_3",
                "archetype": "Rock / Nit",
                "dna_block_en": "Grey felted badger with oversized spectacles",
                "short_look_en": "Spectacled stoic badger",
                "acting_beats_en": "Adjusts spectacles slowly",
                "personality_and_catchphrases_fa": "خیلی محافظه‌کار",
                "voice_description_fa": "صدای بم و خسته",
                "is_style_anchor": False,
            }
        ],
        "environment": {},
    }
    write_universe(universe_data)

    res = client.post(
        f"/api/projects/{ep_id}/sync-universe-characters",
        json={"character_ids": ["char_bijan"]},
    )
    assert res.status_code == 200, res.text
    saved = read_state(ep_id)
    assert len(saved["characters"]) == 1
    c = saved["characters"][0]
    assert c["id"] == "char_bijan"
    assert c["name_fa"] == "بیژن"
    assert c["flow_tag"] == "@Bijan"
    assert c["default_seat"] == "seat_3"
    assert c["assigned_seat"] == "seat_3"
    assert c["dna_block_en"] == "Grey felted badger with oversized spectacles"
    assert c["short_look_en"] == "Spectacled stoic badger"
    assert c["acting_beats_en"] == "Adjusts spectacles slowly"
    assert c["avatar_url"] == ""  # NO kambiz.svg
    assert c["turnaround_sheet"] == ""


def test_import_scenes_preserves_uploaded_assets_and_normalizes(client):
    ep_id, _ = _init_episode("ep06-scenes-test")

    # Seed state with existing scene having uploaded assets
    state = read_state(ep_id)
    state["scenes"] = [
        {
            "id": "scene_01",
            "scene_id": "scene_01",
            "title": "Old Scene 1",
            "image_path": f"/media/{ep_id}/assets/images/scene_01.png",
            "visual_asset": f"/media/{ep_id}/assets/images/scene_01.png",
            "video_path": f"/media/{ep_id}/scenes/scene_01_motion.mp4",
            "video_asset": f"/media/{ep_id}/scenes/scene_01_motion.mp4",
            "shot_mode": "ai_video",
        }
    ]
    write_state(ep_id, state)

    payload = {
        "json_content": {
            "hand_timeline": {"preflop": "Hero raises to 3bb"},
            "scenes": [
                {
                    "scene_id": "scene_01",
                    "scene_title_fa": "نمای آغازین بازطراحی شده",
                    "shot_mode": "ai_video",
                    "media_type": "ai_video",
                    "visual_prompt_en": "Felt poker room wide shot with needle-felted characters",
                }
            ],
        }
    }

    res = client.post(f"/api/projects/{ep_id}/import-json/scenes", json=payload)
    assert res.status_code == 200, res.text
    saved = read_state(ep_id)

    assert saved["hand_timeline"] == {"preflop": "Hero raises to 3bb"}
    assert len(saved["scenes"]) == 1
    sc = saved["scenes"][0]
    assert sc["id"] == "scene_01"
    assert sc["status"] == "ready_for_review"
    assert sc["title"] == "نمای آغازین بازطراحی شده"
    # Uploaded paths preserved!
    assert sc["image_path"] == f"/media/{ep_id}/assets/images/scene_01.png"
    assert sc["video_path"] == f"/media/{ep_id}/scenes/scene_01_motion.mp4"

    # Stage 6 waiting_approval
    stage_6 = next(s for s in saved["stages"] if s["stage_number"] == 6)
    assert stage_6["status"] == "waiting_approval"
    assert saved["current_stage"] == 1


def test_import_scenes_hard_validation_error(client):
    ep_id, _ = _init_episode("ep07-scenes-invalid-test")

    # Invalid scene ID format fails hard validation
    payload = {
        "json_content": {
            "scenes": [
                {
                    "id": "invalid_id_format",
                    "scene_id": "invalid_id_format",
                    "visual_prompt_en": "test",
                }
            ]
        }
    }
    res = client.post(f"/api/projects/{ep_id}/import-json/scenes", json=payload)
    assert res.status_code == 422
    assert "must match scene_NN" in res.json()["detail"]


def test_manual_stage_approval_advancement(client):
    ep_id, _ = _init_episode("ep08-manual-approval-test")

    # HITL: Manual approval via /stage_status MUST advance stage and set UTC Z timestamp
    req = {
        "stage_number": 1,
        "status": "approved",
        "notes": "Reviewed and approved by producer",
    }
    res = client.post(f"/api/projects/{ep_id}/stage_status", json=req)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["current_stage"] == 2

    saved = read_state(ep_id)
    assert saved["current_stage"] == 2
    stage_1 = next(s for s in saved["stages"] if s["stage_number"] == 1)
    stage_2 = next(s for s in saved["stages"] if s["stage_number"] == 2)

    assert stage_1["status"] == "approved"
    assert stage_1["notes"] == "Reviewed and approved by producer"
    assert stage_1["approved_at"].endswith("Z")
    # Verify it parses as ISO datetime
    dt = datetime.fromisoformat(stage_1["approved_at"].replace("Z", "+00:00"))
    assert dt is not None

    # Next stage transitioned from pending to in_progress
    assert stage_2["status"] == "in_progress"


def test_build_prompt_scenes_v2(client):
    ep_id, _ = _init_episode("ep09-prompt-scenes-test")
    # Setup state with bible hand_details
    state = read_state(ep_id)
    state["bible"]["hand_details"] = {
        "blinds": "100/200",
        "preflop": "Arash raises to 600, Bijan calls",
        "flop": "8s 4d 2c, both check",
    }
    state["characters"] = [
        {"id": "char_01", "name_en": "Arash", "flow_tag": "@Arash", "assigned_seat": "seat_1"}
    ]
    write_state(ep_id, state)

    # Setup universe
    write_universe({
        "characters": [
            {
                "id": "char_01",
                "name_en": "Arash",
                "flow_tag": "@Arash",
                "default_seat": "seat_1",
                "dna_block_en": "Orange felted wolf",
            }
        ],
        "environment": {
            "flow_tag": "@PokerRoom",
            "description_fa": "اتاق پوکر",
            "camera_angles": [
                {"id": "seat_1", "flow_tag": "@Seat_1", "background_landmarks_en": "Door and shelf"}
            ]
        }
    })

    res = client.post(f"/api/projects/{ep_id}/build-prompt/scenes")
    assert res.status_code == 200, res.text
    prompt_data = res.json()
    prompt = prompt_data["prompt"]

    # Verify hand_details is in the prompt
    assert "BIBLE HAND DETAILS" in prompt
    assert "Arash raises to 600" in prompt

    # Verify seating summary is from format_seating_summary
    assert "Seat seat_1 (@Seat_1): Arash (@Arash)" in prompt
    assert "Door and shelf" in prompt

    # Verify v2 requirements
    assert "top-level keys `\"hand_timeline\"` and `\"scenes\"`" in prompt
    assert "FORBIDDEN keys" in prompt
    assert "DO NOT write `visual_prompt_en`" in prompt

    # Verify v1 contradiction is GONE
    assert "8-part visual_prompt_en" not in prompt
    assert "minimum 80-120 words" not in prompt

