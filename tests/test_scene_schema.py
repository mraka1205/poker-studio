from backend.services.scene_schema import normalize_scene, validate_scenes, strip_flags


def make_scene(i, media="static_image"):
    prefix = "Maintain exact visual continuity " if i > 1 else ""
    s = {
        "scene_id": f"scene_{i:02d}", "media_type": media, "duration_sec": 2.0,
        "visual_prompt_en": prefix + " ".join(["word"] * 90) + " vertical 9:16",
        "table_blueprint": {"community_cards": {"stage": "flop"}, "pot": {"total_bb": 10}},
        "sfx_cue": "card_snap",
    }
    if media == "static_image":
        s["camera_direction"] = {"motion_type": "slow_zoom_in", "zoom_intensity": 1.2, "camera_prompt_en": "push in"}
    else:
        s["motion_prompt_en"] = "silent acting (mouth closed, no talking)"
    return s


def test_valid_scenes_pass():
    scenes = [make_scene(1), make_scene(2, "ai_video")]
    assert validate_scenes([normalize_scene(s, i, "ep99") for i, s in enumerate(scenes)]) == []


def test_short_prompt_and_missing_camera_fail():
    bad = make_scene(1)
    bad["visual_prompt_en"] = "too short 9:16"
    del bad["camera_direction"]
    errs = validate_scenes([normalize_scene(bad, 0, "ep99")])
    assert any("words" in e for e in errs) and any("camera_direction" in e for e in errs)


def test_normalize_sets_ids_and_strips_flags():
    n = normalize_scene({"id": "scene_03", "motion_prompt_en": "go --ar 9:16 now"}, 2, "ep99")
    assert n["scene_id"] == "scene_03" and n["id"] == "scene_03"
    assert "--ar" not in n["motion_prompt_en"]
    assert strip_flags("a --v 6.1 b") == "a b"


def test_scene_spec_path_requires_built_prompt():
    s = make_scene(1)
    s["scene_spec"] = {"shot_type": "wide_master"}
    errs = validate_scenes([normalize_scene(s, 0, "ep99")])
    assert any("build_scene_prompts" in e for e in errs)
    s["image_prompt_en"] = " ".join(["word"] * 130)
    assert not any("image_prompt_en" in e for e in validate_scenes([normalize_scene(s, 0, "ep99")]))

