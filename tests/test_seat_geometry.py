import pytest
from backend.services.seat_geometry import RosterError, frame_neighbors, merge_roster


def test_neighbors_wrap():
    assert frame_neighbors("seat_1") == {"left": "seat_6", "right": "seat_2"}
    assert frame_neighbors("seat_6") == {"left": "seat_5", "right": "seat_1"}
    assert frame_neighbors("seat_5")["right"] == "seat_6"
    with pytest.raises(RosterError):
        frame_neighbors("seat_9")


def test_merge_roster():
    uni = [{"id": "a", "flow_tag": "@A", "default_seat": "seat_1"}, {"id": "b", "flow_tag": "@B", "default_seat": "seat_5"}]
    r = merge_roster([{"id": "a", "assigned_seat": "seat_3"}, {"flow_tag": "@B"}], uni)
    assert r["seat_3"]["flow_tag"] == "@A" and r["seat_5"]["seat"] == "seat_5"
    assert set(merge_roster([], uni)) == {"seat_1", "seat_5"}
    with pytest.raises(RosterError):
        merge_roster([{"id": "a", "assigned_seat": "seat_5"}, {"id": "b"}], uni)
