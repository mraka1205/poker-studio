# -*- coding: utf-8 -*-
"""
Full storyboard builder for Ep04 strictly adhering to 04-scene-director.md.
"""
import json
import sys

MASTER_LOCK = (
    "Maintain exact visual continuity, character seating positions, chip stack colors, "
    "table felt textures, and lighting geometry matching [Episode_Scene_1_Master]."
)

STYLE_LOCK = (
    "Handcrafted needle-felted stop-motion animation style, tactile fuzzy wool fiber textures, "
    "visible subtle fuzz, miniature stitched fabric clothing, soft warm overhead studio macro lighting, "
    "shallow depth of field, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16"
)

scenes_data = [
    # Scene 01
    {
        "id": "scene_01",
        "beat_index": 1,
        "segment_ids": ["seg_01"],
        "duration_sec": 2.0,
        "title": "نمای معرف میز - شروع دست با حضور هر پنج بازیکن",
        "scene_title_fa": "نمای معرف میز - شروع دست با حضور هر پنج بازیکن",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_Master Wide Establishing Shot",
        "camera_angle": "@Room_Master Wide Establishing Shot",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "wide establishing overview of the entire 6-max oval table, players, and overhead industrial chandelier",
            "end_focus_region": "closer push toward center table felt focusing on Rahim hunched at seat 3 and his protected chip stack",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Gentle, cinematic slow zoom-in from the wide 9:16 room master establishing shot into the center table felt, emphasizing the start of the historic poker hand"
        },
        "characters_present": ["@Arash", "@Keyvan", "@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Arash at seat_1 (far left edge)",
            "@Keyvan at seat_2 (upper left)",
            "@Rahim at seat_3 (center top)",
            "@Farzad at seat_4 (upper right)",
            "@Bijan at seat_5 (far right edge)",
            "seat_6 empty at bottom foreground"
        ],
        "table_state_en": "Preflop start: 1.5 BB pot of miniature wool felt chips in center, no community cards on emerald-green wool felt, Bijan's miniature glass estekan of steaming amber tea and amber tasbih on seat 5 side table, Arash's tablet and neat 100BB chip stacks at seat 1, Keyvan's ultra-neat tall chip towers at seat 2, Rahim's protected chip stack with felted hand guards at seat 3, Farzad's messy chip pile at seat 4, seat 6 empty",
        "visual_prompt_en": (
            "Handcrafted needle-felted stop-motion animation style, wide establishing master shot of the entire 6-max oval poker table inside @PokerRoom. "
            "Seated clockwise around the table: @Arash at seat_1 in a navy knitted hoodie with neat upright posture behind his tablet and neat 100BB chip stacks; "
            "@Keyvan at seat_2 in a sleek charcoal turtleneck with stone-cold composure behind ultra-neat tall chip towers; "
            "@Rahim at seat_3 in a heavy knitted cream cardigan, hunched stoically guarding his chips; "
            "@Farzad at seat_4 in an open-collar black velvet shirt with a gold chain, leaning back aggressively by a messy chip pile; "
            "@Bijan at seat_5 in a patterned paisley shirt with a cheerful smile beside a steaming miniature glass tea estekan and amber tasbih. "
            "Seat_6 remains empty. In the center, an initial 1.5 BB pot of miniature wool felt chips rests on fuzzy emerald-green table felt under a warm hanging industrial pendant lamp. "
            "Miniature Persian rug below the table, felted brick walls with ambient neon rim glow. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦ (Rahim)",
            "board": "Preflop",
            "pot_bb": 1.5,
            "action_badge": "Rahim UTG After 2 Hours"
        },
        "sfx_cue": "card_deal"
    },

    # Scene 02
    {
        "id": "scene_02",
        "beat_index": 2,
        "segment_ids": ["seg_01"],
        "duration_sec": 1.8,
        "title": "چهره خسته رحیم بعد از دو ساعت فولد",
        "scene_title_fa": "چهره خسته رحیم بعد از دو ساعت فولد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "medium close-up from chest up showing Rahim slouched behind his protected chips",
            "end_focus_region": "tighter macro push into Rahim's weary wrinkled face and vintage bifocal glasses",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Subtle slow zoom-in pushing into Rahim's weary expression and furrowed brows after two hours of disciplined folding"
        },
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal wool shoulder on left frame edge)",
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on right frame edge)"
        ],
        "table_state_en": "Preflop initial deal: 1.5 BB pot in center, no community cards on green felt, Rahim's small protected 100BB chip stack fortified behind his trembling needle-felted hands",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) from the chest up. "
            "His deeply wrinkled needle-felted wool face conveys sheer exhaustion after two hours of folding, bushy white eyebrows furrowed low over large vintage bifocal glasses perched on his nose, his thin white mustache downturned. "
            "His trembling felted wire-frame hands rest tightly guarded around his miniature chip stack on the fuzzy emerald-green felt. "
            "On the left frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan) at seat_2 anchors the spatial geometry; on the right frame edge, the out-of-focus black velvet shoulder of Farzad (@Farzad) at seat_4 is visible. "
            "Background displays the seat_3 signature landmark: floor-to-ceiling pleated dark velvet fabric curtains with miniature stitched folds and warm golden-amber light leaking through. "
            "In foreground, the 1.5 BB pot rests untouched on green felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 1.8,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 1.5,
            "action_badge": "Rahim Staring at Aces"
        },
        "sfx_cue": "heartbeat"
    },

    # Scene 03
    {
        "id": "scene_03",
        "beat_index": 3,
        "segment_ids": ["seg_01"],
        "duration_sec": 1.5,
        "title": "دست‌های لرزون رحیم به سمت چیپ‌ها",
        "scene_title_fa": "دست‌های لرزون رحیم به سمت چیپ‌ها",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_3 Extreme Close-Up on Hands",
        "camera_angle": "@Seat_3 Extreme Close-Up on Hands",
        "camera_effect": "zoom_in",
        "camera_direction": None,
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus edge on left)",
            "@Farzad (seat_4, soft out-of-focus edge on right)"
        ],
        "table_state_en": "Preflop initial deal: 1.5 BB pot, no community cards, Rahim's protected chip stack with a miniature brass coin protector on green felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, extreme macro close-up framed at @Seat_3 focusing downward on Rahim's (@Rahim) trembling needle-felted wire-frame hands. "
            "Wrinkled fuzzy wool skin textures, delicate textile fibers on knuckles, and miniature stitched cuffs of his beige cardigan are captured in extreme macro detail as his trembling fingers hover millimeters above his protected stack of miniature red chips. "
            "In the soft out-of-focus upper background, his hunched torso and the deep amber glow of the pleated velvet curtain landmark are visible. "
            "The fuzzy emerald-green wool felt surface reveals fine stray fibers under warm directional macro spotlight, with the 1.5 BB pot just off-frame. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady extreme close-up on needle-felted puppet Rahim (@Rahim) at @Seat_3. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "His wrinkly felted fingers tremble visibly with delicate stop-motion micro-jitters, slowly uncurling from his protective chest posture "
            "and hovering with dramatic hesitation above his miniature chip stack. All chips remain firmly flat on the emerald wool felt with realistic felt friction, "
            "no flying or airborne objects. Pure handcrafted stop-motion comedy feel."
        ),
        "target_video_sec": 1.5,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 1.5,
            "action_badge": "Trembling Hands Reach for Chips"
        },
        "sfx_cue": "heartbeat"
    },

    # Scene 04
    {
        "id": "scene_04",
        "beat_index": 4,
        "segment_ids": ["seg_02"],
        "duration_sec": 2.2,
        "title": "رحیم با غرور از مینی‌ریز می‌گوید",
        "scene_title_fa": "رحیم با غرور از مینی‌ریز می‌گوید",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "medium close-up on Rahim's stooped posture and smug expression",
            "end_focus_region": "tight push into Rahim's haughty micro-smirk and bifocal glasses",
            "zoom_intensity": 1.16,
            "easing": "smooth",
            "camera_prompt_en": "Cinematic slow zoom-in on Rahim as a condescending micro-smirk breaks across his wrinkled puppet face"
        },
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal shoulder on left frame edge)",
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on right frame edge)"
        ],
        "table_state_en": "Preflop: 1.5 BB pot in center, no community cards, Rahim's hand hovering over chips as he prepares his min-raise",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) from the chest up. "
            "A smug, condescending micro-smirk emerges beneath his thin white wool mustache, one bushy eyebrow tilted upward in rare pride as his bead eyes peek over the rims of his vintage bifocal glasses. "
            "His needle-felted right hand proudly grips a small stack of chips while his left hand rests firmly on the leather rail. "
            "On the left frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan) at seat_2; on the right frame edge, the out-of-focus shoulder of Farzad (@Farzad) at seat_4. "
            "Background features the seat_3 signature pleated dark velvet curtains with warm golden-amber backlight. Fuzzy green table felt and 1.5 BB pot in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 1.5,
            "action_badge": "Rahim: 'Mini-Raise Time'"
        },
        "sfx_cue": "chip_slide"
    },

    # Scene 05
    {
        "id": "scene_05",
        "beat_index": 5,
        "segment_ids": ["seg_02"],
        "duration_sec": 2.0,
        "title": "مینی‌ریز ۲ بیگ بلایند رحیم",
        "scene_title_fa": "مینی‌ریز ۲ بیگ بلایند رحیم",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": None,
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal wool shoulder on left)",
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on right)"
        ],
        "table_state_en": "Preflop min-raise: pot grows to 3.5 BB as Rahim slides a tiny 2 BB stack of miniature red chips across the green felt, no community cards",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) chest-up. "
            "His needle-felted wool hands slide a tiny 2 BB stack of miniature red chips across the white embroidered betting line on the fuzzy emerald-green felt, his face tight with pompous pride. "
            "On the left frame edge, the soft out-of-focus charcoal wool profile of Keyvan (@Keyvan) at seat_2; on the right frame edge, the out-of-focus dark velvet sleeve of Farzad (@Farzad) at seat_4. "
            "Background shows the signature dark pleated velvet curtains with warm golden rim light leaking through the seams. "
            "The pot grows to 3.5 BB on the felt, no community cards yet. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Rahim (@Rahim) at @Seat_3. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "With slow, deliberate hesitation and trembling felt fingers, he slides a neat 2 BB stack of miniature red chips forward flat along the fuzzy green wool felt over the betting line, "
            "then gives a stiff, pompous puppet head nod. All chips slide smoothly on felt surface with zero bounce or airborne movement. Pure tactile stop-motion comedy feel."
        ),
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Rahim Min-Raises to 2 BB"
        },
        "sfx_cue": "chip_slide"
    },

    # Scene 06
    {
        "id": "scene_06",
        "beat_index": 6,
        "segment_ids": ["seg_03"],
        "duration_sec": 2.0,
        "title": "نگاه نگران آرش و کیوان به هم",
        "scene_title_fa": "نگاه نگران آرش و کیوان به هم",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_1 to @Seat_2 Two-Shot",
        "camera_angle": "@Seat_1 to @Seat_2 Two-Shot",
        "camera_effect": "pan_left",
        "camera_direction": {
            "motion_type": "pan_left_to_right",
            "start_focus_region": "Arash at seat 1 clutching his tablet in sheer panic",
            "end_focus_region": "Keyvan at seat 2 maintaining an unreadable stone-cold gaze",
            "zoom_intensity": 1.12,
            "easing": "smooth",
            "camera_prompt_en": "Cinematic lateral pan from left to right moving from Arash's panicked mathematical shock across to Keyvan's ice-cold appraisal"
        },
        "characters_present": ["@Arash", "@Keyvan"],
        "adjacent_players": [
            "@Arash at seat_1 (left)",
            "@Keyvan at seat_2 (right)",
            "@Rahim at seat_3 (soft out-of-focus shoulder at far right frame edge)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Rahim's 2 BB bet stack resting in center, Arash's tablet and Keyvan's neat stacks visible",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, cinematic two-shot framed across @Seat_1 and @Seat_2. "
            "Arash (@Arash) on the left in a navy knit hoodie and round spectacles turns with wide, panicked bead eyes toward Keyvan (@Keyvan) on the right. "
            "Keyvan sits upright in his charcoal turtleneck, expression utterly stone-cold and composed behind dark-tinted glasses. "
            "On the far right frame edge, the soft out-of-focus beige shoulder of Rahim (@Rahim) at seat_3 anchors table geometry. "
            "Background transitions smoothly from seat_1's warm LED-lit bookshelf with miniature trophies to seat_2's framed pop-art canvas on dark felted brick. "
            "In foreground, the 3.5 BB pot sits on fuzzy emerald-green felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "K♠ Q♠ (Arash)",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Arash & Keyvan Exchange Glances"
        },
        "sfx_cue": "record_scratch"
    },

    # Scene 07
    {
        "id": "scene_07",
        "beat_index": 7,
        "segment_ids": ["seg_03"],
        "duration_sec": 2.0,
        "title": "آرش وحشت‌زده رنج رحیم را حساب می‌کند",
        "scene_title_fa": "آرش وحشت‌زده رنج رحیم را حساب می‌کند",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_1 Medium Close-Up",
        "camera_angle": "@Seat_1 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "subtle_tilt_shake",
            "start_focus_region": "medium close-up on Arash's hunched chest and nervous hand posture",
            "end_focus_region": "tight macro focus on Arash's sweating brow and askew round glasses",
            "zoom_intensity": 1.18,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Nervous handheld-style micro-shake with tight zoom-in capturing Arash's escalating anxiety as he calculates mathematical odds"
        },
        "characters_present": ["@Arash"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal shoulder on right frame edge)",
            "@Rahim (seat_3, far right, soft out-of-focus profile)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Arash's K♠ Q♠ face down in front of him, tablet with scribbled math odds",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_1 on Arash (@Arash) from the chest up. "
            "His needle-felted brow furrows in extreme anxiety, one finger nervously pushing his thick round spectacles up his fuzzy nose while a tiny crafted felt sweat drop gleams on his temple. "
            "His left hand frantically taps his pocket tablet displaying scribbled percentages and odds on the brown leather rail. "
            "On the right frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan) at seat_2 is clearly visible. "
            "In background behind Arash sits seat_1 landmark: dark needle-felted brick wall with warm LED-lit wooden bookshelves holding miniature vintage poker books. "
            "Fuzzy green table felt with 3.5 BB pot in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "K♠ Q♠",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Arash Calculating Rahim's Range"
        },
        "sfx_cue": "heartbeat"
    },

    # Scene 08
    {
        "id": "scene_08",
        "beat_index": 8,
        "segment_ids": ["seg_03"],
        "duration_sec": 1.8,
        "title": "فولد آرش با شاه-بی‌بی سوتد",
        "scene_title_fa": "فولد آرش با شاه-بی‌بی سوتد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_1 Medium Close-Up",
        "camera_angle": "@Seat_1 Medium Close-Up",
        "camera_effect": "pan_left",
        "camera_direction": {
            "motion_type": "tilt_down",
            "start_focus_region": "Arash's defeated face and slumped shoulders",
            "end_focus_region": "Arash's felt fingers sliding K♠ Q♠ cards flat into the muck",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Smooth vertical tilt-down tracking from Arash's resigned face down to his hands mucking the suited broadway cards"
        },
        "characters_present": ["@Arash"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal wool shoulder on right frame edge)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Arash slides K♠ Q♠ face down toward the muck line on the emerald felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_1 on Arash (@Arash) from the chest up. "
            "His posture slumps in defeated mathematical resignation, eyes closed behind his round black spectacles as his wire-frame felt fingers reluctantly slide his two miniature cards K♠ Q♠ face down flat across the fuzzy emerald wool felt toward the dealer muck line. "
            "On the right frame edge, the soft out-of-focus charcoal shoulder of Keyvan (@Keyvan) at seat_2 anchors spatial continuity. "
            "Background displays the dark needle-felted exposed brick and trophy shelf of seat_1. "
            "Tactile felted table rail, 3.5 BB pot resting on center felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 1.8,
        "poker_table_state": {
            "hero_hand": "K♠ Q♠",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Arash Folds"
        },
        "sfx_cue": "card_fold"
    },

    # Scene 09
    {
        "id": "scene_09",
        "beat_index": 9,
        "segment_ids": ["seg_04"],
        "duration_sec": 2.2,
        "title": "چهره سنگی کیوان در سکوت مطلق",
        "scene_title_fa": "چهره سنگی کیوان در سکوت مطلق",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_2 Medium Close-Up",
        "camera_angle": "@Seat_2 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "static_hold",
            "start_focus_region": "medium close-up on Keyvan's upright posture, tinted glasses, and tall chip towers",
            "end_focus_region": "static hold with razor-sharp macro focus emphasizing lethal unreadable poker face",
            "zoom_intensity": 1.05,
            "easing": "smooth",
            "camera_prompt_en": "Deadpan static hold with subtle imperceptible micro-push accentuating Keyvan's chilling silence and calculating shark demeanor"
        },
        "characters_present": ["@Keyvan"],
        "adjacent_players": [
            "@Arash (seat_1, soft out-of-focus navy hoodie on left frame edge)",
            "@Rahim (seat_3, soft out-of-focus cream cardigan on right frame edge)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Keyvan's 8♥ 7♥ face down, his ultra-neat multi-layer tall chip towers standing tall",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_2 on Keyvan (@Keyvan) from the chest up. "
            "His needle-felted puppet face is an impenetrable mask of pure stone-cold discipline, trimmed dark wool beard, dark-tinted glasses reflecting pinpoint studio lights, hands calmly steepled together in front of towering, multi-colored stacks of miniature chips arranged with geometric precision. "
            "On the left frame edge, the soft out-of-focus navy blue knit shoulder of Arash (@Arash); on the right frame edge, the soft out-of-focus beige cardigan shoulder of Rahim (@Rahim). "
            "Background displays seat_2 landmark: dark felted brick wall with a tiny framed miniature pop-art canvas under a soft spotlight. "
            "Foreground shows fuzzy emerald-green table felt and 3.5 BB pot. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "8♥ 7♥ (Keyvan)",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Keyvan Stone-Cold"
        },
        "sfx_cue": "silence_sting"
    },

    # Scene 10
    {
        "id": "scene_10",
        "beat_index": 10,
        "segment_ids": ["seg_04"],
        "duration_sec": 2.0,
        "title": "کیوان کارت‌ها را آرام زمین می‌گذارد",
        "scene_title_fa": "کیوان کارت‌ها را آرام زمین می‌گذارد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_2 Medium Close-Up",
        "camera_angle": "@Seat_2 Medium Close-Up",
        "camera_effect": "zoom_out",
        "camera_direction": {
            "motion_type": "tilt_down",
            "start_focus_region": "Keyvan's calm face and steepled hands",
            "end_focus_region": "Keyvan's felt hand releasing 8♥ 7♥ smoothly flat onto the table felt",
            "zoom_intensity": 1.14,
            "easing": "smooth",
            "camera_prompt_en": "Smooth vertical tilt-down capturing Keyvan's emotionless hand movement gently laying down his suited connectors without a whisper"
        },
        "characters_present": ["@Keyvan"],
        "adjacent_players": [
            "@Arash (seat_1, soft out-of-focus navy sleeve on left frame edge)",
            "@Rahim (seat_3, soft out-of-focus cream cardigan on right frame edge)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Keyvan lays 8♥ 7♥ face down flat on the felt, tall chip towers untouched",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_2 on Keyvan (@Keyvan) from the chest up. "
            "Without the slightest change in his stoic expression, his needle-felted charcoal-sleeved arm extends forward with surgical calm, laying his two miniature cards 8♥ 7♥ face down flat on the fuzzy green wool felt next to his massive chip towers. "
            "On the left frame edge, the out-of-focus navy shoulder of Arash (@Arash); on the right frame edge, the out-of-focus beige shoulder of Rahim (@Rahim). "
            "Background shows the dark brick wall and miniature art frame of seat_2. "
            "Pristine emerald wool felt and 3.5 BB pot in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "8♥ 7♥",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Keyvan Folds Silently"
        },
        "sfx_cue": "card_fold"
    },

    # Scene 11
    {
        "id": "scene_11",
        "beat_index": 11,
        "segment_ids": ["seg_05"],
        "duration_sec": 2.0,
        "title": "فرزاد هیجان‌زده آل-این می‌گوید",
        "scene_title_fa": "فرزاد هیجان‌زده آل-این می‌گوید",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_4 Medium Close-Up",
        "camera_angle": "@Seat_4 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "fast_punch_in",
            "start_focus_region": "medium close-up on Farzad's broad chest, open velvet collar, and gold chain",
            "end_focus_region": "rapid dramatic punch into Farzad's manic grinning face and raised eyebrows",
            "zoom_intensity": 1.22,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Fast aggressive punch-in on Farzad's face as he roars his blind all-in challenge across the table"
        },
        "characters_present": ["@Farzad"],
        "adjacent_players": [
            "@Rahim (seat_3, soft out-of-focus beige cardigan on left frame edge)",
            "@Bijan (seat_5, soft out-of-focus paisley shirt on right frame edge)"
        ],
        "table_state_en": "Preflop: 3.5 BB pot, no community cards, Farzad's messy chip pile in front of him, cards face down untouched",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_4 on Farzad (@Farzad) from the chest up. "
            "His puppet face is alive with theatrical bravado and street-tough energy, mouth curled in a wild challenging grin beneath a trimmed wool beard, dark eyes gleaming boldly. "
            "Wearing an unbuttoned black velvet shirt revealing a thick miniature gold chain necklace, his tattooed felt arms spread wide in a boastful gesture. "
            "On the left frame edge, the soft out-of-focus cream cardigan of Rahim (@Rahim) at seat_3; on the right frame edge, the out-of-focus paisley shirt of Bijan (@Bijan) at seat_5. "
            "Background reveals seat_4 landmark: carved wooden corner shelf with an open miniature Takhteh-Nard board. "
            "In foreground, a disorganized heap of chips sits ready on the green wool felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "7♣ 2♦ (Farzad)",
            "board": "Preflop",
            "pot_bb": 3.5,
            "action_badge": "Farzad: 'All-In!'"
        },
        "sfx_cue": "record_scratch"
    },

    # Scene 12
    {
        "id": "scene_12",
        "beat_index": 12,
        "segment_ids": ["seg_05"],
        "duration_sec": 2.2,
        "title": "شوو کورکورانه صد بیگ بلایند فرزاد",
        "scene_title_fa": "شوو کورکورانه صد بیگ بلایند فرزاد",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_4 Medium Close-Up",
        "camera_angle": "@Seat_4 Medium Close-Up",
        "camera_effect": "shake",
        "camera_direction": None,
        "characters_present": ["@Farzad"],
        "adjacent_players": [
            "@Rahim (seat_3, soft out-of-focus beige cardigan on left)",
            "@Bijan (seat_5, soft out-of-focus paisley pattern on right)"
        ],
        "table_state_en": "Preflop: pot jumps to ~103.5 BB, Farzad pushes his entire messy 100 BB stack forward in a chaotic pile, no community cards",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_4 on Farzad (@Farzad) chest-up. "
            "Both of his muscular felted arms sweep violently forward across the brown leather table rail, pushing a chaotic 100 BB avalanche of miniature chips across the fuzzy emerald-green felt into the center pot without even glancing at his two cards. "
            "On the left frame edge, the out-of-focus beige shoulder of Rahim (@Rahim) at seat_3; on the right frame edge, the out-of-focus paisley shoulder of Bijan (@Bijan) at seat_5. "
            "Background features the carved wooden corner shelf with Takhteh-Nard and miniature potted plant. "
            "Fuzzy green felt texture with the massive displaced chip pile in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Farzad (@Farzad) at @Seat_4. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "With aggressive swagger, he sweeps both felted arms forward, shoving his entire messy 100 BB pile of miniature chips flat along the fuzzy green wool felt into the center, "
            "laughing silently with head thrown back. All chips slide smoothly on felt surface with realistic stop-motion friction, no flying or airborne objects. Pure tactile stop-motion comedy feel."
        ),
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "7♣ 2♦",
            "board": "Preflop",
            "pot_bb": 103.5,
            "action_badge": "Farzad Shoves 100 BB Blind"
        },
        "sfx_cue": "all_in_alarm"
    },

    # Scene 13
    {
        "id": "scene_13",
        "beat_index": 13,
        "segment_ids": ["seg_05"],
        "duration_sec": 2.0,
        "title": "واکنش شوکه میز به آل-این فرزاد",
        "scene_title_fa": "واکنش شوکه میز به آل-این فرزاد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_Master Wide Reaction Shot",
        "camera_angle": "@Room_Master Wide Reaction Shot",
        "camera_effect": "zoom_out",
        "camera_direction": {
            "motion_type": "slow_zoom_out",
            "start_focus_region": "Farzad's chaotic all-in pile in the center of the table felt",
            "end_focus_region": "wide tableau pulling back to reveal the contrasting stunned expressions of all seated players",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Dramatic slow zoom-out revealing the full 6-max table frozen in disbelief after Farzad's wild blind 100 BB shove"
        },
        "characters_present": ["@Arash", "@Keyvan", "@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Arash at seat_1 (frozen with jaw dropped)",
            "@Keyvan at seat_2 (impassive stone-faced)",
            "@Rahim at seat_3 (eyes bulging behind glasses)",
            "@Farzad at seat_4 (arms outstretched boastfully)",
            "@Bijan at seat_5 (calmly lifting tea cup)",
            "seat_6 empty"
        ],
        "table_state_en": "Preflop: massive ~103.5 BB pot in center, no community cards, Farzad's chaotic all-in stack pushed forward, all players frozen in high-stakes tension",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, wide reaction shot of the entire 6-max oval table inside @PokerRoom. "
            "Farzad (@Farzad) at seat_4 sits with arms triumphantly raised behind his massive chaotic chip pile; "
            "Arash (@Arash) at seat_1 freezes in paralyzed shock gripping his tablet; "
            "Keyvan (@Keyvan) at seat_2 remains completely motionless with an icy stare; "
            "Rahim (@Rahim) at seat_3 stares in bug-eyed shock over his bifocals; "
            "Bijan (@Bijan) at seat_5 casually reaches for his steaming tea glass. "
            "Seat_6 empty. Center table felt displays the towering 103.5 BB pot beneath the hanging industrial lamp. "
            "Rich room landmarks: brick walls, bookshelves, takhteh-nard shelf, and tea tray. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "7♣ 2♦",
            "board": "Preflop",
            "pot_bb": 103.5,
            "action_badge": "Table Stunned"
        },
        "sfx_cue": "all_in_alarm"
    },

    # Scene 14
    {
        "id": "scene_14",
        "beat_index": 14,
        "segment_ids": ["seg_06"],
        "duration_sec": 2.2,
        "title": "بیژن یک قلپ چای می‌زند",
        "scene_title_fa": "بیژن یک قلپ چای می‌زند",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "medium close-up on Bijan holding his tea glass beside his tasbih",
            "end_focus_region": "tight macro focus on Bijan's warm twinkle and bushy mustache as he sips tea",
            "zoom_intensity": 1.16,
            "easing": "smooth",
            "camera_prompt_en": "Cozy, deliberate slow zoom-in capturing Bijan's completely unbothered demeanor and gentle tea-sipping ritual amid table madness"
        },
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on left frame edge)",
            "Empty seat_6 leather chair on right frame edge"
        ],
        "table_state_en": "Preflop: ~103.5 BB pot, no community cards, Bijan's tea estekan steaming, amber tasbih resting on side table, his 9♦ 4♣ face down on felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) from the chest up. "
            "His friendly, slightly stout dad-bod puppet figure radiates blissful unconcern, curly salt-and-pepper hair, thick dark-gray wool mustache curling into a relaxed smile, warm glass bead eyes twinkling. "
            "His right hand brings a miniature glass estekan of steaming amber tea toward his lips, while his left hand lets amber prayer beads (tasbih) rest on the leather armrest rail. "
            "On the left frame edge, the out-of-focus black velvet sleeve of Farzad (@Farzad) at seat_4; right edge shows the empty seat_6 chair. "
            "Background displays seat_5 landmark: carved wooden side table with silver tea tray and brass pistachio bowl. "
            "Fuzzy green felt with ~103.5 BB pot in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣ (Bijan)",
            "board": "Preflop",
            "pot_bb": 103.5,
            "action_badge": "Bijan Sips Tea"
        },
        "sfx_cue": "tea_sip"
    },

    # Scene 15
    {
        "id": "scene_15",
        "beat_index": 15,
        "segment_ids": ["seg_06"],
        "duration_sec": 2.0,
        "title": "کال صد بیگ بلایند بیژن با ۹ و ۴",
        "scene_title_fa": "کال صد بیگ بلایند بیژن با ۹ و ۴",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": None,
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus black velvet on left)",
            "Empty seat_6 on right"
        ],
        "table_state_en": "Preflop: pot swells to ~203.5 BB, Bijan pushes a neat 100 BB stack forward with a grin, no community cards",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) chest-up. "
            "With an effortless cheerful grin, his needle-felted arm slides a neat 100 BB stack of colorful miniature chips smoothly forward across the fuzzy green wool felt to match Farzad's bet, clutching his 9♦ 4♣ cards loosely. "
            "On the left frame edge, the soft out-of-focus black velvet shoulder of Farzad (@Farzad) at seat_4; right edge shows the empty seat_6 chair. "
            "Background highlights the silver tea tray, steaming estekan, and pistachio bowl landmark of seat_5. "
            "The pot swells to 203.5 BB on the fuzzy emerald felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Bijan (@Bijan) at @Seat_5. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "He lowers his miniature glass tea estekan onto the coaster, gives a relaxed carefree puppet nod, and casually pushes a tall 100 BB stack of miniature chips flat along the fuzzy green wool felt into the pot with a knowing smirk. "
            "No flying chips, smooth felt slide. Pure tactile stop-motion comedy feel."
        ),
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "Preflop",
            "pot_bb": 203.5,
            "action_badge": "Bijan Calls 100 BB"
        },
        "sfx_cue": "chip_splash"
    },

    # Scene 16
    {
        "id": "scene_16",
        "beat_index": 16,
        "segment_ids": ["seg_07"],
        "duration_sec": 2.2,
        "title": "رحیم با غرور پاکت آس را می‌بیند",
        "scene_title_fa": "رحیم با غرور پاکت آس را می‌بیند",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "medium close-up on Rahim's stooped posture as he glances between the two chip mounds",
            "end_focus_region": "tighter macro push into Rahim's triumphant gleaming eyes behind his bifocal glasses",
            "zoom_intensity": 1.18,
            "easing": "smooth",
            "camera_prompt_en": "Tense slow zoom-in framing Rahim's realization that his Pocket Aces are about to scoop a mammoth 300 BB pot"
        },
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal shoulder on left frame edge)",
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on right frame edge)"
        ],
        "table_state_en": "Preflop: ~203.5 BB pot, no community cards, Rahim's A♠ A♦ held tightly, his protected 100 BB chip stack ready to commit",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) from the chest up. "
            "His posture straightens with sudden majestic energy, his wrinkled wool face blooming into triumphant vindication, bushy white eyebrows raised high above thick reading glasses as he gazes at his pocket Aces A♠ A♦. "
            "Both felted hands prepare to push his fortified chip fortress forward into the center. "
            "On the left frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan); on the right frame edge, the out-of-focus shoulder of Farzad (@Farzad). "
            "Background reveals the dark pleated velvet curtains with warm golden-amber backlight. "
            "Fuzzy green wool felt with the massive 203.5 BB pot in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 203.5,
            "action_badge": "Rahim: 'Pocket Aces!'"
        },
        "sfx_cue": "chip_slide"
    },

    # Scene 17
    {
        "id": "scene_17",
        "beat_index": 17,
        "segment_ids": ["seg_07"],
        "duration_sec": 2.2,
        "title": "اسنپ-کال رحیم و رو کردن آس‌ها",
        "scene_title_fa": "اسنپ-کال رحیم و رو کردن آس‌ها",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "shake",
        "camera_direction": None,
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal on left)",
            "@Farzad (seat_4, soft out-of-focus velvet on right)"
        ],
        "table_state_en": "Preflop: pot explodes to 300 BB, Rahim shoves all his chips in and flips A♠ A♦ face up on the felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) chest-up. "
            "His wrinkled felt hands aggressively push his remaining 100 BB chip stack into the center pot and triumphantly snap-flip his two miniature cards A♠ A♦ face up flat on the fuzzy emerald wool felt before crossing his arms across his cream cardigan with an imperious smirk. "
            "On the left frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan); on the right frame edge, the out-of-focus shoulder of Farzad (@Farzad). "
            "Background shows the pleated velvet curtain landmark. "
            "The monumental 300 BB pot sits piled on green felt in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Rahim (@Rahim) at @Seat_3. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "With sudden energetic triumph, his trembling hands firmly push his remaining 100 BB chip stack forward, then snap-flip his two miniature cards A♠ A♦ face up flat on the green wool felt before folding his arms proudly. "
            "All chips and cards remain flat on felt surface. Pure tactile stop-motion comedy feel."
        ),
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Preflop",
            "pot_bb": 300.0,
            "action_badge": "Rahim Snap-Calls 100 BB"
        },
        "sfx_cue": "all_in_alarm"
    },

    # Scene 18
    {
        "id": "scene_18",
        "beat_index": 18,
        "segment_ids": ["seg_07"],
        "duration_sec": 2.0,
        "title": "نمای بالا از پات سیصد بیگ بلایند",
        "scene_title_fa": "نمای بالا از پات سیصد بیگ بلایند",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_angle": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_effect": "zoom_out",
        "camera_direction": {
            "motion_type": "slow_zoom_out",
            "start_focus_region": "macro focus on the three colossal stacks of chips in the center pot and exposed Aces",
            "end_focus_region": "wider isometric pull-back showing all cards and player hands resting along the rail",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Grand isometric slow zoom-out revealing the sheer scale of the 300 BB pot across the emerald felt"
        },
        "characters_present": ["@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Rahim at seat_3 (top)",
            "@Farzad at seat_4 (top right)",
            "@Bijan at seat_5 (bottom right)"
        ],
        "table_state_en": "Preflop: massive 300 BB pot in center, three towering chip stacks, no community cards, A♠ A♦ face up, 7♣ 2♦ and 9♦ 4♣ face down",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, isometric top-down macro shot looking directly down at the emerald-green wool felt of @Room_TopDown. "
            "In the center, a colossal 300 BB pot of miniature felt chips forms three towering mountains on the fuzzy felt. "
            "Near seat_3, Rahim's A♠ A♦ lie face up, crisp and miniature; near seat_4, Farzad's 7♣ 2♦ lie face down; near seat_5, Bijan's 9♦ 4♣ lie face down. "
            "No community cards on the felt yet. "
            "Curved hand-stitched brown leather table rail surrounds the green felt, with tiny felted hands resting along the rim under warm chandelier light. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦ vs 7♣ 2♦ vs 9♦ 4♣",
            "board": "Preflop",
            "pot_bb": 300.0,
            "action_badge": "3-Way All-In: 300 BB"
        },
        "sfx_cue": "chip_splash"
    },

    # Scene 19
    {
        "id": "scene_19",
        "beat_index": 19,
        "segment_ids": ["seg_08"],
        "duration_sec": 2.0,
        "title": "دیلر فلاپ را باز می‌کند",
        "scene_title_fa": "دیلر فلاپ را باز می‌کند",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_angle": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "tilt_down",
            "start_focus_region": "dealer's miniature felt hand sliding cards from the miniature shoe",
            "end_focus_region": "macro focus on the center felt where the first three board cards are being flipped",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Smooth vertical tilt-down tracking the dealer's felted hand burning a card and beginning the flop deal"
        },
        "characters_present": ["@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Rahim at seat_3",
            "@Farzad at seat_4",
            "@Bijan at seat_5"
        ],
        "table_state_en": "Flop: 300 BB pot, dealer's felted hand turning three miniature community cards face up on emerald felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, top-down isometric macro shot framed at @Room_TopDown over the central green wool felt. "
            "A miniature needle-felted dealer's hand with fine wool stitching burns one card and delicately begins to turn three miniature printed community cards face up on the fuzzy emerald felt beside the massive 300 BB chip pot. "
            "Rahim's miniature A♠ A♦ remain face up near seat_3, while Farzad's and Bijan's cards lie face down on the felt. "
            "Tactile wool fibers, embroidered white betting lines, and the warm cone of overhead pendant macro lighting capture the intense pre-flop climax. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "Dealing Flop",
            "pot_bb": 300.0,
            "action_badge": "Dealer Burns and Turns"
        },
        "sfx_cue": "card_deal"
    },

    # Scene 20
    {
        "id": "scene_20",
        "beat_index": 20,
        "segment_ids": ["seg_08"],
        "duration_sec": 2.0,
        "title": "فلاپ ۹، ۴، ۱۰ روی نمد",
        "scene_title_fa": "فلاپ ۹، ۴، ۱۰ روی نمد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_angle": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_effect": "pan_left",
        "camera_direction": {
            "motion_type": "pan_left_to_right",
            "start_focus_region": "Rahim's exposed A♠ A♦ near seat 3",
            "end_focus_region": "pan across the three flop cards 9♣ 4♠ T♦ over to Bijan's face-down cards",
            "zoom_intensity": 1.18,
            "easing": "smooth",
            "camera_prompt_en": "Dramatic horizontal pan from Rahim's Aces across the fresh flop of 9-4-10 toward Bijan's cards to highlight the shock connection"
        },
        "characters_present": ["@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Rahim at seat_3",
            "@Farzad at seat_4",
            "@Bijan at seat_5"
        ],
        "table_state_en": "Flop: 300 BB pot, community cards 9♣ 4♠ T♦ flat on emerald felt, Bijan's 9♦ 4♣ now two pair",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, isometric top-down macro shot at @Room_TopDown focused squarely on the center table felt. "
            "Three miniature printed community cards lie flat on the fuzzy emerald wool felt: 9♣ 4♠ T♦ (Rainbow) beside the towering 300 BB chip mountain. "
            "Near seat_5, Bijan's face-down cards 9♦ 4♣ sit ominously connected to the board; near seat_3, Rahim's A♠ A♦ remain face up. "
            "Extreme macro detail captures fine woven paper texture, fuzzy green felt fibers, and warm spotlight reflections on chip edges. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "9♣ 4♠ T♦",
            "pot_bb": 300.0,
            "action_badge": "Flop: Bijan Hits Two Pair"
        },
        "sfx_cue": "card_deal"
    },

    # Scene 21
    {
        "id": "scene_21",
        "beat_index": 21,
        "segment_ids": ["seg_08"],
        "duration_sec": 2.0,
        "title": "پوزخند بیژن بعد از دوپر شدن",
        "scene_title_fa": "پوزخند بیژن بعد از دوپر شدن",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": None,
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus black velvet on left)",
            "Empty seat_6 on right"
        ],
        "table_state_en": "Flop: 300 BB pot, 9♣ 4♠ T♦ on felt, Bijan's tea glass steaming, Bijan smiling with two pair",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) from the chest up. "
            "His bead eyes widen in delightful micro-realization, one sculpted wool eyebrow arching upward as a knowing, smug grin spreads under his bushy salt-and-pepper mustache. "
            "His needle-felted fingers tap the brown leather rail twice in quiet satisfaction next to his steaming glass of amber tea. "
            "On the left frame edge, the out-of-focus black velvet shoulder of Farzad (@Farzad) at seat_4; right edge shows empty seat_6. "
            "Background displays the carved side table with silver tea tray and brass pistachios. "
            "Flop cards and 300 BB pot visible in foreground felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Bijan (@Bijan) at @Seat_5. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "His bead eyes widen slightly in comic recognition of his two pair (9 and 4), one wool eyebrow arches into a sly smirk, and his felt fingers tap the leather rail twice in rhythm. "
            "Handcrafted stop-motion acting with zero dialogue."
        ),
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦",
            "pot_bb": 300.0,
            "action_badge": "Bijan: Two Pair!"
        },
        "sfx_cue": "heartbeat"
    },

    # Scene 22
    {
        "id": "scene_22",
        "beat_index": 22,
        "segment_ids": ["seg_09"],
        "duration_sec": 2.0,
        "title": "ترن ۲ روی نمد",
        "scene_title_fa": "ترن ۲ روی نمد",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_angle": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "overview of the four board cards and the 300 BB pot",
            "end_focus_region": "macro push into the newly dealt 2♥ community card",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Tense slow zoom-in focusing tightly onto the newly dealt Turn card 2♥ resting on the green felt"
        },
        "characters_present": ["@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Rahim at seat_3",
            "@Farzad at seat_4",
            "@Bijan at seat_5"
        ],
        "table_state_en": "Turn: 300 BB pot, board 9♣ 4♠ T♦ 2♥, four community cards flat on felt, Bijan still leading with two pair",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, isometric top-down macro shot at @Room_TopDown over the central green wool felt. "
            "Four miniature community cards lie flat in a neat row on the fuzzy emerald felt: 9♣ 4♠ T♦ 2♥ beside the colossal 300 BB pot. "
            "Rahim's A♠ A♦ remain exposed near seat_3, still trailing Bijan's hidden two pair; Farzad's 7♣ 2♦ catches a pair of deuces, still far behind. "
            "Soft overhead pendant light casts warm shadows across card edges and wool fibers. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "9♣ 4♠ T♦ 2♥",
            "pot_bb": 300.0,
            "action_badge": "Turn: 2♥"
        },
        "sfx_cue": "card_deal"
    },

    # Scene 23
    {
        "id": "scene_23",
        "beat_index": 23,
        "segment_ids": ["seg_09"],
        "duration_sec": 2.0,
        "title": "ریور ۴ و فول‌هاوس بیژن",
        "scene_title_fa": "ریور ۴ و فول‌هاوس بیژن",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_angle": "@Room_TopDown Isometric Top-Down Table Shot",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "fast_punch_in",
            "start_focus_region": "overview of the full 5-card board",
            "end_focus_region": "rapid dramatic punch into the river 4♥ cementing Bijan's Full House",
            "zoom_intensity": 1.25,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Fast dramatic punch-in on the fateful River 4♥ locking in Bijan's monstrous Full House over Rahim's Aces"
        },
        "characters_present": ["@Rahim", "@Farzad", "@Bijan"],
        "adjacent_players": [
            "@Rahim at seat_3",
            "@Farzad at seat_4",
            "@Bijan at seat_5"
        ],
        "table_state_en": "River: 300 BB pot, complete board 9♣ 4♠ T♦ 2♥ 4♥ flat on felt, Bijan makes full house (4s full of 9s) crushing Rahim's pocket Aces",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, isometric top-down macro shot at @Room_TopDown on the center table felt. "
            "Five miniature community cards complete the board flat on the fuzzy emerald wool felt: 9♣ 4♠ T♦ 2♥ 4♥ beside the monumental 300 BB pot. "
            "Near seat_5, Bijan's cards 9♦ 4♣ now combine with the board for an unbeatable Full House, 4s full of 9s; near seat_3, Rahim's A♠ A♦ are completely crushed. "
            "Crisp miniature card illustrations and tactile wool fuzz textures captured in dramatic overhead macro lighting. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "River: Bijan Full House!"
        },
        "sfx_cue": "card_deal"
    },

    # Scene 24
    {
        "id": "scene_24",
        "beat_index": 24,
        "segment_ids": ["seg_09"],
        "duration_sec": 2.0,
        "title": "واکنش بیژن به فول‌هاوس شدن",
        "scene_title_fa": "واکنش بیژن به فول‌هاوس شدن",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "shake",
        "camera_direction": None,
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus black velvet on left)",
            "Empty seat_6 on right"
        ],
        "table_state_en": "River: 300 BB pot, full board 9♣ 4♠ T♦ 2♥ 4♥, Bijan turns over 9♦ 4♣ full house with a cheerful toast",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) from the chest up. "
            "He leans back comfortably against his dark leather chair with a radiant, carefree grin, lifting his miniature glass tea estekan in a cheerful silent toast toward Rahim while turning over his 9♦ 4♣ cards face up on the rail. "
            "On the left frame edge, the out-of-focus black velvet shoulder of Farzad (@Farzad); on the right, empty seat_6. "
            "Background shows the carved wooden side table with amber tea tray and brass pistachios. "
            "Full board and 300 BB pot in foreground green felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Bijan (@Bijan) at @Seat_5. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "He leans back comfortably into his leather chair, raises his miniature glass tea estekan toward the table in a silent celebratory toast, "
            "and winks playfully at Rahim with one sculpted eye. Pure tactile stop-motion comedy."
        ),
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Bijan Scoops 300 BB"
        },
        "sfx_cue": "chip_splash"
    },

    # Scene 25
    {
        "id": "scene_25",
        "beat_index": 25,
        "segment_ids": ["seg_10"],
        "duration_sec": 2.2,
        "title": "رحیم گیج و مبهوت",
        "scene_title_fa": "رحیم گیج و مبهوت",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_3 Medium Close-Up",
        "camera_angle": "@Seat_3 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "fast_punch_in",
            "start_focus_region": "medium close-up on Rahim's stooped chest and frozen arms",
            "end_focus_region": "tight punch into Rahim's petrified wide-open eyes and sagging jaw",
            "zoom_intensity": 1.22,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Fast dramatic punch-in targeting Rahim's frozen expression of utter catastrophic shock as reality sinks in"
        },
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus charcoal shoulder on left frame edge)",
            "@Farzad (seat_4, soft out-of-focus black velvet shoulder on right frame edge)"
        ],
        "table_state_en": "Showdown: 300 BB pot, full board 9♣ 4♠ T♦ 2♥ 4♥, Rahim's A♠ A♦ exposed and cracked, Rahim petrified in horror",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_3 on Rahim (@Rahim) from the chest up. "
            "His wrinkled needle-felted face is completely petrified in comic horror, mouth dropped wide open beneath his white mustache, glass bead eyes bulging wildly behind crooked bifocal reading glasses as he stares at Bijan's 9-4. "
            "Both trembling felt hands freeze mid-air above his lost chips. "
            "On the left frame edge, the soft out-of-focus charcoal wool shoulder of Keyvan (@Keyvan); on the right frame edge, the out-of-focus shoulder of Farzad (@Farzad). "
            "Background shows the dark pleated velvet curtains of seat_3. "
            "Foreground green wool felt with the full board and giant pot. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Rahim: 'What Happened?!'"
        },
        "sfx_cue": "record_scratch"
    },

    # Scene 26
    {
        "id": "scene_26",
        "beat_index": 26,
        "segment_ids": ["seg_10"],
        "duration_sec": 2.0,
        "title": "کلوزآپ آس‌های رحیم و دست‌ها روی سر",
        "scene_title_fa": "کلوزآپ آس‌های رحیم و دست‌ها روی سر",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_3 Extreme Close-Up on Cards",
        "camera_angle": "@Seat_3 Extreme Close-Up on Cards",
        "camera_effect": "shake",
        "camera_direction": {
            "motion_type": "subtle_tilt_shake",
            "start_focus_region": "macro focus on the cracked pair of Aces lying flat on the green felt",
            "end_focus_region": "subtle shaky push toward Rahim's trembling hands clutching his head in the soft background",
            "zoom_intensity": 1.15,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Traumatic macro micro-shake framing the dead Pocket Aces on the felt while Rahim's felt hands clutch his head in despair"
        },
        "characters_present": ["@Rahim"],
        "adjacent_players": [
            "@Keyvan (seat_2, soft out-of-focus edge on left)",
            "@Farzad (seat_4, soft out-of-focus edge on right)"
        ],
        "table_state_en": "Showdown: 300 BB pot, board 9♣ 4♠ T♦ 2♥ 4♥, Rahim's A♠ A♦ flat on felt, his felted hands clutching his head in despair",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, extreme macro close-up framed at @Seat_3 looking low along the table felt. "
            "In sharp foreground focus, Rahim's two miniature cards A♠ A♦ lie flat and lifeless on the fuzzy emerald wool felt beside the embroidered white line. "
            "In the soft out-of-focus background, Rahim's trembling felted hands clutch both sides of his head in theatrical agony, cream cardigan rumpled, mouth agape. "
            "On the left and right frame edges, soft out-of-focus shoulders of Keyvan and Farzad anchor table continuity. "
            "Warm directional spotlight highlighting delicate stray wool fibers on the felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "A♠ A♦",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Aces Cracked"
        },
        "sfx_cue": "heartbeat"
    },

    # Scene 27
    {
        "id": "scene_27",
        "beat_index": 27,
        "segment_ids": ["seg_11"],
        "duration_sec": 2.2,
        "title": "تیلت شدید فرزاد",
        "scene_title_fa": "تیلت شدید فرزاد",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_4 Medium Close-Up",
        "camera_angle": "@Seat_4 Medium Close-Up",
        "camera_effect": "shake",
        "camera_direction": None,
        "characters_present": ["@Farzad"],
        "adjacent_players": [
            "@Rahim (seat_3, soft out-of-focus cream cardigan on left)",
            "@Bijan (seat_5, soft out-of-focus paisley on right)"
        ],
        "table_state_en": "Showdown: 300 BB pot, board 9♣ 4♠ T♦ 2♥ 4♥, Farzad's 7♣ 2♦ exposed in defeat, Farzad in explosive tilt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_4 on Farzad (@Farzad) from the chest up. "
            "His puppet face is contorted into exaggerated cartoon rage, red felt wool cheeks puffing, dark beard bristling, thick gold chain bouncing against his chest as his tattooed arms shake in furious disbelief at Bijan's 9-4. "
            "On the left frame edge, the out-of-focus cream cardigan of Rahim (@Rahim) at seat_3; on the right frame edge, the out-of-focus paisley shirt of Bijan (@Bijan) at seat_5. "
            "Background displays seat_4 landmark: carved wooden corner shelf with Takhteh-Nard. "
            "The 300 BB pot and 7♣ 2♦ cards visible on green felt in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Farzad (@Farzad) at @Seat_4. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "His felted face contorts into extreme comic rage and tilt, red felt cheeks bulging, his head shaking violently side to side as he throws both arms in the air in theatrical exasperation. "
            "Pure stop-motion animation slapstick."
        ),
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "7♣ 2♦",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Farzad on Mega-Tilt"
        },
        "sfx_cue": "record_scratch"
    },

    # Scene 28
    {
        "id": "scene_28",
        "beat_index": 28,
        "segment_ids": ["seg_11"],
        "duration_sec": 2.0,
        "title": "مشت کوبیدن فرزاد روی میز",
        "scene_title_fa": "مشت کوبیدن فرزاد روی میز",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_4 Medium Close-Up",
        "camera_angle": "@Seat_4 Medium Close-Up",
        "camera_effect": "shake",
        "camera_direction": {
            "motion_type": "fast_punch_in",
            "start_focus_region": "Farzad raising both clenched felt fists high above his head",
            "end_focus_region": "violent macro punch-in as his fist slams the brown leather table rail making nearby chips rattle",
            "zoom_intensity": 1.22,
            "easing": "dramatic_punch",
            "camera_prompt_en": "Fast explosive punch-in with table impact shock as Farzad slams his fist onto the padded leather rail"
        },
        "characters_present": ["@Farzad"],
        "adjacent_players": [
            "@Rahim (seat_3, soft out-of-focus cream cardigan on left frame edge)",
            "@Bijan (seat_5, soft out-of-focus paisley shirt on right frame edge)"
        ],
        "table_state_en": "Showdown: 300 BB pot, board 9♣ 4♠ T♦ 2♥ 4♥, Farzad slams fist, chips rattling on green felt",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_4 on Farzad (@Farzad) from the chest up. "
            "He slams a clenched needle-felted fist heavily down onto the dark brown leather table rail in sheer exasperation, causing loose miniature chips and his exposed 7♣ 2♦ cards to rattle on the fuzzy green wool felt. "
            "His teeth are clenched under his trimmed beard, eyes narrowed in volcanic frustration. "
            "On the left frame edge, the out-of-focus cream cardigan of Rahim (@Rahim) at seat_3; on the right frame edge, the out-of-focus paisley shirt of Bijan (@Bijan) at seat_5. "
            "Background shows the Takhteh-Nard corner shelf landmark. "
            "Foreground green felt with scattered chips and full board. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "7♣ 2♦",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Farzad Slams Table"
        },
        "sfx_cue": "table_slam"
    },

    # Scene 29
    {
        "id": "scene_29",
        "beat_index": 29,
        "segment_ids": ["seg_12"],
        "duration_sec": 2.2,
        "title": "پوزخند و حرف‌های بیژن",
        "scene_title_fa": "پوزخند و حرف‌های بیژن",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_in",
            "start_focus_region": "medium close-up on Bijan shrugging his shoulders with a tea cup in hand",
            "end_focus_region": "tighter macro push into Bijan's hilarious knowing wink and broad mustache grin",
            "zoom_intensity": 1.16,
            "easing": "smooth",
            "camera_prompt_en": "Charming slow zoom-in on Bijan's nonchalant shrug and playful wink as he delivers his immortal punchline"
        },
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus fuming black velvet shoulder on left frame edge)",
            "Empty seat_6 on right frame edge"
        ],
        "table_state_en": "Showdown: 300 BB pot ready to be scooped, full board 9♣ 4♠ T♦ 2♥ 4♥, Bijan's tea glass and amber tasbih on table",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) from the chest up. "
            "He gives a hilarious nonchalant shoulder shrug, raising both hands with an innocent, broad toothy grin under his bushy salt-and-pepper mustache, one eye winking playfully across the table at Arash. "
            "Holding his miniature tea glass lightly, amber prayer beads draped over his wrist, he embodies the supreme carefree calling station. "
            "On the left frame edge, the fuming out-of-focus black velvet shoulder of Farzad (@Farzad) at seat_4; on the right, empty seat_6. "
            "Background displays the carved side table with silver tea tray and brass pistachios. "
            "Monumental 300 BB pot on foreground green wool felt. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Bijan: 'I Came to Keep You Company'"
        },
        "sfx_cue": "tea_sip"
    },

    # Scene 30
    {
        "id": "scene_30",
        "beat_index": 30,
        "segment_ids": ["seg_12"],
        "duration_sec": 2.2,
        "title": "بیژن پات سیصد بیگ بلایند را جمع می‌کند",
        "scene_title_fa": "بیژن پات سیصد بیگ بلایند را جمع می‌کند",
        "media_type": "ai_video",
        "shot_mode": "ai_video",
        "camera": "@Seat_5 Medium Close-Up",
        "camera_angle": "@Seat_5 Medium Close-Up",
        "camera_effect": "zoom_out",
        "camera_direction": None,
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus black velvet on left)",
            "Empty seat_6 on right"
        ],
        "table_state_en": "Showdown: Bijan rakes the entire 300 BB pot across the green felt toward himself, board 9♣ 4♠ T♦ 2♥ 4♥",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) chest-up. "
            "With wide joyful arms, his needle-felted hands sweep smoothly across the fuzzy emerald wool felt, raking the gigantic 300 BB mountain of colorful miniature chips toward his chest, his face glowing with pure unearned poker happiness. "
            "On the left frame edge, the out-of-focus slumped shoulder of Farzad (@Farzad) at seat_4; on the right, empty seat_6. "
            "Background features the carved wooden side table with the silver tea tray and brass bowl. "
            "Full board 9♣ 4♠ T♦ 2♥ 4♥ visible on green felt in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": (
            "Steady medium close-up on needle-felted puppet Bijan (@Bijan) at @Seat_5. Tactile 12fps stop-motion puppet animation, "
            "subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). "
            "He stretches both fuzzy wool arms wide across the felt, gathering the massive 300 BB mountain of miniature colorful chips smoothly toward his chest in a greedy, joyful hug, "
            "chuckling silently. All chips drag flat along the wool felt with realistic textile friction, no flying pieces. Pure tactile stop-motion comedy feel."
        ),
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 300.0,
            "action_badge": "Bijan Wins 300 BB"
        },
        "sfx_cue": "chip_splash"
    },

    # Scene 31
    {
        "id": "scene_31",
        "beat_index": 31,
        "segment_ids": ["seg_13"],
        "duration_sec": 2.2,
        "title": "لبخند خونسرد کیوان در سکوت",
        "scene_title_fa": "لبخند خونسرد کیوان در سکوت",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_2 Medium Close-Up",
        "camera_angle": "@Seat_2 Medium Close-Up",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "static_hold",
            "start_focus_region": "medium close-up on Keyvan's poised posture, dark-tinted glasses, and immaculate chip towers",
            "end_focus_region": "static hold with razor-sharp macro focus emphasizing his quiet, subtle smirk",
            "zoom_intensity": 1.06,
            "easing": "smooth",
            "camera_prompt_en": "Chillingly calm static hold on Keyvan as a tiny micro-smirk of pure pro satisfaction curls on his stoic lips"
        },
        "characters_present": ["@Keyvan"],
        "adjacent_players": [
            "@Arash (seat_1, soft out-of-focus navy hoodie on left frame edge)",
            "@Rahim (seat_3, soft out-of-focus slumping cream cardigan on right frame edge)"
        ],
        "table_state_en": "Aftermath: Bijan's 300 BB pot stacked at seat 5, board 9♣ 4♠ T♦ 2♥ 4♥, Keyvan's neat stacks untouched, Keyvan smiling faintly",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_2 on Keyvan (@Keyvan) from the chest up. "
            "While chaos and ruins engulf the table around him, Keyvan remains the picture of serene, calculated pro composure. "
            "His dark-tinted glasses catch a pinpoint reflection of the overhead chandelier, and a faint, knowing micro-smirk grazes his lips beneath neatly trimmed stubble. "
            "His towering, multi-colored stacks of chips remain completely pristine and untouched. "
            "On the left frame edge, the out-of-focus navy shoulder of Arash (@Arash); on the right frame edge, the out-of-focus slumping beige shoulder of Rahim (@Rahim). "
            "Background shows seat_2 dark brick wall and pop-art canvas. "
            "Clean emerald felt in foreground. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.2,
        "poker_table_state": {
            "hero_hand": "8♥ 7♥ (folded)",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 0,
            "action_badge": "Keyvan's Silent Smirk"
        },
        "sfx_cue": "silence_sting"
    },

    # Scene 32
    {
        "id": "scene_32",
        "beat_index": 32,
        "segment_ids": ["seg_13"],
        "duration_sec": 2.0,
        "title": "جادوی چایی بیژن - جمع‌بندی طلایی",
        "scene_title_fa": "جادوی چایی بیژن - جمع‌بندی طلایی",
        "media_type": "static_image",
        "shot_mode": "static_zoom",
        "camera": "@Seat_5 Extreme Close-Up on Tea Glass",
        "camera_angle": "@Seat_5 Extreme Close-Up on Tea Glass",
        "camera_effect": "zoom_in",
        "camera_direction": {
            "motion_type": "slow_zoom_out",
            "start_focus_region": "extreme macro focus on the glowing amber tea estekan with delicate rising steam wisp",
            "end_focus_region": "gentle pull-back revealing the amber tasbih and Bijan's colossal 300 BB chip mountain in background",
            "zoom_intensity": 1.15,
            "easing": "smooth",
            "camera_prompt_en": "Poetic slow zoom-out pulling back from the glowing estekan of Persian tea to reveal the mammoth 300 BB chip stack, framing the golden takeaway"
        },
        "characters_present": ["@Bijan"],
        "adjacent_players": [
            "@Farzad (seat_4, soft out-of-focus shoulder on left frame edge)",
            "Empty seat_6 on right frame edge"
        ],
        "table_state_en": "Aftermath: 300 BB pot stacked at seat 5, board 9♣ 4♠ T♦ 2♥ 4♥, Bijan's amber tea glass glowing under chandelier light, amber tasbih beside it",
        "visual_prompt_en": (
            f"{MASTER_LOCK} "
            "Handcrafted needle-felted stop-motion animation style, extreme macro close-up framed at @Seat_5 on Bijan's miniature Persian tea tray. "
            "In crystal-clear macro focus sits an authentic miniature glass estekan of hot dark amber tea with a delicate spun-wool steam wisp rising, flanked by glossy amber prayer beads (tasbih) and a brass bowl of miniature pistachios on the carved wooden side table. "
            "In the soft-focus warm background, Bijan's triumphant dad-bod smile and his newly won mountain of 300 BB chips gleam under the warm overhead industrial pendant light. "
            "On the left frame edge, the out-of-focus shoulder of Farzad at seat_4 anchors spatial continuity. "
            f"{STYLE_LOCK}"
        ),
        "motion_prompt_en": "",
        "target_video_sec": 2.0,
        "poker_table_state": {
            "hero_hand": "9♦ 4♣",
            "board": "9♣ 4♠ T♦ 2♥ 4♥",
            "pot_bb": 0,
            "action_badge": "Golden Takeaway: Tea Magic > Nit Folds"
        },
        "sfx_cue": "magic_chime"
    }
]

