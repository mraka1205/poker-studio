import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test(name, fn):
    try:
        fn()
        print(f"PASS: {name}")
    except Exception as e:
        print(f"FAIL: {name} -> {e}")
        sys.exit(1)

def check_projects():
    req = urllib.request.urlopen(f"{BASE_URL}/api/projects")
    data = json.loads(req.read().decode())
    assert len(data["projects"]) > 0
    assert data["projects"][0]["episode_id"] == "ep01-sample"

def check_load_state():
    req = urllib.request.urlopen(f"{BASE_URL}/api/projects/ep01-sample")
    data = json.loads(req.read().decode())
    assert data["episode_id"] == "ep01-sample"
    assert len(data["script"]["segments"]) > 0

def check_build_prompts():
    for stage in ["bible", "script", "characters", "scenes"]:
        req = urllib.request.Request(
            f"{BASE_URL}/api/projects/ep01-sample/build-prompt/{stage}",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        res = json.loads(urllib.request.urlopen(req).read().decode())
        assert len(res["prompt"]) > 500
        assert res["stage"] == stage

def check_import_bible():
    sample_bible = {
        "concept_summary": {
            "theme": "چرا با AK روی فلاپ خشک نباید خودکشی کنیم؟",
            "poker_lesson": "قانون فولد به چک‌ریز",
            "gto_vs_exploit": "فولد بالاترین EV را دارد"
        },
        "hand_details": {
            "game_type": "NLH",
            "hero_cards": "A♠ K♥",
            "effective_stack_bb": 100
        },
        "archetypes": [{"name": "کامبیز", "role": "HERO"}],
        "comedy_beats": ["شوخی اول تست", "شوخی دوم تست"]
    }
    body = json.dumps({"json_content": sample_bible}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/projects/ep01-sample/import-json/bible",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode())
    assert res["status"] == "success"

def check_subtitles():
    req = urllib.request.Request(
        f"{BASE_URL}/api/projects/ep01-sample/generate_subtitles",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode())
    assert res["status"] == "success"
    assert res["segment_count"] > 0

def check_settings():
    req = urllib.request.urlopen(f"{BASE_URL}/api/settings")
    res = json.loads(req.read().decode())
    assert "openrouter_model" in res

    body = json.dumps({"openrouter_model": "google/gemini-2.5-flash"}).encode("utf-8")
    req2 = urllib.request.Request(
        f"{BASE_URL}/api/settings",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    res2 = json.loads(urllib.request.urlopen(req2).read().decode())
    assert res2["status"] == "success"

test("List projects", check_projects)
test("Load state", check_load_state)
test("Build all 4 AI Studio mega-prompts", check_build_prompts)
test("Import Bible JSON", check_import_bible)
test("Generate Subtitles (.srt)", check_subtitles)
test("Settings read and save", check_settings)

print("\nALL VERIFICATIONS PASSED!")
