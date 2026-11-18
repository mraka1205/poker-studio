import json

with open('projects/ep04-poker-hand/state.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data.get('scenes', []):
    print(f"=== {s['id']} (beat {s.get('beat_index')}, {s.get('duration_sec')}s) ===")
    print(f"Title: {s.get('title')}")
    print(f"Segments: {s.get('segment_ids')}")
    print(f"Camera: {s.get('camera')}")
    print(f"Characters: {s.get('characters_present')}")
    print(f"HUD: {s.get('poker_table_state')}")
    print(f"Shot Mode: {s.get('shot_mode')}")
    print(f"Current Prompt Start: {(s.get('visual_prompt_en') or '')[:80]}...")
    print()
