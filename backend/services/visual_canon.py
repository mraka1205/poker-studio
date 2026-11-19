"""Single source of truth for global visual constants and seed data for projects/universe.json."""

STYLE_LOCK = ("Handcrafted needle-felted stop-motion miniature: fuzzy wool fibers, stitched real-fabric clothing, "
              "glass-bead eyes, handmade imperfections, macro-lens photography.")
COMPOSITION_RULE = "Vertical 9:16 frame, subject inside the central 60%, bottom 20% calm and uncluttered for subtitles."
NEGATIVE_BLOCK = ("Avoid: text or logos (except rank and suit pips on playing cards), human skin, plastic or CGI look, "
                  "extra characters or limbs, floating chips or cards, borders.")

EMOTION_KEYS = ("neutral", "thinking", "shock", "triumph", "bet")
EMOTION_ALIASES = {
    "panic": "shock", "tilt": "shock", "fear": "shock", "surprise": "shock",
    "smug": "triumph", "win": "triumph", "bluff": "thinking", "calculating": "thinking",
    "raise": "bet", "call": "bet", "allin": "bet", "all_in": "bet", "calm": "neutral", "deadpan": "neutral",
}

LIGHTING_MOODS = {
    "neutral": "Lighting: warm amber pool of light from the overhead pendant lamp, soft shadows, gentle rim light on the wool fibers.",
    "tension": "Lighting: dimmer warm overhead pendant key light with a cool purple neon rim light from the far doorway, deeper shadows.",
    "triumph": "Lighting: brighter golden overhead pendant key light, warm glow on the chips and wool fibers.",
    "tilt": "Lighting: harsh slightly red-tinted overhead pendant key light, small hard shadows under brows and chips.",
}
DEFAULT_MOOD_FOR_EMOTION = {"neutral": "neutral", "thinking": "tension", "shock": "tension", "triumph": "triumph", "bet": "tension"}

# mode: single | props | wide | topdown | duel ; angle: "seat" (focal character's seat angle) or a fixed camera_angles id
SHOT_LIBRARY = {
    "wide_master": {"angle": "room_master", "mode": "wide", "neighbors": False,
        "framing": "wide establishing shot of the whole 6-max table and room with every seated character visible",
        "lens": "28mm macro-wide lens, deep depth of field"},
    "isometric_overview": {"angle": "room_add", "mode": "wide", "neighbors": False,
        "framing": "elevated three-quarters isometric macro establishing shot of the 6-max poker table and room",
        "lens": "35mm macro lens, moderate depth of field"},
    "closeup_seat": {"angle": "seat", "mode": "single", "neighbors": True,
        "framing": "tight chest-up close-up of the focal puppet",
        "lens": "85mm macro portrait lens, shallow depth of field"},
    "medium_seat": {"angle": "seat", "mode": "single", "neighbors": True,
        "framing": "waist-up medium shot of the focal puppet with hands and chips on the rail visible",
        "lens": "50mm macro lens, moderate depth of field"},
    "low_angle_hero": {"angle": "seat", "mode": "single", "neighbors": True,
        "framing": "low camera at table-felt level looking up at the focal puppet, heroic and menacing",
        "lens": "35mm macro lens, shallow depth of field"},
    "reaction_insert": {"angle": "seat", "mode": "single", "neighbors": False,
        "framing": "extreme close-up on the focal puppet's face and glass-bead eyes, everything else softly blurred",
        "lens": "100mm macro lens, very shallow depth of field"},
    "chips_macro": {"angle": "seat", "mode": "props", "neighbors": False,
        "framing": "extreme macro of the chips and cards on the felt in front of the focal puppet, whose torso is softly blurred behind",
        "lens": "100mm macro lens, very shallow depth of field"},
    "topdown_pot": {"angle": "room_topdown", "mode": "topdown", "neighbors": False,
        "framing": "straight top-down view onto the felt showing only hands, chips and cards, no faces",
        "lens": "overhead macro lens, everything in sharp focus"},
    "ots_duel": {"angle": "room_ots", "mode": "duel", "neighbors": False,
        "framing": "over-the-shoulder duel shot with the dark slightly blurred shoulder and hand of the foreground puppet and sharp focus on the focal puppet across the table",
        "lens": "70mm macro lens, shallow depth of field"},
}

SEED_ENV_CANON = {
    "table_en": "an oval 6-max poker table covered in fuzzy emerald-green wool felt with a dark brown hand-stitched leather armrest rail and a thin white embroidered betting line",
    "table_short_en": "fuzzy emerald-green wool felt and a dark brown hand-stitched leather rail",
    "chips_en": "Miniature round ceramic poker chips in white, red, green and black",
    "lamp_en": "one tiny black industrial pendant lamp hanging above the center of the table",
    "room_en": "dark needle-felted brick walls, a miniature woven Persian rug under the table and dark padded leather chairs",
}

