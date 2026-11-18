import urllib.request
import json
import shutil
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# 1. Create a new episode
create_payload = {
    "title": "وقتی با پاکت شاه روی فلاپ آس‌دار کالینگ استیشن میشی",
    "raw_hand_or_concept": "هیرو تو پوزیشن کات‌آف با پاکت کینگ (KK) ریز میده. اصغر فیش با آس-سه آف‌سوت کال میکنه. رو فلاپ آس میاد..."
}
req = urllib.request.Request(
    f"{BASE_URL}/api/projects",
    data=json.dumps(create_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print("Created episode ID:", res["episode_id"])
new_ep_id = res["episode_id"]

# 2. Check state.json
req = urllib.request.urlopen(f"{BASE_URL}/api/projects/{new_ep_id}")
state = json.loads(req.read().decode())
print("State raw_hand_or_concept:", state["idea"]["raw_hand_or_concept"])
assert state["idea"]["raw_hand_or_concept"] == create_payload["raw_hand_or_concept"]

# 3. Update idea via /save-idea
updated_idea = "متن ویرایش‌شده جدید: هیرو تیلت میشه و تمام چیپ‌هاش رو به اصغر فیش میده."
save_payload = {"raw_hand_or_concept": updated_idea}
req = urllib.request.Request(
    f"{BASE_URL}/api/projects/{new_ep_id}/save-idea",
    data=json.dumps(save_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print("Save-idea response:", res["status"])

# 4. Check build-prompt contains updated_idea
req = urllib.request.Request(
    f"{BASE_URL}/api/projects/{new_ep_id}/build-prompt/bible",
    data=b"{}",
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print("Prompt contains updated text?", updated_idea in res["prompt"])
assert updated_idea in res["prompt"]

# 5. Clean up test project folder
proj_path = Path("g:/poker-studio/projects") / new_ep_id
if proj_path.exists():
    shutil.rmtree(proj_path)
    print("Cleaned up test folder:", new_ep_id)

print("\nALL NEW TESTS PASSED!")
