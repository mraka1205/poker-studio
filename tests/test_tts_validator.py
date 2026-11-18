from backend.services.tts_validator import validate_segments


def test_clean_segment_has_no_errors():
    seg = {"id": "seg_01", "speaker": "NARRATOR", "estimated_duration_sec": 5,
           "subtitle_fa": "فکر کردی با آس و شاه پادشاهی؟",
           "tts_fa": "فِکْر کَردی با آس و شاه پادِشاهی؟"}
    assert [i for i in validate_segments([seg]) if i["severity"] == "error"] == []


def test_latin_and_missing_diacritics_flagged():
    seg = {"id": "s", "speaker": "HERO", "estimated_duration_sec": 5,
           "subtitle_fa": "فلاپ آمد", "tts_fa": "flop فلاپ آمد"}
    msgs = " ".join(i["message"] for i in validate_segments([seg]))
    assert "Latin" in msgs and "diacritic" in msgs and "فِلاپ" in msgs and "speaker" in msgs
