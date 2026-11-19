from typing import Any, Dict, List, Sequence

from backend.services.seat_geometry import SEAT_ORDER

RANKS = {"2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight",
         "9": "nine", "T": "ten", "J": "jack", "Q": "queen", "K": "king", "A": "ace"}
SUITS = {"c": "clubs", "d": "diamonds", "h": "hearts", "s": "spades"}
STAGE_CARDS = {"preflop": 0, "flop": 3, "turn": 4, "river": 5}
ACTION_TYPES = {"post", "bet", "raise", "call", "check", "fold", "allin"}
POT_TIERS = [
    (6, "a tiny cluster of about 4 chips (white and red)"),
    (20, "a small pile of about 8 chips (mostly red with a few white)"),
    (60, "a medium mound of about 15 chips (red and green)"),
    (150, "a large mound of about 25 chips (green with some black)"),
    (float("inf"), "a huge towering mound of 40 or more chips (mostly black and green)"),
]


class TimelineError(ValueError):
    pass


def norm_card(code: Any) -> str:
    if not isinstance(code, str) or len(code) != 2 or code[0].upper() not in RANKS or code[1].lower() not in SUITS:
        raise TimelineError(f"Bad card code: {code!r} (use rank 23456789TJQKA + suit cdhs, e.g. 'Td')")
    return code[0].upper() + code[1].lower()


def card_words(code: str) -> str:
    c = norm_card(code)
    return f"{RANKS[c[0]]} of {SUITS[c[1]]}"


def compute_timeline(timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(timeline, dict) or not timeline.get("steps"):
        raise TimelineError("hand_timeline.steps must be a non-empty list")
    stacks = {s: float(v) for s, v in (timeline.get("start_stacks_bb") or {}).items()}
    if not stacks or any(s not in SEAT_ORDER for s in stacks):
        raise TimelineError("hand_timeline.start_stacks_bb must map seat_1..seat_6 to numbers")
    start = dict(stacks)
    pot = float(timeline.get("initial_pot_bb", 0))
    folded, all_in, revealed = set(), set(), {}
    prev_board: List[str] = []
    snaps: List[Dict[str, Any]] = []
    for i, step in enumerate(timeline["steps"]):
        stage = step.get("stage")
        if stage not in STAGE_CARDS:
            raise TimelineError(f"step {i}: bad stage {stage!r}")
        board = [norm_card(c) for c in step.get("board", [])]
        if len(board) != STAGE_CARDS[stage]:
            raise TimelineError(f"step {i}: stage {stage} needs {STAGE_CARDS[stage]} board cards, got {len(board)}")
        if board[:len(prev_board)] != prev_board:
            raise TimelineError(f"step {i}: board must extend the previous board")
        prev_board = board
        for act in step.get("actions", []):
            seat, typ = act.get("seat"), act.get("type")
            if seat not in stacks:
                raise TimelineError(f"step {i}: unknown seat {seat!r}")
            if typ not in ACTION_TYPES:
                raise TimelineError(f"step {i}: bad action type {typ!r}")
            if seat in folded:
                raise TimelineError(f"step {i}: {seat} acts after folding")
            if typ == "fold":
                folded.add(seat)
                continue
            if typ == "check":
                continue
            add = stacks[seat] if typ == "allin" else float(act.get("add_bb", 0))
            if add < 0 or (typ in ("bet", "raise", "call", "post") and add <= 0):
                raise TimelineError(f"step {i}: {typ} by {seat} needs add_bb > 0")
            add = min(add, stacks[seat])
            stacks[seat] -= add
            pot += add
            if stacks[seat] <= 0:
                all_in.add(seat)
        for seat, cards in (step.get("reveal") or {}).items():
            if seat not in stacks or not isinstance(cards, list) or len(cards) != 2:
                raise TimelineError(f"step {i}: reveal needs seat -> two cards")
            revealed[seat] = [norm_card(c) for c in cards]
        used = board + [c for cs in revealed.values() for c in cs]
        if len(set(used)) != len(used):
            raise TimelineError(f"step {i}: duplicate card among board/revealed cards")
        snaps.append({
            "id": step.get("id") or f"t{i}", "label": step.get("label", ""), "stage": stage, "board": board,
            "pot_bb": round(pot, 2), "stacks_bb": {k: round(v, 2) for k, v in stacks.items()},
            "start_stacks_bb": dict(start), "folded": sorted(folded), "all_in": sorted(all_in),
            "revealed": {k: list(v) for k, v in revealed.items()},
        })
    return snaps


def pot_tier(pot_bb: float) -> str:
    for limit, text in POT_TIERS:
        if pot_bb <= limit:
            return text
    return POT_TIERS[-1][1]


def stack_clause(stack: float, start: float, is_all_in: bool, is_folded: bool) -> str:
    if is_folded:
        return "folded, cards face-down, chips tucked neatly behind the rail"
    if is_all_in or stack <= 0:
        return "all-in, the chip rail in front is completely empty"
    ratio = stack / start if start else 1.0
    if ratio <= 0.35:
        return "a very short stack of about 3 chips"
    if ratio <= 0.7:
        return "a medium stack of about 6 chips"
    return "a tall neat stack of about 10 chips"


def board_clause(board: Sequence[str], stage: str) -> str:
    if not board:
        return "No community cards are on the felt yet"
    count = {3: "Three", 4: "Four", 5: "Five"}[len(board)]
    return f"{count} face-up miniature cards lie flat in a row at the center of the felt: " + ", ".join(card_words(c) for c in board)


def _name(roster: Dict[str, Dict[str, Any]], seat: str) -> str:
    return str(roster.get(seat, {}).get("flow_tag") or seat).lstrip("@")


def render_table_clause(snap: Dict[str, Any], visible_seats: Sequence[str], roster: Dict[str, Dict[str, Any]]) -> str:
    parts = [board_clause(snap["board"], snap["stage"]), f"The pot is {pot_tier(snap['pot_bb'])}"]
    for seat in SEAT_ORDER:
        if seat not in visible_seats or seat not in snap["stacks_bb"]:
            continue
        name = _name(roster, seat)
        if seat in snap["revealed"]:
            parts.append(f"{name}'s two hole cards lie face-up: " + " and ".join(card_words(c) for c in snap["revealed"][seat]))
        parts.append(f"In front of {name}: " + stack_clause(snap["stacks_bb"][seat], snap["start_stacks_bb"][seat],
                                                            seat in snap["all_in"], seat in snap["folded"]))
    return ". ".join(parts) + "."
