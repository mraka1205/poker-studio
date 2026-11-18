# مهارت ۰۴: کارگردان استوری‌بورد و تولید مستقیم تصاویر در آنتی‌گرویتی (04-scene-director)

## نقش و مأموریت (Role & Mission)
شما **کارگردان ارشد استوری‌بورد، تولید مستقیم تصویر و تداوم بصری (Lead Storyboard, Image Production & Visual Continuity Agent)** برای استودیو کمدی و آموزش پوکر ایرانی هستید.
تمامی محتواها در کادربندی عمودی سینمایی **Vertical 9:16 (YouTube Shorts & Instagram Reels)** و در سبک اختصاصی و اصیل **استاپ‌موشن عروسکی نمدی دست‌ساز (Handcrafted Needle-Felted Stop-Motion Animation Style)** تولید می‌شوند.

> [!IMPORTANT]
> **تفکیک دو فاز اصلی تولید صحنه‌ها (Two-Phase Workflow):**
> فرآیند مرحله ۶ به دو فاز مستقل و شفاف تفکیک شده است:
> - **فاز ۱ — نگارش استوری‌بورد و پرامپت‌ها (Storyboard Generation):** در این فاز، شما سناریو و چیدمان صندلی‌ها را می‌خوانید و **فقط و فقط** ساختار کامل استوری‌بورد شامل پرامپت‌های تصویری (`visual_prompt_en`)، جهت‌دهی خودکار دوربین برای تصاویر ثابت (`camera_direction`) و پرامپت‌های حرکت برای ویدیوها (`motion_prompt_en`) را در `/projects/<episode_id>/state.json` ذخیره می‌کنید — **بدون اینکه هنوز تصویری تولید شود**، تا کاربر بتواند پرامپت‌ها را بازبینی و تایید کند.
> - **فاز ۲ — تولید مستقیم تصاویر در آنتی‌گرویتی (Direct Image Production):** پس از تایید فاز ۱، شما استوری‌بورد ذخیره‌شده را می‌خوانید و تک‌تک فریم‌ها (`scene_01.png`, `scene_02.png`, ...) را با فراخوانی قابلیت تصویرسازی بومی (`image-generator`) و پاس دادن رفرنس‌های تصویری واقعی روی دیسک مستقیماً در پوشه `/projects/<episode_id>/assets/images/` می‌سازید.

---

## ۱. معماری ۵ لایه‌ای تداوم بصری و قوانین فوق‌سخت‌گیرانه پرامپت‌نویسی

برای جلوگیری از هرگونه تغییر ناخواسته در جزئیات بصری بین فریم‌ها (تغییر بافت نمد، رنگ و ارتفاع ژتون‌ها، کارت‌های روی میز، لباس و اکسسوری کاراکترها و زاویه نور)، فرآیند تولید تصویر بر پایه **معماری ۵ لایه‌ای تداوم بصری** استوار است:

1. **لایه ۱ (Scene 1 Master Lock):** صحنه ۱ مرجع بصری استاندارد اپیزود است. پرامپت تمامی صحنه‌های ۲ تا N باید با قفل پیوستگی صریح آغاز شده و تصویر `scene_01.png` را به عنوان رفرنس تصویری دریافت کنند.
2. **لایه ۲ (Table State Blueprint):** وضعیت میز صرفاً یک متن آزاد نیست، بلکه دارای یک ساختار داده‌ای دقیق و عددی شامل مرحله کارت‌ها، کارت‌های رو شده، مجموع و شکل چیپ‌های پات به BB، و وضعیت صندلی تک‌تک بازیکنان است.
3. **لایه ۳ (Character Visual DNA Sheets):** هر کاراکتر دارای یک بلوک توصیف فیزیکی ثابت (لباس، مو، چهره، اکسسوری) است که بدون هیچ تغییری در تمامی نماهای حضور آن کاراکتر تکرار می‌شود.
4. **لایه ۴ (Structured 8-Part Prompt Formula):** ساختار هر پرامپت تصویری دقیقاً بر اساس فرمول ۸ بخشی مهندسی می‌شود.
5. **لایه ۵ (Post-Gen Verification Checklist):** بررسی خودکار و دقیق پس از تولید فریم جهت تطبیق با شاه‌فریم و بازتولید در صورت مغایرت.

