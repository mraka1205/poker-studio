import json

with open('projects/ep04-poker-hand/state.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

scenes = data.get('scenes', [])
print(f"Total scenes: {len(scenes)}")
for s in scenes:
    sid = s.get('id')
    beat = s.get('beat_index')
    dur = s.get('duration_sec')
    segs = s.get('segment_ids')
    shot_mode = s.get('shot_mode')
    media_type = s.get('media_type')
    cam = s.get('camera') or s.get('camera_angle')
    title = s.get('title')
    has_cam_dir = 'camera_direction' in s and s['camera_direction'] is not None
    has_mot_prompt = bool(s.get('motion_prompt_en'))
    word_count = len((s.get('visual_prompt_en') or '').split())
    print(f"{sid} | beat {beat} | {dur}s | {shot_mode}/{media_type} | words: {word_count} | cam_dir: {has_cam_dir} | mot: {has_mot_prompt} | cam: {cam} | title: {title}")