print(f"Generated {len(scenes_data)} scenes.")

# Verification pass
errors = []
for i, sc in enumerate(scenes_data, 1):
    sc_id = sc["id"]
    words = len(sc["visual_prompt_en"].split())
    if words < 80:
        errors.append(f"{sc_id}: visual_prompt_en has only {words} words (<80)")
    
    m_type = sc["media_type"]
    if m_type == "static_image":
        if not sc.get("camera_direction"):
            errors.append(f"{sc_id}: static_image missing camera_direction")
        else:
            cd = sc["camera_direction"]
            for req_key in ["motion_type", "start_focus_region", "end_focus_region", "zoom_intensity", "easing", "camera_prompt_en"]:
                if req_key not in cd:
                    errors.append(f"{sc_id}: camera_direction missing {req_key}")
        if sc.get("motion_prompt_en") != "":
            errors.append(f"{sc_id}: static_image has non-empty motion_prompt_en")
    elif m_type == "ai_video":
        if sc.get("camera_direction") is not None:
            errors.append(f"{sc_id}: ai_video must have camera_direction=None")
        if not sc.get("motion_prompt_en"):
            errors.append(f"{sc_id}: ai_video missing motion_prompt_en")
        else:
            mp = sc["motion_prompt_en"]
            if "--ar" in mp:
                errors.append(f"{sc_id}: motion_prompt_en must not contain --ar")
    else:
        errors.append(f"{sc_id}: invalid media_type {m_type}")

    if i > 1:
        if not sc["visual_prompt_en"].startswith(MASTER_LOCK):
            errors.append(f"{sc_id}: scene > 1 must start with MASTER_LOCK")
    else:
        if sc["visual_prompt_en"].startswith(MASTER_LOCK):
            errors.append(f"{sc_id}: scene 1 should NOT start with MASTER_LOCK")

