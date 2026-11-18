import re
from typing import Any, Dict, List

LATIN_RE = re.compile(r"[A-Za-z]")
DIGIT_RE = re.compile(r"[0-9۰-۹]")
SPEAKER_RE = re.compile(r"^(NARRATOR|@\w+)$")
LETTER_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u067E\u0686\u0698\u06A9\u06AF\u06CC]")
MARK_RE = re.compile(r"[\u064B-\u0652]")
PHONETIC_TERMS = {
    "فلاپ": "فِلاپ", "ریور": "ریوِر", "تریبت": "تِریبِت",
    "چکریز": "چِکرِیز", "سیبت": "سیبِت", "بلوف": "بْلَف",
}
MIN_DIACRITIC_DENSITY = 0.12
MAX_WORDS_PER_SEC = 4.5


def validate_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []

    def add(seg_id, field, severity, message):
        issues.append({"segment_id": str(seg_id), "field": field, "severity": severity, "message": message})

    for i, seg in enumerate(segments or []):
        sid = seg.get("id") or f"index_{i}"
        sub, tts = (seg.get("subtitle_fa") or "").strip(), (seg.get("tts_fa") or "").strip()
        if not sub:
            add(sid, "subtitle_fa", "error", "subtitle_fa is empty")
        if not tts:
            add(sid, "tts_fa", "error", "tts_fa is empty")
        else:
            if LATIN_RE.search(tts):
                add(sid, "tts_fa", "error", "Latin letters found; spell English terms phonetically in Persian")
            if DIGIT_RE.search(tts):
                add(sid, "tts_fa", "warning", "Digits found; write numbers as words")
            letters, marks = len(LETTER_RE.findall(tts)), len(MARK_RE.findall(tts))
            if letters and marks / letters < MIN_DIACRITIC_DENSITY:
                add(sid, "tts_fa", "warning", f"Low diacritic density ({marks}/{letters})")
            for base, expected in PHONETIC_TERMS.items():
                if base in tts and expected not in tts:
                    add(sid, "tts_fa", "warning", f"Term '{base}' should be written '{expected}'")
        dur = seg.get("estimated_duration_sec")
        if not isinstance(dur, (int, float)) or not 1 <= dur <= 12:
            add(sid, "estimated_duration_sec", "warning", "Duration should be a number between 1 and 12")
        elif sub and len(sub.split()) / dur > MAX_WORDS_PER_SEC:
            add(sid, "estimated_duration_sec", "warning", "Text too long for the estimated duration")
        if not SPEAKER_RE.match(str(seg.get("speaker", ""))):
            add(sid, "speaker", "warning", "speaker must be NARRATOR or an @Tag from universe.json")
    return issues