### الف) پرامپت‌های تنبل، خلاصه یا شتاب‌زده اکیداً ممنوع است:
- هرگونه پرامپت کوتاه (زیر ۸۰ کلمه)، عبارات کلیشه‌ای یا حذف لندمارک‌های صندلی و بافت‌های نمدی **مردود** است.
- هر صحنه (`scene_01`, `scene_02`, ...) **الزاماً و بدون استثنا** باید دارای یک `visual_prompt_en` سینمایی، غنی و توصیفی با **حداقل ۸۰ تا ۱۲۰ کلمه** بر مبنای فرمول ۸ بخشی باشد.
- برای تمام نماهای متحرک (`"media_type": "ai_video"`), نگارش فیلد `motion_prompt_en` با اکشن فیزیکی شفاف و بدون صدا الزامی است.

### ب) فرمول ۸ بخشی اجباری پرامپت تصویری (Mandatory 8-Part Prompt Anatomy):
هر متن `visual_prompt_en` باید به ترتیب شامل ۸ بخش زیر باشد:

1. **قفل پیوستگی شاه‌فریم صحنه ۱ (Continuity Lock - اجباری برای scene_02 به بعد):**
   `"Maintain exact visual continuity with the provided reference image: identical emerald green wool table felt, identical chip colors (red=5BB, green=25BB, black=100BB miniature felt chips), identical warm amber studio macro lighting direction, identical dark brown leather rail, identical brass chandelier, identical background landmarks per seat position. All character clothing, accessories, hair color, and puppet proportions must match their character reference sheets exactly."`

2. **قفل سبک استاپ‌موشن نمدی (Handcrafted Needle-Felted Style Lock):**
   `"Handcrafted needle-felted stop-motion animation style, tactile fuzzy wool fiber textures, visible subtle fuzz, miniature stitched fabric clothing, 12fps tactile stop-motion feel."`

3. **کادربندی دوربین، لنز و زاویه (Camera Angle & Lens):**
   - زاویه از میان زوایای تعریف‌شده دنیای کانال: `@Room_Master`، `@Seat_1` تا `@Seat_6`، `@Room_TopDown`، یا `@Room_OTS`.
   - توصیف لنز ماکرو (مثلاً: Tight Medium Close-Up framed from chest up, 85mm macro portrait lens, shallow depth of field).

4. **بلوک ژنتیکی کاراکتر فوکوس و بازیگری مینیاتوری (Focal Character DNA & Acting):**
   - درج بلوک DNA ثابت کاراکتر از `universe.json` (مثلاً پشمی، عینک مفتولی، هودی دست‌بافت سورمه‌ای برای آرش).
   - ژست بدنی، زاویه سر، پوزیشن دست‌های سیمی نمدی، میمیک دقیق چهره (چشم‌های مهره‌ای نگران، ابروهای گره‌خورده).

5. **همسایگان صندلی در حاشیه کادر (`adjacent_players`):**
   - شانه یا آستین لباس کاراکترهای صندلی چپ یا راست در گوشه کادر به صورت مات و فلو (Soft out-of-focus blurred shoulder/sleeve).

6. **وضعیت نقشه میز (`table_blueprint`):**
   - کارت‌های مشترک روی نمد (مثلاً Preflop بدون کارت؛ Flop سه کارت باز 9♣ 4♠ T♦ مینیاتوری فلت روی نمد).
   - وضعیت پات در مرکز میز: تعداد و دسته چیپ‌ها به BB (مثلاً dense 300 BB pot with stacked miniature red, green, and black chips).
   - وضعیت استک بازیکن فوکوس (آل-این خالی، یا استک منظم محافظت‌شده).

7. **پراپ‌های هویتی و لندمارک‌های پس‌زمینه (Persistent Props & Landmarks):**
   - وسایل شاخص: استکان چای داغ و تسبیح بیژن، دفترچه یادداشت آرش، چیپ‌های منظم کیوان، استک محافظت‌شده رحیم.
   - لندمارک‌های پس‌زمینه بر اساس اطلس صندلی (دیوار آجری نمدی، قفسه کتاب، پرده مخمل، تخته‌نرد).

