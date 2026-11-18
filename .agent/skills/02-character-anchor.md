# مهارت ۰۲: هدایت لنگر استایل و یکدستی کاراکترها (Character Anchor & Visual Consistency)

## هدف و مأموریت
حفظ یکدستی کامل بصری (Visual Consistency) در تمامی تصاویر تولیدی با مدل‌های هوش مصنوعی (مانند Midjourney, Flux, Stable Diffusion, DALL-E). در پروژه‌های انیمیشن سریالی، بزرگ‌ترین چالش تغییر چهره، سن، رنگ پوست یا فرم لباس کاراکترها در نماهای مختلف است. این مهارت تضمین می‌کند که کاراکترها همیشه هویت ثابت و امضای بصری یکپارچه داشته باشند.

---

## ۱. مفهوم استایل لنگر (The Style Anchor)
کاراکتر «لنگر» کاراکتری است که استایل گرافیکی کلی پروژه روی او تعریف و قفل می‌شود. در استودیو پوکر ما، **«کامبیز جی‌تی‌او» (Kambiz GTO)** کاراکتر لنگر است.

### ساختار پرامپت ریشه (Root Style Anchor):
تمامی پرامپت‌های تولید تصویر برای کاراکترها و صحنه‌ها **باید** بلوک استایل زیر را در ابتدای پرامپت خود داشته باشند:

```text
[STYLE_ANCHOR]: Modern dynamic 2D cartoon animation style, bold stylized ink outlines, rich vibrant saturated color palette, expressive exaggeration, Rick and Morty meets Archer adult animation comic aesthetic, clean cinematic cell shading, poker room ambient neon lighting.
```

---

## ۲. مشخصات کاراکترهای اصلی پروژه (Character Profiles)

### کاراکتر ۱ (لنگر استایل): کامبیز جی‌تی‌او (Kambiz GTO)
- **نقش:** تحلیل‌گر عصبی، وسواسی، عاشق احتمالات ریاضی، نِرد کلاسیک.
- **امضای بصری:**
  - عینک فریم‌گرد مشکی بزرگ که گاهی نور کارت‌ها رویش رفلکس می‌زند.
  - موهای نامرتب و پریشان قهوه‌ای تیره، ته‌ریش کوتاه.
  - هودی سرمه‌ای تیره با طرح ریاضی کوچک یا چارت رِینج، ساعت دیجیتال کاسیو در دست.
  - میمیک‌های کلیدی: چشم‌های از حدقه بیرون زده از شوک، نگاه مغرورانه با لبخند تحقیرآمیز، یا عرق سرد ریختن از سردرگمی.
- **پرامپت قفل شده کاراکتر (Character Token):**
  ```text
  kambiz_gto_persian_poker_nerd: a 28-year-old Iranian guy with messy dark hair, thick round black glasses, short stubble, wearing a navy blue hoodie, intense analytical facial expression, sweat drops, holding a glowing tablet with poker range charts.
  ```

### کاراکتر ۲: اصغر فیش (Asghar Calling Station)
- **نقش:** بازیکن لوکال، صمیمی، خرافاتی، عاشق کال کردن بدون فکر، سلطان گات‌شات.
- **امضای بصری:**
  - پیراهن نخی راه‌راه یا گلدار دکمه‌باز، زنجیر باریک طلا یا نقره دور گردن.
  - سبیل پهن پرپشت ایرانی، موهای جوگندمی کم‌پشت.
  - تسبیح شاه‌مقصود در دست، فنجان چای کمرباریک روی میز جلویش.
  - میمیک کلیدی: نیشخند گشاد و خونسرد در اوج بلف حریف، چشمک زدن دوستانه، کشیدن چیپ‌ها با بیخیالی.
- **پرامپت قفل شده کاراکتر (Character Token):**
  ```text
  asghar_fish_persian_calling_station: a 52-year-old cheerful Iranian man with thick salt-and-pepper mustache, open-collar striped vintage shirt, relaxed confident smile, holding amber prayer beads (tasbih) in one hand and green poker chips in the other, completely careless attitude.
  ```

### کاراکتر ۳: بهروز نیت (Behrouz The Granite Nit)
- **نقش:** بازیکن خشن، فوق‌العاده بسته، محتاط، کوه سنگ و استرس.
- **امضای بصری:**
  - کلاه لبه‌دار (Cap) پایین کشیده، عینک آفتابی تیره حتی زیر نور کم سالن.
  - کاپشن بادگیر ورزشی تیره با زیپ بالا کشیده تا زیر چانه.
  - دست‌های قفل شده روی دو کارتش، مثل مجسمه بدون تکان خوردن.
  - میمیک کلیدی: اخم غلیظ، نگاه مشکوک از بالای عینک آفتابی، فولد دادن با حس انزجار.
- **پرامپت قفل شده کاراکتر (Character Token):**
  ```text
  behrouz_nit_stone_player: a 40-year-old stern Iranian poker player, dark baseball cap pulled low, black sunglasses covering his eyes, high-collared dark windbreaker zipped up to chin, folded arms, grumpy suspicious frown, motionless rock demeanor.
  ```

---

## ۳. دستورالعمل خروجی فوتوشیت (Character Sheet Template)
برای هر کاراکتر پیش از ورود به تولید نماها، یک **Character Turnaround Sheet** تولید و تصویب می‌شود:
1. نمای روبه‌رو (Front View)
2. نمای سه رخ (3/4 Profile View)
3. ۳ واکنش میمیک چهره (Tilt Shock / Confident Smile / Poker Face Neutral)

## ۴. روش‌های فنی حفظ یکدستی (Consistency Rules):
- در Midjourney از دستور `--cref [URL_OF_APPROVED_SHEET] --cw 80` استفاده شود.
- در Flux / SD از LoRA اختصاصی یا کنترل‌نت Reference / IP-Adapter بهره گرفته شود.
- تمام پرامپت‌ها باید متغیرهای نسبت تصویر (`--ar 9:16` برای ریلز یا `--ar 16:9` برای یوتیوب اصلی) را رعایت کنند.
