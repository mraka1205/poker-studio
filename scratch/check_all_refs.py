import json

with open('projects/universe.json', encoding='utf-8') as f:
    u = json.load(f)

with open('projects/ep04-poker-hand/state.json', encoding='utf-8') as f:
    st = json.load(f)

# Camera angle mapping
angle_map = {}
for a in u.get('environment', {}).get('camera_angles', []):
    angle_map[a['flow_tag']] = a['reference_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/')

# Character mapping
char_map = {}
for c in u.get('characters', []):
    char_map[c['flow_tag']] = {
        'face': c['face_sheet_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/'),
        'body': c['body_sheet_image_path'].replace('/media/universe/', 'G:/poker-studio/projects/universe/')
    }

for s in st['scenes']:
    sid = s['scene_id']
    c_ang = s.get('camera_angle', '')
    # find tag in camera_angle
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
    
    # find character sheet
    chars = s.get('characters_present', [])
    char_ref = None
    if chars:
        main_char = chars[0]
        if main_char in char_map:
            char_ref = char_map[main_char]['face']
    
    print(f"{sid}: angle_ref={ref_angle}, char_ref={char_ref}")