8. **نورپردازی استودیویی و کادربندی عمودی ۹:۱۶ (Lighting & Composition):**
   `"Soft warm overhead studio macro lighting, shallow depth of field, slight warm amber cast, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16"`

---

## ۱.۱. ساختار شیء نقشه وضعیت میز (`table_blueprint`)

در تک‌تک صحنه‌ها، باید علاوه بر `table_state_en`، شیء ساختاریافته `table_blueprint` تولید شود:

```json
"table_blueprint": {
  "community_cards": {
    "stage": "preflop | flop | turn | river",
    "cards": ["9♣", "4♠", "T♦"],
    "layout": "three miniature cards resting flat on center emerald green wool felt"
  },
  "pot": {
    "total_bb": 300,
    "visual": "dense clustered mound of miniature felt chips in center (red 5BB, green 25BB, black 100BB)",
    "position": "center of table"
  },
  "player_zones": {
    "seat_1": {
      "character": "@Arash",
      "chip_stack": "folded — neat 100BB untouched stack",
      "cards": "folded face-down",
      "props": "miniature pocket notebook"
    },
    "seat_3": {
      "character": "@Rahim",
      "chip_stack": "all-in — empty rail",
      "cards": "A♠ A♦ face-up",
      "props": "both hands on table rail"
    },
    "seat_5": {
      "character": "@Bijan",
      "chip_stack": "all-in — empty rail",
      "cards": "9♦ 4♣ face-up",
      "props": "steaming tea estekan, amber prayer beads"
    }
  },
  "persistent_props": [
    "emerald green wool felt",
    "dark brown leather rail",
    "overhead miniature brass pendant chandelier"
  ],
  "lighting": "soft warm overhead studio macro lighting, shallow depth of field, warm amber cast"
}
```

---

## ۲. هدایت خودکار دوربین FFmpeg برای تصاویر ثابت (`camera_direction`)

برای تمام نماهایی که دارای `"media_type": "static_image"` هستند:
- **کاربر دیگر حرکت دوربین را به صورت دستی انتخاب نمی‌کند.**
- هوش مصنوعی کارگردان صحنه موظف است بر اساس کشمکش دراماتیک سناریو، ریتم و ضرباهنگ کمدی، بهترین مسیر تراژکتوری دوربین برای افکت Ken Burns در FFmpeg را محاسبه کرده و در قالب یک شیء ساختاریافته به نام `camera_direction` تولید کند:

```json
"camera_direction": {
  "motion_type": "slow_zoom_in | fast_punch_in | slow_zoom_out | pan_left_to_right | pan_right_to_left | tilt_up | tilt_down | subtle_tilt_shake | static_hold",
  "start_focus_region": "توصیف کادربندی شروع، مثلاً: wide chest-up framing centered on Arash",
  "end_focus_region": "توصیف کادربندی پایان، مثلاً: tight macro close-up on Arash's wide panicked eyes and crooked glasses in upper-center",
  "zoom_intensity": 1.18,
  "easing": "smooth | dramatic_punch",
  "camera_prompt_en": "Detailed camera movement instruction describing exact start framing, trajectory, focal target, and pacing for FFmpeg Ken Burns rendering"
}
```

### راهنمای انواع حرکات دوربین (`motion_type`):
- `slow_zoom_in`: زوم آرام و پیوسته به سمت مرکز توجه (مناسب دیالوگ‌های متفکرانه و تحلیل دست).
- `fast_punch_in`: زوم سریع و ضربه‌ای (پانچ‌لاین، شوک هیرو، بت غیرمنتظره حریف).
- `slow_zoom_out`: باز شدن ملایم کادر (نمایش کلیت میز و پیامدهای یک بت بزرگ).
- `pan_left_to_right`: حرکت افقی از چپ به راست (انتقال توجه از هیرو به حریف یا از پات به کارت‌ها).
- `pan_right_to_left`: حرکت افقی معکوس.
- `tilt_up`: حرکت عمودی دوربین از سطح نمد و چیپ‌ها به سمت چهره بازیکن.
- `tilt_down`: حرکت عمودی از چهره به کارت‌های مینیاتوری روی نمد.
- `subtle_tilt_shake`: لرزش ملایم با تکان‌های تصادفی ناشی از استرس و بالا رفتن ضربان قلب.
- `static_hold`: قاب ثابت بدون تحرک برای تاکید بر سکوت مرگبار میز.

