import pytest
from backend.services import table_state as ts


def tl():
    return {"start_stacks_bb": {"seat_1": 100, "seat_2": 100, "seat_5": 100}, "initial_pot_bb": 1.5, "steps": [
        {"id": "t0", "label": "Deal", "stage": "preflop", "board": [], "actions": []},
        {"id": "t1", "label": "3-bet call", "stage": "preflop", "board": [], "actions": [
            {"seat": "seat_1", "type": "raise", "add_bb": 9}, {"seat": "seat_5", "type": "call", "add_bb": 9},
            {"seat": "seat_2", "type": "fold"}]},
        {"id": "t2", "label": "Flop", "stage": "flop", "board": ["8s", "4d", "2c"], "actions": [
            {"seat": "seat_1", "type": "bet", "add_bb": 6}, {"seat": "seat_5", "type": "raise", "add_bb": 22}]},
        {"id": "t3", "label": "Shove", "stage": "flop", "board": ["8s", "4d", "2c"], "actions": [{"seat": "seat_1", "type": "allin"}]},
    ]}


def test_numbers_and_monotonicity():
    s = ts.compute_timeline(tl())
    assert [x["pot_bb"] for x in s][:3] == [1.5, 19.5, 47.5]
    pots = [x["pot_bb"] for x in s]
    assert pots == sorted(pots)
    for a, b in zip(s, s[1:]):
        assert all(b["stacks_bb"][k] <= a["stacks_bb"][k] for k in a["stacks_bb"])
    assert "seat_1" in s[3]["all_in"] and "seat_2" in s[1]["folded"]


def test_clauses():
    s = ts.compute_timeline(tl())
    roster = {"seat_1": {"flow_tag": "@Arash"}, "seat_5": {"flow_tag": "@Bijan"}}
    text = ts.render_table_clause(s[3], ["seat_1", "seat_5"], roster)
    assert "eight of spades, four of diamonds, two of clubs" in text
    assert "In front of Arash: all-in" in text and "huge" in text or "large" in text
    assert "No community cards" in ts.render_table_clause(s[0], ["seat_1"], roster)
    assert ts.pot_tier(4.5).startswith("a tiny cluster")


@pytest.mark.parametrize("mutate", [
    lambda t: t["steps"][2].update(board=["8s", "4d"]),
    lambda t: t["steps"][1]["actions"].append({"seat": "seat_9", "type": "call", "add_bb": 1}),
    lambda t: t["steps"][2].update(board=["8s", "8S", "2c"]),
    lambda t: t["steps"][1]["actions"].append({"seat": "seat_2", "type": "call", "add_bb": 1}),
])
def test_invalid_timelines(mutate):
    t = tl()
    mutate(t)
    with pytest.raises(ts.TimelineError):
        ts.compute_timeline(t)
