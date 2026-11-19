from typing import Any, Dict, Iterable, List, Optional

FORBIDDEN = ("--ar", "--v ", "youtube", "instagram", "12fps", "brass chandelier", "felt chips",
             "[", "]", "{", "}", "@", "rick and morty")
MIN_WORDS, MAX_WORDS = 120, 400
VARIETY_SHOTS = {"topdown_pot", "ots_duel", "chips_macro"}


def lint_prompt(prompt: str, required_substrings: Iterable[str] = (), min_words: int = MIN_WORDS,
                max_words: int = MAX_WORDS) -> List[str]:
    p = prompt or ""
    low = p.lower()
    errs: List[str] = []
    n = len(p.split())
    if n < min_words or n > max_words:
        errs.append(f"image_prompt_en has {n} words (need {min_words}-{max_words})")
    for bad in FORBIDDEN:
        if bad in low:
            errs.append(f"image_prompt_en contains forbidden token {bad!r}")
    for req in required_substrings:
        if req and req not in p:
            errs.append(f"image_prompt_en is missing required text: {req[:60]!r}")
    return errs


def lint_sequence(specs: List[Optional[Dict[str, Any]]]) -> List[str]:
    errs: List[str] = []
    prev_key, prev_shot, run, prev_step = None, None, 0, -1
    for i, sp in enumerate(specs):
        if not isinstance(sp, dict):
            continue
        shot = sp.get("shot_type")
        key = (shot, sp.get("camera_angle_id"), sp.get("focal"))
        if i == 0 and shot != "wide_master":
            errs.append("scene 1: shot_type must be wide_master (it is the episode master reference frame)")
        if key == prev_key:
            errs.append(f"scene {i + 1}: same shot_type, angle and focal as the previous scene")
        run = run + 1 if shot == prev_shot else 1
        if run >= 3:
            errs.append(f"scene {i + 1}: shot_type {shot!r} used 3 times in a row")
        step = sp.get("timeline_step")
        if isinstance(step, int):
            if step < prev_step:
                errs.append(f"scene {i + 1}: timeline_step {step} goes backwards (previous {prev_step})")
            prev_step = step
        prev_key, prev_shot = key, shot
    if len(specs) >= 6 and not any(isinstance(s, dict) and s.get("shot_type") in VARIETY_SHOTS for s in specs[1:]):
        errs.append("storyboard with 6+ scenes needs at least one topdown_pot, ots_duel or chips_macro shot")
    return errs