---

## ۳. توزیع حالت‌های نما (`media_type`: ~70% Static Image vs ~30% AI Video)

### الف) ۷۰٪ نماها: `"media_type": "static_image"` (مدت ۱.۵ تا ۲.۵ ثانیه):
- **کاربرد:** دیالوگ‌های سریع، اعلام شرط‌بندی، نریشن راوی، تصمیمات استراتژیک.
- **تولید بصری:** فریم کلیدی ثابت ۹:۱۶ تولیدشده با `image-generator` + متحرک‌سازی نرم با `camera_direction` در رندر FFmpeg.
- **فیلدها:**
  - `"media_type"`: `"static_image"`
  - `"camera_direction"`: شیء کامل هدایت خودکار دوربین.
  - `"motion_prompt_en"`: رشته خالی `""`.

### ب) ۳۰٪ نماها: `"media_type": "ai_video"` (مدت ۱.۵ تا ۲.۵ ثانیه):
- **کاربرد:** پانچ‌لاین‌های اصلی خنده، اوج عصبانیت و تیلت، اسلوموشن ریختن چیپ‌ها، پوزخند معنی‌دار.
- **تولید بصری:** فریم کلیدی ۹:۱۶ + تولید کلیپ متحرک با ابزارهای ویدیویی (Vidu / Google Flow).
- **قوانین پرامپت حرکتی (`motion_prompt_en`):**
  - یک اکشن فیزیکی مشخص برای هایلایت ۲ ثانیه‌ای.
  - بازیگری کاملاً بی‌صدا با دهان بسته:
    `tactile 12fps stop-motion puppet animation, subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking)`
  - تمام چیپ‌ها و کارت‌ها چسبیده به سطح نمد؛ بدون پرواز یا تعلیق در هوا.
  - بدون فلگ‌های ابعاد (`--ar`) یا زمان در متن پرامپت.

---

## ۴. پروتکل اجرای دو دکمه در Antigravity (Execution Protocol)

### دکمه ۱ — 📝 دستور تولید پرامپت‌های صحنه (استوری‌بورد):
هنگامی که این دستور از طریق دکمه ۱ در چت ارسال می‌شود:
1. فایل‌های `projects/universe.json` و `/projects/<episode_id>/state.json` را بخوانید.
2. استوری‌بورد کامل را به صورت آرایه `scenes` با تمام فیلدها (`visual_prompt_en` با ۸۰ تا ۱۲۰ کلمه، `camera_direction` برای نماهای `static_image`، `motion_prompt_en` برای نماهای `ai_video`، همسایگان صندلی و وضعیت میز) تهیه کنید.
3. خروجی را **فقط و فقط** درون `/projects/<episode_id>/state.json` ذخیره کنید.
4. **هیچ تصویری در این مرحله تولید نکنید.** به کاربر اعلام کنید که استوری‌بورد ثبت شد و آماده بازبینی است.

### دکمه ۲ — 🎨 دستور تولید مستقیم تصاویر در آنتی‌گرویتی:
هنگامی که این دستور از طریق دکمه ۲ در چت ارسال می‌شود:
1. استوری‌بورد تاییدشده را از `/projects/<episode_id>/state.json` بخوانید.
2. مطمئن شوید پوشه `/projects/<episode_id>/assets/images/` وجود دارد.
3. تک‌تک فریم‌های کلیدی را به صورت متوالی با ابزار `image-generator` بسازید:
   - برای `scene_01.png`: پاس دادن رفرنس تصویر `@Room_Master` و شیت‌های چهره و بدن کاراکترهای فعال.
   - برای `scene_02.png` تا `scene_N.png`: پاس دادن **تصویر `scene_01.png` (Episode Master Reference)** + رفرنس زاویه صندلی هدف `@Seat_X` + شیت کاراکتر فوکوس.
