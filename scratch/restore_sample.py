import json

state_file = "g:/poker-studio/projects/ep01-sample/state.json"
with open(state_file, "r", encoding="utf-8") as f:
    state = json.load(f)

full_segments = [
  {
    "id": "seg_01",
    "act": "Hook (قلاب اول)",
    "speaker": "Narration",
    "emotion": "energetic_sarcastic",
    "subtitle_fa": "فکر کردی با دست آس و شاه (AK) شدی پادشاه کل کازینو؟ صبر کن تا فلاپ برسه!",
    "tts_fa": "فِکْر کَردی با دَسْتِ آس و شاه، اِی‌کِی، شُدی پادِشاهِ کُلِّ کاّزینو؟ صَبْر کُن تا فِلاپ بِرِسِه!",
    "estimated_duration_sec": 5.0,
    "poker_context": "Hero deals AK offsuit preflop in Button position"
  },
  {
    "id": "seg_02",
    "act": "The Hand Setup (چیدمان دست)",
    "speaker": "Narration",
    "emotion": "analytical",
    "subtitle_fa": "صد بیگی عمیقی، تو باتن با آس و شاه آفرین ۳-بِت زدی، اصغر فیش هم از بیگ بلایند با لبخند ژکوند کال می‌کنه.",
    "tts_fa": "صَد بیگی عَمیقی، تو باتِن با آس و شاه آفِرین تِریبِت زَدی، اَصْغَر فیش هَم از بیگ بْلایْند با لَبْخَندِ ژوکوند کال می‌کُنِه.",
    "estimated_duration_sec": 7.5,
    "poker_context": "Hero on BTN 3-bets to 9 BB. Villain BB calls. Pot = 19.5 BB."
  },
  {
    "id": "seg_03",
    "act": "The Hand Setup (فلاپ فاجعه)",
    "speaker": "Kambiz",
    "emotion": "shocked_tilt",
    "subtitle_fa": "فلاپ میاد: ۸ پیک، ۴ خشت، ۲ گشنیز! هیچ لعنتی به هیچی وصل نیست، ولی سولور من می‌گه سی‌بِت بزن!",
    "tts_fa": "فِلاپ میاد: هَشْتِ پیک، چَهارِ خِشْت، دویِ گِشْنیز! هیچ لَعْنَتی به هیچی وَصْل نیست، وَلی سولوِرِ مَن می‌گِه سی‌بِت بِزَن!",
    "estimated_duration_sec": 6.8,
    "poker_context": "Board: 8s 4d 2c (Rainbow Dry Board). Hero has As Kh."
  },
  {
    "id": "seg_04",
    "act": "The Comedy Breakdown (ضربه چک‌ریز)",
    "speaker": "Asghar",
    "emotion": "teasing_confident",
    "subtitle_fa": "کامبیز سی‌بت می‌زنه، اصغر تسبیح رو می‌ذاره زمین، یهو میگه: چِک‌رِیز، ۴۰ تا بیگی بیار وسط داداش!",
    "tts_fa": "کامبیز سی‌بِت می‌زَنِه، اَصْغَر تَسْبیح رو می‌ذارِه زَمین، یهو میگِه: چِک‌رِیز، چِهِل تا بیگی بیار وَسَط داداش!",
    "estimated_duration_sec": 7.0,
    "poker_context": "Hero C-Bets 6 BB. Asghar Check-Raises to 22 BB."
  },
  {
    "id": "seg_05",
    "act": "The Comedy Breakdown (توهم هیرو)",
    "speaker": "Kambiz",
    "emotion": "panicked_denial",
    "subtitle_fa": "مغز هیرو داد می‌زنه: نکنه داره بلفم می‌زنه؟ من آس دارم! من بلاکر دارم! آل‌آین می‌زنم بفهمه رئیس کیه!",
    "tts_fa": "مَغْزِ هیرو داد می‌زَنِه: نَکُنِه دارِه بْلَفَم می‌زَنِه؟ مَن آس دارَم! مَن بْلاکِر دارَم! آل‌آین می‌زَنَم بِفَهمِه رَئیس کیِه!",
    "estimated_duration_sec": 7.5,
    "poker_context": "Hero tilts, shoves All-in with Ace-high no pair."
  },
  {
    "id": "seg_06",
    "act": "The Golden Takeaway (آموزش طلایی)",
    "speaker": "Narration",
    "emotion": "authoritative_humorous",
    "subtitle_fa": "اصغر با دست ۸ و ۷ سویتد یه پیر داره و کال می‌کنه! کل استک پر! یادت نره: دست AK فقط یک آس‌های (Ace-High) سادست!",
    "tts_fa": "اَصْغَر با دَسْتِ هَشْت و هَفْتِ سوتِد یِه پیر دارِه و کال می‌کُنِه! کُلِّ اِستَک پَر! یادِت نَرِه: دَسْتِ اِی‌کِی فَقَط یک آس‌هایِ سادَسْت!",
    "estimated_duration_sec": 8.0,
    "poker_context": "Asghar shows 8s 7s, Pair of Eights. Hero busted."
  },
  {
    "id": "seg_07",
    "act": "The Golden Takeaway (جمع‌بندی نهایی)",
    "speaker": "Narration",
    "emotion": "witty_cta",
    "subtitle_fa": "قانون طلایی: روی بورد خشک، با دست پیرنشده سایز بت رو کنترل کن و جلوی چک‌ریز فیش‌های محله، راحت فولد بده. چنل رو سابسکرایب کن تا استکت دود نشه!",
    "tts_fa": "قانونِ طَلایی: رویِ بوردِ خُشْک، با دَسْتِ پیر نَشُدِه سایزِ بِت رو کُنْتُرُل کُن و جِلویِ چِک‌رِیزِ فیش‌هایِ مَحَلِّه، راحَت فولد بِدِه. چَنِل رو سابْسْکرایْب کُن تا اِسْتَکِت دود نَشِه!",
    "estimated_duration_sec": 9.0,
    "poker_context": "Golden rule graphic overlay and CTA animation"
  }
]

state["script"]["segments"] = full_segments
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print("Restored full 7 segments!")
