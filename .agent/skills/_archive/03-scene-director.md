# مهارت ۰۳: کارگردانی نماها و استوری‌بورد بصری (Scene Director & Beat Breakdown)

## هدف و مأموریت
تبدیل سناریوهای تایید شده به **بیت‌های بصری ۳ تا ۶ ثانیه‌ای (Visual Beats)**، آماده برای تولید تصاویر و انیمیشن در هوش مصنوعی (مانند Midjourney, Flux, Runway Gen-3, Luma Dream Machine, Kling AI) به همراه اطلاعات وضعیت میز پوکر (Table State) و نشانه‌گذاری‌های صوتی و افکت‌ها (SFX Cues).

---

## ۱. قوانین ریتم و ضرب‌آهنگ (The 3-6 Second Beat Rule)
برای نگه‌داشتن توجه مخاطب در پلتفرم‌های ریلز و شورتس، هیچ نمایی نباید بیش از ۶ ثانیه ثابت بماند:
- **نمای معرفی/قلاب (0-4s):** کلوزآپ پرانرژی، واکنش هیجانی، زاویه دوربین کج (Dutch Angle) یا چشم‌انداز میز با گرافیک پاپ‌آپ.
- **نمای کارت‌ها و اکشن (3-5s):** نمای از بالا (Top-down) یا از پشت شانه هیرو (Over-The-Shoulder) که کارت‌های در دست و کارت‌های بورد را شفاف نشان می‌دهد.
- **نمای کمدی/دیالوگ (3-4s):** نمای دونفره یا کلوزآپ کاراکتر در حال صحبت با ژست‌های اغراق‌شده کارتونی.
- **نمای نتیجه‌گیری (4-6s):** جمع شدن پات، تابلوی قانون طلایی گرافیکی روی صفحه، و انیمیشن پایانی.

---

## ۲. وضعیت میز پوکر (Poker Table State HUD)
هر نمایی که میز بازی را شامل می‌شود باید داده‌های ریاضی و وضعیت دست را در فیلد `poker_table_state` مشخص کند:
- **Board Cards:** کارت‌های روی زمین به تفکیک خال و رنک (مثلاً `[ A♠, 8♦, 3♣ ]`)
- **Pot Size:** سایز پات بر حسب بیگ بلایند (مثلاً `28.5 BB`)
- **Player Stacks:** استک هر بازیکن در گیر در دست (`Hero: 85 BB`, `Villain: 110 BB`)
- **Action Badge:** برچسب اکشن جاری (`Hero C-Bets 33%`, `Villain Check-Raises 3.5x`)
- **Equity HUD:** درصد شانس برد هیرو روی صفحه (`Hero Equity: 62%`)

---

## ۳. کاتالوگ افکت‌های صوتی استاندارد (Standard SFX Catalog)
افکت‌های صوتی ریتم کمدی را می‌سازند و در فیلد `sfx_cue` قرار می‌گیرند:
- `sfx_chip_riffle`: صدای کلیک و شافل کردن چیپ‌های سفالی سنگین.
- `sfx_card_snap`: صدای پرتاب یا ورق خوردن شلاقی کارت روی ماهوت میز.
- `sfx_dramatic_heartbeat`: تپش قلب سنگین و بم در لحظه تصمیم‌گیری بزرگ یا بلف حریف.
- `sfx_tilt_alarm`: آژیر خطر یا بوق خنده‌دار فاجعه مغزی کاراکتر هنگام تیلت.
- `sfx_record_scratch`: ایست ناگهانی موسیقی برای شوخی یا خطای مضحک.
- `sfx_glass_shatter`: خرد شدن شیشه نمادین وقتی نقشه هیرو نابود می‌شود.
- `sfx_cash_register_ding`: صدای چرخ چاه پول یا دینگ صندوق هنگام کال کردن فیش.
- `sfx_casino_ambient`: صدای محو مکالمات پس‌زمینه و خنده‌ها در سالن پوکر.

---

## ۴. ساختار پرامپت‌نویسی صحنه‌ها (Prompt Engineering Blueprint)
هر پرامپت بصری (`visual_prompt`) ترکیبی از این ۴ لایه است:

```text
[STYLE_ANCHOR] + [CHARACTER_TOKEN] + [SCENE_ACTION & CAMERA] + [LIGHTING & COMPOSITION]
```

### نمونه پرامپت استاندارد برای Midjourney / Flux:
```text
Modern 2D cartoon animation style, Rick and Morty comic aesthetic. Kambiz the Persian poker nerd wearing navy hoodie and thick round glasses staring in horror at a dry poker board (King of clubs, 7 of diamonds, 2 of spades), sweat dripping down his temples, dramatic dramatic red rim light, extreme close-up low angle shot, vibrant neon casino ambiance --ar 9:16 --v 6.1
```

### نمونه پرامپت انیمیشن برای Runway Gen-3 / Kling:
```text
Slow zoom in on Kambiz's sweating face, shaking his head in disbelief, animated 2D comic style, blinking eyes with glowing reflection of poker cards in his glasses lenses, subtle hand tremor holding chips.
```

---

## ۵. قالب خروجی سناریوی تفکیک‌شده در `state.json`

```json
{
  "scenes": [
    {
      "id": "scene_01",
      "beat_index": 1,
      "time_range": "00:00 - 00:04",
      "title": "قلاب اول - شوک هیرو پای میز",
      "speaker": "Narration",
      "subtitle_fa": "عاشق ای‌کی هستی تا وقتی که سه تا کارت سفید بدون آس و شاه مثل آوار می‌ریزه رو سرت!",
      "tts_fa": "عاشِقِ اِی‌کِی هَستی تا وَقْتی که سِه تا کارْتِ سِفید بِدونِ آس و شاه مِثْلِ آوار می‌ریزِه رو سَرِت!",
      "camera": "Extreme Close-Up Dutch Angle",
      "character_id": "char_kambiz",
      "visual_prompt": "Modern 2D cartoon animation style. Close-up on Kambiz with round glasses and messy hair sweating with terrified facial expression looking down at the poker table, dramatic rim lighting, vibrant neon casino background --ar 9:16",
      "poker_table_state": {
        "board": ["8♠", "4♦", "2♣"],
        "pot_bb": 14,
        "hero_hand": "A♠ K♥",
        "action_badge": "Flop Missed completely"
      },
      "sfx_cue": "sfx_dramatic_heartbeat",
      "visual_asset": "/projects/ep01-sample/scenes/scene_01.png",
      "status": "ready_for_review"
    }
  ]
}
```
