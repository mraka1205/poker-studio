import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test():
    print("--- 1. Testing Projects List & Universe Preservation ---")
    r = requests.get(f"{BASE_URL}/api/projects")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    projects = r.json().get("projects", [])
    project_ids = [p["episode_id"] for p in projects]
    print(f"Active projects: {project_ids}")
    for exp in ["ep01-sample", "ep02--playwithjj", "ep03-poker-hand"]:
        assert exp in project_ids, f"Project {exp} missing!"
    print("Projects preserved OK.")

    r_uni = requests.get(f"{BASE_URL}/api/universe")
    assert r_uni.status_code == 200, f"Universe status: {r_uni.status_code}"
    uni = r_uni.json()
    assert uni.get("version") == "1.2.0" or uni.get("universe_version") == "1.2.0"
    print("Universe preserved OK.")

    print("\n--- 2. Testing Scene Prompt Builder (Master Continuity + Seated Neighbors) ---")
    r_prompt = requests.post(f"{BASE_URL}/api/projects/ep03-poker-hand/build-prompt/scenes")
    assert r_prompt.status_code == 200, f"Prompt builder failed: {r_prompt.text}"
    p_data = r_prompt.json()
    prompt_text = p_data.get("prompt", "")
    
    assert "[Episode_Scene_1_Master]" in prompt_text, "Missing [Episode_Scene_1_Master] reference lock!"
    assert "SEATED NEIGHBORS" in prompt_text, "Missing SEATED NEIGHBORS in prompt!"
    assert "table_state_en" in prompt_text, "Missing table_state_en in prompt!"
    assert "adjacent_players" in prompt_text, "Missing adjacent_players in prompt!"
    assert "@Room_Master" in prompt_text, "Missing @Room_Master in prompt!"
    assert "vertical 9:16" in prompt_text, "Missing vertical 9:16 in prompt!"
    print("Scene prompt builder contains all continuity rules and seating calculations.")

    print("\n--- 3. Testing Import JSON with table_state_en and adjacent_players ---")
    # Sample scene payload
    sample_payload = {
        "json_content": {
            "scenes": [
                {
                    "scene_id": "scene_01",
                    "segment_ids": ["seg_01"],
                    "duration_sec": 2.0,
                    "scene_title_fa": "نمای مستر معرف میز و شروع دست",
                    "shot_mode": "static_zoom",
                    "camera_effect": "zoom_in",
                    "camera_angle": "@Room_Master Wide Establishing Shot",
                    "characters_present": ["@Arash", "@Bijan"],
                    "adjacent_players": ["@Arash (seat_1)", "@Bijan (seat_5)"],
                    "table_state_en": "Preflop: 4.5 BB pot, no community cards, Bijan's tea glass and tasbih on right felt, Arash 100BB stack on left",
                    "visual_prompt_en": "Handcrafted needle-felted stop-motion animation style, wide establishing master shot at @Room_Master showing 6-max oval table with Arash (@Arash) at seat 1 and Bijan (@Bijan) at seat 5. Soft warm studio macro lighting, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16",
                    "motion_prompt_en": "",
                    "target_video_sec": 2.0,
                    "poker_hud_overlay": {
                        "hero_hand": "A♠ K♥",
                        "board": "Preflop Deal",
                        "pot_bb": 4.5,
                        "action_badge": "Hero Deals AK Offsuit"
                    },
                    "sfx_cue": "card_deal"
                },
                {
                    "scene_id": "scene_02",
                    "segment_ids": ["seg_02"],
                    "duration_sec": 2.2,
                    "scene_title_fa": "تریبِت آرش و واکنش زیرچشمی بیژن",
                    "shot_mode": "static_zoom",
                    "camera_effect": "zoom_in",
                    "camera_angle": "@Seat_1 Medium Close-Up",
                    "characters_present": ["@Arash"],
                    "adjacent_players": ["@Bijan (seat_5, soft out-of-focus shoulder at frame edge)"],
                    "table_state_en": "Preflop 3-Bet: 19.5 BB pot pushed towards center, no community cards on green felt yet",
                    "visual_prompt_en": "Maintain exact visual continuity, character seating positions, chip stack colors, and table prop placement matching [Episode_Scene_1_Master]. Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_1 on Arash (@Arash) chest-up. In background behind him is seat 1 landmark: dark brick wall with warm bookshelf. On right edge, soft out-of-focus wool shoulder of Bijan (@Bijan). Vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16",
                    "motion_prompt_en": "",
                    "target_video_sec": 2.0,
                    "poker_hud_overlay": {
                        "hero_hand": "A♠ K♥",
                        "board": "No Cards Yet",
                        "pot_bb": 19.5,
                        "action_badge": "Hero 3-Bets 9BB | Bijan Calls"
                    },
                    "sfx_cue": "chip_splash"
                }
            ]
        }
    }
    
    # We test JSON import on ep03-poker-hand
    r_import = requests.post(f"{BASE_URL}/api/projects/ep03-poker-hand/import-json/scenes", json=sample_payload)
    assert r_import.status_code == 200, f"Import scenes failed: {r_import.text}"
    saved_state = r_import.json().get("state", {})
    saved_scenes = saved_state.get("scenes", [])
    assert len(saved_scenes) >= 2, f"Expected at least 2 scenes, got {len(saved_scenes)}"
    assert saved_scenes[0].get("table_state_en") == sample_payload["json_content"]["scenes"][0]["table_state_en"]
    assert saved_scenes[1].get("adjacent_players") == sample_payload["json_content"]["scenes"][1]["adjacent_players"]
    print("Import JSON preserves table_state_en and adjacent_players correctly.")

    print("\n--- 4. Testing update_scene_details endpoint ---")
    r_up = requests.post(f"{BASE_URL}/api/projects/ep03-poker-hand/scenes/scene_01/update", json={
        "table_state_en": "Updated table state test",
        "adjacent_players": ["@Bijan (seat_5)"]
    })
    assert r_up.status_code == 200, f"Update failed: {r_up.text}"
    up_scene = r_up.json().get("scene", {})
    assert up_scene.get("table_state_en") == "Updated table state test"
    assert up_scene.get("adjacent_players") == ["@Bijan (seat_5)"]
    print("Scene update endpoint verified.")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 100%")

if __name__ == "__main__":
    test()
