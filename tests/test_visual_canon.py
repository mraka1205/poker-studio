from backend.services import visual_canon as vc
from scripts.apply_visual_anchors import apply


def test_seed_quality():
    for tag, c in vc.SEED_CHARACTERS.items():
        assert 25 <= len(c["dna_block_en"].split()) <= 65, tag
        assert "--" not in c["dna_block_en"] and "@" not in c["dna_block_en"]
        assert set(c["acting_beats_en"]) == set(vc.EMOTION_KEYS), tag
    assert set(vc.SHOT_LIBRARY[k]["mode"] for k in vc.SHOT_LIBRARY) == {"single", "props", "wide", "topdown", "duel"}
    assert set(vc.DEFAULT_MOOD_FOR_EMOTION.values()) <= set(vc.LIGHTING_MOODS)


def test_apply_is_idempotent_and_ignores_unknown_chars():
    u = {"environment": {}, "characters": [{"flow_tag": "@Arash", "dna_block_en": "old"}, {"flow_tag": "@Nobody"}]}
    u, changes = apply(u)
    assert any("@Arash: dna_block_en" in c for c in changes)
    assert u["characters"][0]["dna_block_en"] == vc.SEED_CHARACTERS["@Arash"]["dna_block_en"]
    assert "dna_block_en" not in u["characters"][1]
    _, changes2 = apply(u)
    assert changes2 == []
