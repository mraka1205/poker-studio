from backend.services import visual_canon as vc

BEATS = {k: f"shows {k} acting" for k in vc.EMOTION_KEYS}


def make_universe():
    def char(i, tag, seat, dna, look):
        return {"id": i, "flow_tag": tag, "default_seat": seat, "dna_block_en": dna, "short_look_en": look,
                "acting_beats_en": dict(BEATS), "face_sheet_image_path": f"/media/universe/{i}_face.jpg",
                "body_sheet_image_path": f"/media/universe/{i}_body.jpg"}
    chars = [char("char_a", "@Arash", "seat_1", "slender needle-felted wool puppet with round wire spectacles", "a navy hoodie"),
             char("char_k", "@Keyvan", "seat_2", "lean needle-felted wool puppet with dark-tinted glasses", "a charcoal turtleneck"),
             char("char_b", "@Bijan", "seat_5", "stout needle-felted wool puppet with a bushy gray mustache", "an orange patterned shirt")]
    ids = ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "room_master", "room_topdown", "room_ots"]
    angles = [{"id": a, "flow_tag": "@" + a, "background_landmarks_en": f"landmarks behind {a}",
               "reference_image_path": f"/media/universe/{a}.jpg"} for a in ids]
    return {"environment": {"canon_en": dict(vc.SEED_ENV_CANON), "camera_angles": angles}, "characters": chars}


def media_files(universe):
    names = [a["reference_image_path"] for a in universe["environment"]["camera_angles"]]
    for c in universe["characters"]:
        names += [c["face_sheet_image_path"], c["body_sheet_image_path"]]
    return names


def make_timeline():
    return {"start_stacks_bb": {"seat_1": 100, "seat_2": 100, "seat_5": 100}, "initial_pot_bb": 1.5, "steps": [
        {"id": "t0", "label": "Deal", "stage": "preflop", "board": [], "actions": []},
        {"id": "t1", "label": "Arash 3-bets to 9 BB, Bijan calls", "stage": "preflop", "board": [], "actions": [
            {"seat": "seat_1", "type": "raise", "add_bb": 9}, {"seat": "seat_5", "type": "call", "add_bb": 9},
            {"seat": "seat_2", "type": "fold"}]},
        {"id": "t2", "label": "Flop", "stage": "flop", "board": ["8s", "4d", "2c"], "actions": [
            {"seat": "seat_1", "type": "bet", "add_bb": 6}, {"seat": "seat_5", "type": "raise", "add_bb": 22}]},
        {"id": "t3", "label": "Arash shoves", "stage": "flop", "board": ["8s", "4d", "2c"],
         "actions": [{"seat": "seat_1", "type": "allin"}]}]}


def make_state(ep="ep99-test"):
    specs = [
        {"shot_type": "wide_master", "timeline_step": 0},
        {"shot_type": "closeup_seat", "focal": "@Arash", "emotion": "thinking", "timeline_step": 1},
        {"shot_type": "chips_macro", "focal": "@Bijan", "emotion": "bet", "timeline_step": 2},
        {"shot_type": "ots_duel", "focal": "@Bijan", "ots_from": "@Arash", "emotion": "triumph", "timeline_step": 3},
        {"shot_type": "topdown_pot", "timeline_step": 3},
        {"shot_type": "reaction_insert", "focal": "@Arash", "emotion": "shock", "mood": "tension", "timeline_step": 3}]
    return {"episode_id": ep, "hand_timeline": make_timeline(),
            "characters": [{"id": "char_a", "flow_tag": "@Arash", "assigned_seat": "seat_1"},
                           {"id": "char_k", "flow_tag": "@Keyvan", "assigned_seat": "seat_2"},
                           {"id": "char_b", "flow_tag": "@Bijan", "assigned_seat": "seat_5"}],
            "scenes": [{"scene_id": f"scene_{i + 1:02d}", "scene_spec": s} for i, s in enumerate(specs)]}