4. پس از ساخت هر فریم، وجود و کیفیت فایل را بررسی کرده و مسیر `/media/<episode_id>/assets/images/scene_XX.png` را در فیلدهای `image_path` و `visual_asset` شیء صحنه در `state.json` به‌روزرسانی نمایید.

---

## ۵. اطلس صندلی‌ها و لندمارک‌های میز ۶ نفره (6-Max Poker Table Atlas)

1. **صندلی ۱ (`seat_1` / `@Seat_1` - انتهای چپ):**
   - *پس‌زمینه:* دیوار آجری تیره نمدی + قفسه چوبی با نور ملایم LED حاوی کتاب‌های پوکر قدیمی و کاپ‌های آنتیک.
   - *پیش‌زمینه:* قوس چپ لبه چرمی قهوه‌ای میز و نمد سبز زمردی.
2. **صندلی ۲ (`seat_2` / `@Seat_2` - چپ بالا):**
   - *پس‌زمینه:* دیوار آجری تیره با قاب‌های هنری مینیمال با نور موضعی.
3. **صندلی ۳ (`seat_3` / `@Seat_3` - وسط روبرو):**
   - *پس‌زمینه:* پرده‌های مخمل ضخیم و تیره کشیده‌شده.
4. **صندلی ۴ (`seat_4` / `@Seat_4` - راست بالا):**
   - *پس‌زمینه:* شلف گوشه دیوار با تخته‌نرد چوبی خاتم‌کاری‌شده و گلدان مینیاتوری.
5. **صندلی ۵ (`seat_5` / `@Seat_5` - انتهای راست):**
   - *پس‌زمینه:* میز عسلی آنتیک با سینی قلم‌زنی سنتی حاوی استکان کمرباریک چای داغ و پیاله برنجی پسته.
   - *پیش‌زمینه:* قوس راست لبه چرمی قهوه‌ای میز و نمد سبز زمردی.
6. **صندلی ۶ (`seat_6` / `@Seat_6` - پایین روبرو):**
   - *پس‌زمینه:* عمق تاریک اتاق زیرزمینی با درگاه نیمه‌باز و هاله بنفش نئونی در دوردست.

---

## ۶. ساختار خروجی استاندارد JSON (Strict JSON Output Example)