SEED_CHARACTERS = {
    "@Arash": {
        "dna_block_en": "slender, slightly hunched needle-felted wool puppet with messy dark brown felted hair, thin round black wire-frame spectacles, a navy-blue knitted zip-up hoodie with small cyan grid embroidery, dark rolled-up wool trousers, small white felt sneakers and a tiny crumpled pocket notebook",
        "short_look_en": "a navy knitted hoodie and round wire glasses",
        "acting_beats_en": {
            "neutral": "sits slightly hunched with a thumb and forefinger resting on the rim of his glasses, the pocket notebook flat beside his chips",
            "thinking": "pushes his wire glasses up his nose with one felt finger while counting outs on the other hand, brows knotted",
            "shock": "bead eyes wide, mouth a tight small line, a tiny felt sweat bead on his temple, both hands frozen above the table",
            "triumph": "sits upright with a small smug half-smile, glasses glinting, one hand tapping the notebook",
            "bet": "pushes a neat stack of red chips forward with both hands, eyes locked on the opponent"}},
    "@Bijan": {
        "dna_block_en": "stout dad-bod needle-felted wool puppet with receding salt-and-pepper curly wool hair, a thick bushy dark-gray felt mustache, an open-collar burnt-orange and teal geometric-pattern felt shirt over a white undershirt, brown wool trousers, dark slip-on loafers, amber prayer beads in the left hand and a slim-waisted glass tea estekan in the right hand",
        "short_look_en": "an orange-and-teal patterned shirt and a bushy gray mustache",
        "acting_beats_en": {
            "neutral": "leans back relaxed with one elbow on the leather rail, tea glass in his right hand, amber prayer beads looped over his left fingers",
            "thinking": "squints one eye at the opponent over the rim of the tea glass while his thumb rolls one prayer bead",
            "shock": "eyebrows raised high, tea glass paused halfway to his mouth, bead eyes round and innocent",
            "triumph": "broad warm grin under the bushy mustache, tea glass raised slightly, other hand pulling the chips closer",
            "bet": "slides a single short stack of red chips forward with calm fingertips, still holding the prayer beads"}},
    "@Rahim": {
        "dna_block_en": "frail, slightly stooped needle-felted wool puppet with sparse white wool hair, thick bushy white eyebrows, a thin white mustache, large vintage bifocal glasses low on the nose, a heavy knitted beige cardigan over a buttoned shirt, high-waisted dark brown pleated wool trousers and leather slippers",
        "short_look_en": "a beige knitted cardigan and large bifocal glasses",
        "acting_beats_en": {
            "neutral": "sits stooped with both arms crossed tightly over his chest, chin tucked, glasses low on his nose",
            "thinking": "peers over the top of his bifocals at his two cards, lips pressed thin",
            "shock": "bushy white eyebrows shot up, mouth slightly open, hands clamped around his small chip stack",
            "triumph": "a tiny hidden micro-smirk, arms still crossed, a brass lucky coin resting on his neat chip stack",
            "bet": "slowly nudges a few chips forward with trembling fingers while the other hand guards his stack"}},
    "@Farzad": {
        "dna_block_en": "muscular, broad-shouldered needle-felted wool puppet with sharp faded dark wool hair, a trimmed beard, a fitted black velvet button-up shirt open at the collar over a thick shiny gold chain, rolled sleeves showing small stitched forearm tattoos, a chunky gold bracelet and watch, dark trousers and glossy loafers",
        "short_look_en": "a black velvet shirt and a thick gold chain",
        "acting_beats_en": {
            "neutral": "sprawls back in the chair with his chest out, one hand idly shuffling a stack of chips, gold chain catching the light",
            "thinking": "narrowed eyes and a crooked grin, tapping chips against the felt in a quick rhythm",
            "shock": "a theatrical shrug with palms up, eyebrows raised, mock-innocent grin",
            "triumph": "arrogant smirk with one raised eyebrow, leaning forward with both arms spread to rake in the pot",
            "bet": "shoves a huge pile of chips to the center with a flat open hand without looking at his cards"}},
    "@Keyvan": {
        "dna_block_en": "lean, upright needle-felted wool puppet with neat dark hair in a clean side part, a sharp angular face with trimmed dark stubble, dark-tinted rectangular glasses, a fitted charcoal-gray wool turtleneck, tailored black trousers, a matte-black wristwatch and dark suede shoes",
        "short_look_en": "a charcoal turtleneck and dark-tinted glasses",
        "acting_beats_en": {
            "neutral": "sits perfectly upright with hands steepled under his chin, expressionless, dark glasses level",
            "thinking": "stone-still stare at the opponent over steepled fingers, a tall neat tower of chips in front of him",
            "shock": "one barely raised eyebrow above the dark glasses, otherwise unmoved",
            "triumph": "a tiny micro-smirk of quiet satisfaction while squaring a chip tower with two fingers",
            "bet": "pushes a single chip forward with two fingers, very slowly, eyes never leaving the opponent"}},
}
