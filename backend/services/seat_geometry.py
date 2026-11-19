"""Seat ring: clockwise from above. Camera facing seat X: right = next seat, left = previous seat."""
from typing import Any, Dict, List, Optional

SEAT_ORDER = ("seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6")


class RosterError(ValueError):
    pass


def frame_neighbors(seat_id: str) -> Dict[str, str]:
    if seat_id not in SEAT_ORDER:
        raise RosterError(f"Unknown seat: {seat_id!r}")
    i = SEAT_ORDER.index(seat_id)
    return {"left": SEAT_ORDER[(i - 1) % 6], "right": SEAT_ORDER[(i + 1) % 6]}


def merge_roster(state_characters: Optional[List[Dict[str, Any]]],
                 universe_characters: Optional[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Return {seat_id: universe character record + 'seat'}.  Episode seat overrides universe default_seat."""
    uni = list(universe_characters or [])
    by_id = {c.get("id"): c for c in uni}
    by_tag = {c.get("flow_tag"): c for c in uni}
    source = list(state_characters or []) or [{"id": c.get("id"), "flow_tag": c.get("flow_tag")} for c in uni]
    roster: Dict[str, Dict[str, Any]] = {}
    for sc in source:
        uc = by_id.get(sc.get("id")) or by_tag.get(sc.get("flow_tag"))
        if uc is None:
            continue
        seat = sc.get("assigned_seat") or sc.get("default_seat") or uc.get("default_seat")
        if seat not in SEAT_ORDER:
            raise RosterError(f"{uc.get('flow_tag')}: invalid seat {seat!r}")
        if seat in roster:
            raise RosterError(f"Two characters on {seat}: {roster[seat].get('flow_tag')} and {uc.get('flow_tag')}")
        rec = dict(uc)
        rec["seat"] = seat
        roster[seat] = rec
    if not roster:
        raise RosterError("No episode characters could be matched to universe.json")
    return roster


def format_seating_summary(
    roster: Dict[str, Dict[str, Any]],
    camera_angles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    angles_by_id: Dict[str, Dict[str, Any]] = {}
    if camera_angles:
        if isinstance(camera_angles, list):
            angles_by_id = {a.get("id"): a for a in camera_angles if isinstance(a, dict) and "id" in a}
        elif isinstance(camera_angles, dict):
            angles_by_id = camera_angles

    lines: List[str] = []
    for seat_id in SEAT_ORDER:
        c = roster.get(seat_id)
        fn = frame_neighbors(seat_id)
        left_seat = fn["left"]
        right_seat = fn["right"]
        left_char = roster.get(left_seat)
        right_char = roster.get(right_seat)

        left_desc = (
            f"{left_char.get('name_en') or left_char.get('id', 'Player')} ({left_char.get('flow_tag', '')})"
            if left_char else "Empty Chair"
        )
        right_desc = (
            f"{right_char.get('name_en') or right_char.get('id', 'Player')} ({right_char.get('flow_tag', '')})"
            if right_char else "Empty Chair"
        )

        ang = angles_by_id.get(seat_id, {})
        ang_tag = ang.get("flow_tag", f"@{seat_id.title()}")
        landmarks = ang.get("background_landmarks_en", "distinct room background")

        if c:
            c_tag = c.get("flow_tag", "")
            c_name = c.get("name_en") or c.get("id", "Player")
            lines.append(
                f"- Seat {seat_id} ({ang_tag}): {c_name} ({c_tag}) | "
                f"Left neighbor: {left_desc} ({left_seat}) | "
                f"Right neighbor: {right_desc} ({right_seat}) | "
                f"Background behind: {landmarks}"
            )
        else:
            lines.append(
                f"- Seat {seat_id} ({ang_tag}): [Empty Chair] | "
                f"Left: {left_desc} | Right: {right_desc} | "
                f"Background behind: {landmarks}"
            )

    return "\n".join(lines)
