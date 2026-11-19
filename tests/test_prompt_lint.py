from backend.services.prompt_lint import lint_prompt, lint_sequence


def test_prompt_rules():
    good = " ".join(["word"] * 130)
    assert lint_prompt(good, ["word word"]) == []
    bad = lint_prompt("short --ar 9:16 for YouTube @Arash {x}", ["needed text"])
    joined = " ".join(bad)
    assert "words" in joined and "--ar" in joined and "youtube" in joined and "@" in joined and "needed text" in joined


def test_sequence_rules():
    ok = [{"shot_type": "wide_master"}, {"shot_type": "closeup_seat", "focal": "@A", "timeline_step": 1},
          {"shot_type": "chips_macro", "focal": "@B", "timeline_step": 2}, {"shot_type": "medium_seat", "focal": "@A", "timeline_step": 2},
          {"shot_type": "closeup_seat", "focal": "@B", "timeline_step": 3}, {"shot_type": "reaction_insert", "focal": "@A", "timeline_step": 3}]
    assert lint_sequence(ok) == []
    assert any("wide_master" in e for e in lint_sequence([{"shot_type": "closeup_seat"}]))
    dup = [{"shot_type": "wide_master"}] + [{"shot_type": "closeup_seat", "focal": "@A"}] * 3
    assert len(lint_sequence(dup)) >= 2
    back = [{"shot_type": "wide_master"}, {"shot_type": "medium_seat", "timeline_step": 3}, {"shot_type": "closeup_seat", "timeline_step": 1}]
    assert any("backwards" in e for e in lint_sequence(back))
    flat = [{"shot_type": "wide_master"}] + [{"shot_type": s, "focal": "@A"} for s in
            ["closeup_seat", "medium_seat", "closeup_seat", "medium_seat", "closeup_seat"]]
    assert any("at least one" in e for e in lint_sequence(flat))
