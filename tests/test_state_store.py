import json
import pytest
from backend.services import state_store as ss
from backend.services.paths import projects_dir


def _make(ep="ep99-test"):
    d = projects_dir() / ep
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"episode_id": ep, "scenes": []}), encoding="utf-8")
    return ep


def test_roundtrip_backup_and_no_tmp_left():
    ep = _make()
    ss.update_state(ep, lambda s: s.update(title="x"))
    assert ss.read_state(ep)["title"] == "x"
    d = projects_dir() / ep
    assert (d / "state.json.bak").exists()
    assert not list(d.glob("*.tmp"))


def test_etag_conflict():
    ep = _make()
    e1 = ss.compute_etag(ep)
    ss.apply_patch(ep, {"a": 1})
    with pytest.raises(ss.EtagConflict):
        ss.apply_patch(ep, {"b": 2}, base_etag=e1)


def test_snapshot_and_restore():
    ep = _make()
    snap = ss.snapshot_state(ep, "state.json.pre_test.bak")
    ss.apply_patch(ep, {"broken": True})
    ss.restore_state_from(ep, snap, keep_rejected_as="state.json.rejected")
    assert "broken" not in ss.read_state(ep)
    assert (projects_dir() / ep / "state.json.rejected").exists()
