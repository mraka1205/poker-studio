import urllib.request
import json

test_json = """```json
{
  "script_title": "چرا با AK روی فلاپ خشک نباید خودکشی کنیم؟",
  "segments": [
    {
      "id": "seg_01",
      "act": "Hook",
      "speaker": "NARRATOR",
      "emotion": "sarcastic",
      "subtitle_fa": "فکر کردی با دست آس و شاه شدی پادشاه کل کازینو؟ صبر کن تا فلاپ برسه!",
      "tts_fa": "فِکْر کَردی با دَسْتِ آس و شاه شُدی پادِشاهِ کُلِّ کاّزینو؟ صَبْر کُن تا فِلاپ بِرِسِه!",
      "estimated_duration_sec": 4.5
    }
  ]
}
```"""

body = json.dumps({"json_content": test_json}).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/projects/ep01-sample/import-json/script",
    data=body,
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print("Import status:", res["status"])
print("Imported segments count:", len(res["state"]["script"]["segments"]))
