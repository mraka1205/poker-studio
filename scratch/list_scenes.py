import json

with open('projects/ep04-poker-hand/state.json', encoding='utf-8') as f:
    st = json.load(f)

for s in st['scenes']:
    print(f"{s['scene_id']}: angle={s.get('camera_angle')}, chars={s.get('characters_present')}")
