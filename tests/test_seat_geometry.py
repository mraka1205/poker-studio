import pytest
from backend.services.seat_geometry import (
    RosterError,
    frame_neighbors,
    merge_roster,
    format_seating_summary,
    SEAT_ORDER,
)


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


def test_format_seating_summary():
    uni = [
        {"id": "a", "name_en": "Arash", "flow_tag": "@Arash", "default_seat": "seat_1"},
        {"id": "b", "name_en": "Bijan", "flow_tag": "@Bijan", "default_seat": "seat_2"},
    ]
    roster = merge_roster([], uni)
    angles = [
        {"id": "seat_1", "flow_tag": "@Seat_1", "background_landmarks_en": "Door and shelf"},
        {"id": "seat_2", "flow_tag": "@Seat_2", "background_landmarks_en": "Bookshelf and neon"},
    ]
    summary = format_seating_summary(roster, angles)
    assert "- Seat seat_1 (@Seat_1): Arash (@Arash)" in summary
    assert "Right neighbor: Bijan (@Bijan) (seat_2)" in summary
    assert "Left neighbor: Empty Chair (seat_6)" in summary
    assert "Door and shelf" in summary

    # Empty seats format
    assert "- Seat seat_3 (@Seat_3): [Empty Chair]" in summary

