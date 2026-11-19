import json
from backend.services.scene_prompt_builder import build_episode_prompts
from backend.services.state_store import read_state, write_state
from tests.helpers_visual import make_state, make_universe, media_files


def _setup(root, ep="ep99-test"):
    uni = make_universe()
    (root / "universe.json").write_text(json.dumps(uni), encoding="utf-8")
    for url in media_files(uni):
        p = root / url[len("/media/"):]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
    (root / ep).mkdir()
    write_state(ep, make_state(ep))


def test_full_build(tmp_path):
    ep = "ep99-test"
    _setup(tmp_path, ep)
    res = build_episode_prompts(ep)
    assert res["errors"] == [], res["errors"]
    st = read_state(ep)
    for sc in st["scenes"]:
        assert sc["image_prompt_en"] == sc["visual_prompt_en"] and "@" not in sc["image_prompt_en"]
        assert sc["table_blueprint"]["community_cards"]["stage"] in ("preflop", "flop")
    assert st["scenes"][2]["poker_table_state"]["pot_bb"] == 47.5
    batch = json.loads((tmp_path / ep / "assets" / "image_batch.json").read_text(encoding="utf-8"))
    assert [b["ImageName"] for b in batch] == [f"scene_0{i}" for i in range(1, 7)]
    assert not batch[0]["ImagePaths"][-1].endswith("scene_01.png")
    assert batch[1]["ImagePaths"][-1].endswith("scene_01.png") and len(batch[1]["ImagePaths"]) == 4


def test_single_scene_and_errors(tmp_path):
    ep = "ep99-test"
    _setup(tmp_path, ep)
    assert build_episode_prompts(ep, scene_id="scene_02")["errors"] == []
    assert (tmp_path / ep / "assets" / "image_batch_single.json").exists()
    st = read_state(ep)
    st["scenes"][1]["scene_spec"]["shot_type"] = "nope"
    write_state(ep, st)
    res = build_episode_prompts(ep)
    assert res["status"] == "error" and any("scene_02" in e for e in res["errors"])
