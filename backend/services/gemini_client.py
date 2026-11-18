import json
import re
from typing import Dict, Any, List, Optional
import httpx
from fastapi import HTTPException

BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"


def clean_json_text(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()
    return json.loads(cleaned)


async def list_gemini_models(api_key: str) -> List[Dict[str, Any]]:
    if not api_key or not api_key.strip():
        raise HTTPException(status_code=400, detail="کلید Gemini API وارد نشده است.")

    url = f"{BASE_GEMINI_URL}/models?key={api_key.strip()}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            res = await client.get(url)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"خطا در اتصال به Google AI Studio: {str(e)}")

    if res.status_code != 200:
        err_msg = res.text
        try:
            err_json = res.json()
            err_msg = err_json.get("error", {}).get("message", res.text)
        except Exception:
            pass
        raise HTTPException(
            status_code=res.status_code, 
            detail=f"خطای سرویس Google Gemini ({res.status_code}): {err_msg}"
        )

    data = res.json()
    models = data.get("models", [])
    valid_models = []
    for m in models:
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods or not methods:
            raw_name = m.get("name", "")
            m_id = raw_name.replace("models/", "")
            d_name = m.get("displayName") or m.get("display_name") or m_id
            valid_models.append({
                "id": m_id,
                "name": m_id,
                "clean_name": m_id,
                "display_name": d_name,
                "displayName": d_name,
                "description": m.get("description", ""),
                "version": m.get("version", "")
            })
    return valid_models


async def call_gemini_generate_content(
    api_key: str,
    model: str,
    system_instruction: str,
    prompt: str,
    temperature: float = 0.4
) -> Dict[str, Any]:
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=400,
            detail="کلید Gemini API تنظیم نشده است. لطفاً در بخش تنظیمات (Settings) کلید خود را وارد کنید."
        )

    model_clean = (model or "gemini-2.5-flash").strip().replace("models/", "")
    url = f"{BASE_GEMINI_URL}/models/{model_clean}:generateContent?key={api_key.strip()}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": temperature
        }
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            res = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        except Exception as e:
            raise HTTPException(
                status_code=502, 
                detail=f"خطا در برقراری ارتباط با Google Gemini API: {str(e)}"
            )

    if res.status_code != 200:
        err_msg = res.text
        try:
            err_json = res.json()
            err_msg = err_json.get("error", {}).get("message", res.text)
        except Exception:
            pass
        raise HTTPException(
            status_code=res.status_code,
            detail=f"خطای Gemini API ({res.status_code}): {err_msg}"
        )

    data = res.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=500, detail="Gemini هیچ پاسخی بازنگرداند (پاسخ فیلتر یا مسدود شده است).")

    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts or "text" not in parts[0]:
        raise HTTPException(status_code=500, detail="پاسخ متنی معتبری از Gemini دریافت نشد.")

    raw_text = parts[0]["text"]
    try:
        return clean_json_text(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"خروجی مدل به فرمت معتبر JSON تبدیل نشد: {str(e)}\nمتن خام: {raw_text[:300]}"
        )
