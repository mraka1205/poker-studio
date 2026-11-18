from scripts.repair_universe import repair, TABLET, NOTEBOOK


def test_repair_is_idempotent_and_fixes_placeholders():
    u = {"characters": [
        {"id": "a", "persona_behavior_prompt": "persona", "personality_and_catchphrases_fa": "x...",
         "visual_prompt_en": f"intro {TABLET}", "full_body_prompt_en": "full", "is_style_anchor": False},
        {"id": "b", "persona_behavior_prompt": "p2", "personality_and_catchphrases_fa": "ok text",
         "visual_prompt_en": "puppet... --ar 9:16", "full_body_prompt_en": "full2"},
    ]}
    fixed, notes = repair(u)
    a, b = fixed["characters"]
    assert NOTEBOOK in a["visual_prompt_en"] and TABLET not in a["visual_prompt_en"]
    assert a["personality_and_catchphrases_fa"] == "persona"
    assert b["visual_prompt_en"] == "full2" and b["personality_and_catchphrases_fa"] == "ok text"
    assert a["is_style_anchor"] is True
    _, notes2 = repair(fixed)
    assert notes2 == []