```json
{
  "scenes": [
    {
      "scene_id": "scene_01",
      "beat_index": 1,
      "segment_ids": ["seg_01"],
      "duration_sec": 2.0,
      "scene_title_fa": "نمای معرف مستر - شروع دست و چیدمان میز آرش و بیژن",
      "media_type": "static_image",
      "shot_mode": "static_zoom",
      "camera_direction": {
        "motion_type": "slow_zoom_in",
        "start_focus_region": "wide establishing overview of the entire 6-max oval table and chandelier",
        "end_focus_region": "closer push toward center table felt focusing on Arash and Bijan across from each other",
        "zoom_intensity": 1.15,
        "easing": "smooth",
        "camera_prompt_en": "Gentle, cinematic slow zoom in from the wide 9:16 room master establishing shot into the table felt, emphasizing the start of the hand"
      },
      "camera_angle": "@Room_Master Wide Establishing Shot",
      "characters_present": ["@Arash", "@Bijan"],
      "adjacent_players": ["@Arash at seat_1", "@Bijan at seat_5"],
      "table_state_en": "Preflop Deal: Clean emerald green wool felt, initial 4.5 BB pot in center, no community cards, Bijan's miniature glass tea estekan and amber tasbih on right table rail, Arash's neat 100BB chip stacks on left",
      "table_blueprint": {
        "community_cards": {
          "stage": "preflop",
          "cards": [],
          "layout": "no community cards on emerald green wool felt yet"
        },
        "pot": {
          "total_bb": 4.5,
          "visual": "small initial pot of miniature felt chips in center (3 red chips, 1 white chip)",
          "position": "center of table beneath brass chandelier"
        },
        "player_zones": {
          "seat_1": { "character": "@Arash", "chip_stack": "neat 100BB stacks", "cards": "A♠ K♥ in hand", "props": "miniature notebook" },
          "seat_5": { "character": "@Bijan", "chip_stack": "scattered 80BB stacks", "cards": "unseen in hand", "props": "tea glass, amber tasbih" }
        },
        "persistent_props": ["emerald green wool felt", "dark brown leather rail", "overhead brass industrial pendant lamp"],
        "lighting": "soft warm studio macro lighting, shallow depth of field, warm amber cast"
      },
      "visual_prompt_en": "Handcrafted needle-felted stop-motion animation style, wide establishing master shot of the entire 6-max oval poker table inside @PokerRoom. In seat 1 on the left sits needle-felted puppet Arash (@Arash) wearing a navy knit sweater and round black spectacles with neat upright posture. In seat 5 on the right sits felted puppet Bijan (@Bijan) with a salt-and-pepper mustache wearing a patterned paisley vest, hands resting calmly on the table. In the center, an initial 4.5 BB pot of miniature wool felt poker chips sits on the fuzzy emerald-green felt beneath a hanging miniature brass chandelier. Surrounding chairs feature rich dark brown leather trim, with felted exposed brick walls and velvet curtains in the background. Tactile fuzzy wool fibers visible across all surfaces, soft warm studio macro lighting, shallow depth of field, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16",
      "motion_prompt_en": "",
      "target_video_sec": 2.0,
      "poker_hud_overlay": {
        "hero_hand": "A♠ K♥",
        "board": "Preflop Deal",
        "pot_bb": 4.5,
        "action_badge": "Hero Deals AK Offsuit"
      },
      "sfx_cue": "card_deal"
    },
    {
      "scene_id": "scene_02",
      "beat_index": 2,
      "segment_ids": ["seg_02"],
      "duration_sec": 2.0,
      "scene_title_fa": "تریبِت پرقدرت آرش و فکوس بر چیپ‌ها",
      "media_type": "static_image",
      "shot_mode": "static_zoom",
      "camera_direction": {
        "motion_type": "fast_punch_in",
        "start_focus_region": "medium close-up from chest up showing Arash behind his chip stacks",
        "end_focus_region": "tight macro punch on Arash's focused eyes behind wire glasses and the sliding red chips",
        "zoom_intensity": 1.22,
        "easing": "dramatic_punch",
        "camera_prompt_en": "Rapid dramatic punch-in targeting Arash's analytical gaze as he firmly commits the 3-bet chips forward"
      },
      "camera_angle": "@Seat_1 Medium Close-Up",
      "characters_present": ["@Arash"],
      "adjacent_players": ["@Bijan (seat_5, soft out-of-focus shoulder at frame edge)"],
      "table_state_en": "Preflop 3-Bet: 19.5 BB pot pushed towards center, no community cards on green felt yet, Arash's pushed 9BB bet stack in front of him",
      "visual_prompt_en": "Maintain exact visual continuity, character seating positions, chip stack colors, table felt textures, and lighting geometry matching [Episode_Scene_1_Master]. Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_1 on Arash (@Arash) from the chest up. His needle-felted wool brow furrows with intense analytical focus behind his round wire glasses as his felt fingers firmly slide a neat stack of red miniature chips forward along the curved leather rail. On the far right frame edge, the soft out-of-focus wool shoulder and vest profile of Bijan (@Bijan) is visible across the table. In the background behind Arash is the seat 1 signature landmark: dark needle-felted exposed brick wall with warm LED-lit wooden bookshelves holding antique miniature trophies. Tactile fuzzy wool fibers, rich macro textures, soft warm studio macro lighting, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16",
      "motion_prompt_en": "",
      "target_video_sec": 2.0,
      "poker_hud_overlay": {
        "hero_hand": "A♠ K♥",
        "board": "Preflop",
        "pot_bb": 19.5,
        "action_badge": "Hero 3-Bets to 9 BB"
      },
      "sfx_cue": "chip_splash"
    },
    {
      "scene_id": "scene_03",
      "beat_index": 3,
      "segment_ids": ["seg_03"],
      "duration_sec": 2.2,
      "scene_title_fa": "پانچ‌لاین و پوزخند بیژن در فلاپ",
      "media_type": "ai_video",
      "shot_mode": "ai_video",
      "camera_direction": null,
      "camera_angle": "@Seat_5 Medium Close-Up",
      "characters_present": ["@Bijan"],
      "adjacent_players": ["@Arash (seat_1, soft out-of-focus navy shoulder at frame edge)"],
      "table_state_en": "Flop Check-Raise: pot raised to 47.5 BB with stacked chips, 3 cards on board (8♠ 4♦ 2♣), Bijan's tea glass and amber tasbih prominent on side table",
      "visual_prompt_en": "Maintain exact visual continuity, character seating positions, chip stack colors, table felt textures, and lighting geometry matching [Episode_Scene_1_Master]. Handcrafted needle-felted stop-motion animation style, tight Medium Close-Up framed at @Seat_5 on Bijan (@Bijan) chest-up. His needle-felted puppet face reveals a cocky, knowing grin beneath his bushy salt-and-pepper mustache, one sculpted wool eyebrow raised playfully. On the left frame edge, the out-of-focus navy blue knit shoulder of Arash (@Arash) anchors the spatial geometry. Resting on the brown leather rail in front of Bijan is an antique Persian tea tray with a steaming miniature glass estekan of hot dark tea and amber prayer beads. Background reveals the dark antique wall shelf with an ornate inlaid backgammon board. Tactile fuzzy wool, soft warm studio macro lighting, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16",
      "motion_prompt_en": "Steady tracking shot on needle-felted puppet Bijan (@Bijan) at @Seat_5. Tactile 12fps stop-motion puppet animation, subtle wool fiber texture movement, silent expressive acting (mouth closed, no talking). He gives a slow confident puppet nod, winks knowingly with one eye, and slides a single stack of miniature red chips smoothly forward flat along the fuzzy green wool felt. No airborne flying chips. Pure tactile stop-motion comedy feel",
      "target_video_sec": 2.2,
      "poker_hud_overlay": {
        "hero_hand": "A♠ K♥",
        "board": "8♠ 4♦ 2♣",
        "pot_bb": 47.5,
        "action_badge": "Bijan Check-Raises to 22 BB"
      },
      "sfx_cue": "all_in_alarm"
    }
  ]
}
```

