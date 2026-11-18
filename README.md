# استودیو کمدی و آموزش پوکر (Poker Animation Studio)
### معماری هیبرید: Google AI Studio + OpenRouter API + نظارت انسان (HITL)

استودیوی محلی و تحت وب برای تولید ویدیوهای کوتاه طنز و آموزشی پوکر ایرانی با تفکیک هوشمند مراحل خلاقانه و مراحل خودکارسازی شده.

---

## ۱. معماری هیبرید هوش مصنوعی (Hybrid AI Architecture)

1. **مراحل خلاقانه (Creative Stages - دستی در Google AI Studio / Gemini):**
   - مراحل: **ایده و بابل (Bible)**، **سناریوی دو متنی با اعراب TTS**، و **لنگر استایل کاراکترها (Character Turnarounds)**.
   - عملکرد: کاربر با یک کلیک روی **«کپی پرامپت کامل برای AI Studio»**، پرامپت اختصاصی ترکیب‌شده با داده‌های پروژه و فایل مهارت را کپی کرده، در مدل‌های پرچمدار و رایگان Gemini در AI Studio اجرا می‌کند، سپس JSON خروجی را در کادر **«ثبت و تایید JSON خروجی»** قرار می‌دهد تا مستقیماً اعتبارسنجی و در `state.json` ذخیره شود.

2. **مراحل ساختاریافته و خودکار (Automated Stages - با OpenRouter API):**
   - مراحل: **تولید استوری‌بورد صحنه‌ها (Scene Breakdown)** و **بازسازی اعراب و تلفظ فونتیک خطوط سناریو (Regenerate TTS Diacritics)**.
   - عملکرد: مستقیماً از بک‌اند با فراخوانی OpenRouter (مدل پیش‌فرض: `google/gemini-2.5-flash` با خروجی تضمین‌شده `json_object`).

3. **سامانه فایل‌محور محلی (Local File System):**
   - ذخیره تمامی متادیتا در `/projects/<episode_id>/state.json` و فایل‌های مالتی‌مدیا در زیرپوشه‌های `/audio`, `/characters`, `/scenes`, `/exports`.

---

## ۲. مهارت‌های تخصصی پوکر (`/.agent/skills/`)

- **`01-bible-and-jokes.md`:** تدوین کتابچه استراتژی، تضاد GTO در برابر Exploit، جزئیات دست و ۴ تا ۶ شوخی بومی‌سازی شده فرهنگ پوکر ایرانی.
- **`02-persian-script-writer.md`:** نگارش سناریوی ۴ پرده‌ای با قانون اجباری خروجی دو متنی: `subtitle_fa` (متن تمیز عامیانه) و `tts_fa` (اعراب‌گذاری کامل و هجی فونتیک اصطلاحات فِلاپ، تِریبِت، چِک‌رِیز، آل‌آین).
- **`03-character-anchor.md`:** لنگر استایل ۲ بعدی کاراکتر هیرو (کامبیز جی‌تی‌او) و پرامپت‌های مدل‌شیت چندزاویه‌ای کاراکترها با ارجاع به Style Anchor.
- **`04-scene-director.md`:** تقطیع سناریو به نماهای ۳ تا ۶ ثانیه‌ای، پرامپت انگلیسی تصویر/ویدیو، وضعیت هاد میز پوکر (`poker_hud_overlay`) و برچسب‌های افکت صوتی (`sfx_cue`).

---

## ۳. اندپوینت‌های اضافه شده به بک‌اند FastAPI

- `POST /api/projects/{id}/build-prompt/{stage}`: تولید مگافرانت آماده برای AI Studio بر اساس مهارت‌های چهارگانه.
- `POST /api/projects/{id}/import-json/{stage}`: پاک‌سازی مارک‌داون، اعتبارسنجی JSON و ذخیره مستقیم در بخش مربوطه `state.json`.
- `POST /api/projects/{id}/run-openrouter/{task}`:
  - `generate_scenes`: تولید خودکار صحنه‌ها، هاد میز و SFX با OpenRouter.
  - `regenerate_tts_fa`: تولید مجدد اعراب فونتیک خطوط فارسی پس از ویرایش دستی.
- `GET /api/settings` و `POST /api/settings`: مدیریت کلید OpenRouter و مدل در فایل `.env`.
- `POST /api/projects/{id}/upload/{asset_type}`: آپلود فایل‌های کاراکتر، صحنه و صدا.

---

## ۴. دسترسی به استودیو

- **فرانت‌اند تعاملی (Vite):** [http://localhost:5173](http://localhost:5173)
- **بک‌اند و نسخه تولیدی (FastAPI):** [http://localhost:8000](http://localhost:8000)
- **سندهای تعاملی Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
