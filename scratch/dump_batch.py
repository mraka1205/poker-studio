import json

with open('projects/universe.json', encoding='utf-8') as f:
    u = json.load(f)

with open('projects/ep04-poker-hand/state.json', encoding='utf-8') as f:
    st = json.load(f)

angle_map = {}
for a in u.get('environment', {}).get('camera_angles', []):
    angle_map[a['flow_tag']] = a['reference_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/')

char_map = {}
for c in u.get('characters', []):
    char_map[c['flow_tag']] = {
        'face': c['face_sheet_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/'),
        'body': c['body_sheet_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/')
    }

def get_scene_info(s):
    sid = s['scene_id']
    c_ang = s.get('camera_angle', '')
    ref_angle = None
    for tag in angle_map:
        if tag in c_ang:
            ref_angle = angle_map[tag]
            break
    if not ref_angle:
        if 'TopDown' in c_ang:
            ref_angle = angle_map.get('@Room_TopDown')
        elif 'Master' in c_ang:
            ref_angle = angle_map.get('@Room_Master')
        elif 'Seat_1' in c_ang:
            ref_angle = angle_map.get('@Seat_1')
        elif 'Seat_2' in c_ang:
            ref_angle = angle_map.get('@Seat_2')
        elif 'Seat_3' in c_ang:
            ref_angle = angle_map.get('@Seat_3')
        elif 'Seat_4' in c_ang:
            ref_angle = angle_map.get('@Seat_4')
        elif 'Seat_5' in c_ang:
            ref_angle = angle_map.get('@Seat_5')
        elif 'Seat_6' in c_ang:
            ref_angle = angle_map.get('@Seat_6')
        elif 'OTS' in c_ang:
            ref_angle = angle_map.get('@Room_OTS')
    
    chars = s.get('characters_present', [])
    char_ref = None
    if chars:
        main_char = chars[0]
        if main_char in char_map:
            char_ref = char_map[main_char]['face']
            
    img_paths = ["G:/poker-studio/projects/ep04-poker-hand/assets/images/scene_01.png"]
    if ref_angle:
        img_paths.append(ref_angle)
    if char_ref:
        img_paths.append(char_ref)
        
    return {
        "scene_id": sid,
        "ImageName": sid,
        "AspectRatio": "9:16",
        "ImagePaths": img_paths,
        "Prompt": s.get('visual_prompt_en') or s.get('visual_prompt')
    }

def print_batch(start_idx, end_idx):
    scenes = st['scenes'][start_idx:end_idx]
    out = []
    for s in scenes:
        info = get_scene_info(s)
        out.append(info)
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    print_batch(start, end)