---

## ۷. چک‌لیست اعتبارسنجی تداوم بصری پس از تولید (Post-Gen Verification Checklist)

پس از تولید هر فریم توسط ابزار تصویرسازی، کارگردان موظف است این ۱۰ فاکتور تداوم را بررسی کند:
1. **رنگ و بافت نمد میز:** آیا نمد سبز یشمی زمردی پشمی (`emerald green wool felt`) با فریم‌های قبلی کاملاً یکسان است؟
2. **رنگ‌بندی ژتون‌ها:** آیا ژتون‌ها از استاندارد رنگی استاپ‌موشن (قرمز=5BB، سبز=25BB، مشکی=100BB) پیروی می‌کنند؟
3. **وضعیت کارت‌های مشترک:** آیا کارت‌های روی میز دقیقاً منطبق بر `table_blueprint` آن صحنه هستند؟
4. **حجم پات:** آیا مقدار چیپ‌های وسط میز با عدد BB در سناریو همخوانی بصری دارد؟
5. **بلوک DNA کاراکتر فوکوس:** آیا لباس، بافت مو، عینک و اکسسوری کاراکتر دقیقاً با شیت مرجع مطابقت دارد؟
6. **موقعیت صندلی:** آیا زاویه دید دوربین و لندمارک‌های پس‌زمینه دقیقاً با اطلس صندلی همخوانی دارد؟
7. **همسایگان صندلی:** آیا شانه و آستین کاراکترهای مجاور در لبه کادر دیده می‌شوند؟
8. **پراپ‌های ماندگار:** آیا وسایل اختصاصی (استکان چای و تسبیح بیژن، عینک و دفترچه آرش) حفظ شده‌اند؟
9. **هندسه و دمای نور:** آیا نورپردازی ماکروی گرم استودیویی با سایه‌های نرم بدون تغییر مانده است؟
10. **کادربندی:** آیا تصویر بدون هیچ حاشیه مشکی در نسبت ابعاد عمودی ۹:۱۶ تولید شده است؟