if errors:
    print("VERIFICATION FAILED:")
    for err in errors:
        print("  -", err)
    sys.exit(1)
else:
    print("ALL 32 SCENES PASSED STRICT VALIDATION!")
    for sc in scenes_data:
        words = len(sc["visual_prompt_en"].split())
        print(f"  {sc['id']}: {sc['media_type']} | {words} words | cam: {sc['camera_angle'][:30]}")

# Now enrich scenes for state.json
with open("projects/ep04-poker-hand/state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

# Update state["scenes"]
enriched = []
for idx, sc in enumerate(scenes_data, 1):
    sc_id = sc["id"]
    dur = float(sc["duration_sec"])
    media_type = sc["media_type"]
    mode = sc["shot_mode"]
    hud = sc["poker_table_state"]
    img_asset = f"/media/ep04-poker-hand/assets/images/{sc_id}.png"

    enriched.append({
        "id": sc_id,
        "scene_id": sc_id,
        "beat_index": idx,
        "time_range": f"00:{(idx-1)*2:02d} - 00:{idx*2:02d}",
        "title": sc["scene_title_fa"],
        "scene_title_fa": sc["scene_title_fa"],
        "duration_sec": dur,
        "segment_ids": sc["segment_ids"],
        "characters_present": sc["characters_present"],
        "adjacent_players": sc["adjacent_players"],
        "table_state_en": sc["table_state_en"],
        "camera": sc["camera_angle"],
        "camera_angle": sc["camera_angle"],
        "media_type": media_type,
        "shot_mode": mode,
        "camera_effect": sc["camera_effect"],
        "camera_direction": sc["camera_direction"],
        "visual_prompt": sc["visual_prompt_en"],
        "visual_prompt_en": sc["visual_prompt_en"],
        "motion_prompt_en": sc["motion_prompt_en"],
        "target_video_sec": float(sc["target_video_sec"]),
        "poker_table_state": hud,
        "poker_hud_overlay": hud,
        "sfx_cue": sc["sfx_cue"],
        "visual_asset": img_asset,
        "image_path": img_asset,
        "video_path": None,
        "video_asset": None,
        "status": "ready_for_review"
    })

state["scenes"] = enriched

with open("projects/ep04-poker-hand/state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print("Saved updated scenes directly into projects/ep04-poker-hand/state.json!")
