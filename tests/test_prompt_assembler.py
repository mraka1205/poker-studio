import pytest
from backend.services import table_state as ts
from backend.services import visual_canon as vc
from backend.services.prompt_assembler import SpecError, assemble_scene_prompt
from backend.services.seat_geometry import merge_roster
from tests.helpers_visual import make_state, make_timeline, make_universe


def ctx(idx=1):
    u = make_universe()
    st = make_state()
    return {"universe": u, "roster": merge_roster(st["characters"], u["characters"]),
            "snapshots": ts.compute_timeline(make_timeline()), "scene_index": idx, "master_path": "/media/ep99-test/assets/images/scene_01.png"}


def test_closeup_contains_anchors_and_neighbors():
    spec = {"shot_type": "closeup_seat", "focal": "@Arash", "emotion": "thinking", "timeline_step": 1}
    out = assemble_scene_prompt(spec, ctx())
    p = out["image_prompt_en"]
    assert "slender needle-felted wool puppet with round wire spectacles" in p
    assert vc.STYLE_LOCK in p and vc.NEGATIVE_BLOCK in p and vc.COMPOSITION_RULE in p
    assert "Left edge of the frame: an empty dark leather chair." in p        # seat_6 is empty
    assert "Right edge of the frame: the soft out-of-focus shoulder of Keyvan in a charcoal turtleneck." in p  # seat_2
    assert "@" not in p and "--" not in p
    assert [r["role"] for r in out["references"]] == ["angle", "face", "body", "master"]
    assert p.startswith("References: Image 1 = angle and set")
    assert 120 <= out["word_count"] <= 400


def test_deterministic_and_first_scene_has_no_master():
    spec = {"shot_type": "wide_master", "timeline_step": 0}
    a = assemble_scene_prompt(spec, ctx(0))
    assert a == assemble_scene_prompt(spec, ctx(0))
    assert "master" not in [r["role"] for r in a["references"]]
    assert "Empty dark leather chairs at: seat 3, seat 4, seat 6." in a["image_prompt_en"]


@pytest.mark.parametrize("spec", [
    {"shot_type": "nope"}, {"shot_type": "closeup_seat"}, {"shot_type": "ots_duel", "focal": "@Arash"},
    {"shot_type": "closeup_seat", "focal": "@Rahim"}, {"shot_type": "closeup_seat", "focal": "@Arash", "emotion": "dancing"}])
def test_bad_specs_raise(spec):
    with pytest.raises(SpecError):
        assemble_scene_prompt(spec, ctx())


def test_reference_cap_and_missing_files():
    c = ctx()
    out = assemble_scene_prompt({"shot_type": "wide_master", "timeline_step": 0}, c)
    assert len(out["references"]) <= 4
    c["path_exists"] = lambda p: "seat_1" not in p
    out = assemble_scene_prompt({"shot_type": "closeup_seat", "focal": "@Arash", "timeline_step": 1}, c)
    assert any("missing reference image for angle" in w for w in out["warnings"])
