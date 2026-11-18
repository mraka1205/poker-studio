import React, { useState, useEffect } from 'react';
import { Lightbulb, BookTemplate, Check, CheckCircle2, Sparkles, Palette, Save } from 'lucide-react';
import AiStudioBridge from './AiStudioBridge';
import { saveEpisodeIdea } from '../api';

export default function IdeaBibleView({
  ideaData = {},
  bibleData = {},
  episodeId,
  stageNumber = 1,
  stageStatus,
  onApproveStage,
  onRefresh
}) {
  const isIdea = stageNumber === 1;

  // Local state for editable raw idea text
  const [rawIdeaText, setRawIdeaText] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const initialText = ideaData?.raw_hand_or_concept || ideaData?.theme || '';
    setRawIdeaText(initialText);
  }, [ideaData?.raw_hand_or_concept, ideaData?.theme, episodeId]);

  const handleSaveIdea = async () => {
    setIsSaving(true);
    try {
      await saveEpisodeIdea(episodeId, {
        raw_hand_or_concept: rawIdeaText.trim(),
        theme: rawIdeaText.trim()
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در ذخیره ایده: ' + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* AI Studio Bridge for Idea & Bible */}
      <AiStudioBridge
        episodeId={episodeId}
        stage="bible"
        stageTitle="کتابچه استراتژی و جوک‌ها (Bible)"
        description="پرامپت مهارت ۰۱ را برای Gemini کپی کنید تا مفهوم GTO vs Exploit، جزئیات دست و ۴ تا ۶ جوک اصیل پوکر ایرانی بر اساس ایده خام ثبت‌شده در قالب JSON تولید شود."
        onSuccess={() => {
          if (onRefresh) onRefresh();
        }}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله {stageNumber}: {isIdea ? 'ایده و کانسپت اولیه' : 'کتابچه سبک و اصول طراحی (Bible)'}
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            {isIdea ? 'تعریف دست، تضاد کمدی و پیام آموزشی' : 'جهان داستان، زبان گرافیکی و پالت رنگ نئون'}
          </h2>
        </div>

        {stageStatus === 'approved' ? (
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            این مرحله تایید شد ✓
          </div>
        ) : (
          <button
            onClick={onApproveStage}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-black shadow-lg shadow-amber-500/20 transition-all"
          >
            <Check className="w-4 h-4" />
            تایید مرحله (Approve)
          </button>
        )}
      </div>

      {isIdea ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Editable Raw Poker Hand & Idea Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  ایده خام و شرح دست پوکر (موضوع و فرضیه کمدی)
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">قابل ویرایش</span>
              </div>

              <p className="text-xs text-slate-400">
                دست پوکر، موقعیت بازیکنان، اشتباه خنده‌دار یا مفهوم استراتژیک را بنویسید یا اصلاح کنید:
              </p>

              <textarea
                rows={7}
                value={rawIdeaText}
                onChange={(e) => setRawIdeaText(e.target.value)}
                placeholder="شرح دست پوکر، اشتباه خنده‌دار هیرو، پوزیشن‌ها یا استراتژی مورد نظر را بنویسید..."
                className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-100 leading-relaxed focus:border-amber-500 focus:outline-none resize-y"
              />
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <span className="text-[11px] text-slate-400">
                {saveSuccess ? (
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" />
                    ایده با موفقیت ذخیره شد!
                  </span>
                ) : (
                  'پرامپت AI Studio بر اساس این متن ساخته می‌شود.'
                )}
              </span>

              <button
                onClick={handleSaveIdea}
                disabled={isSaving}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20 transition-all hover:scale-102"
              >
                <Save className="w-3.5 h-3.5" />
                {isSaving ? 'در حال ذخیره...' : 'ذخیره ایده (Save Idea)'}
              </button>
            </div>
          </div>

          {/* Comedy Beats and Lessons Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              شوخی‌ها و دیالوگ‌های استخراج‌شده (Comedy Beats)
            </h3>
            
            {ideaData.core_lesson && (
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed">
                <strong className="text-amber-400 block mb-1">درس استراتژیک دست:</strong>
                {ideaData.core_lesson}
              </div>
            )}

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {(bibleData.comedy_beats || []).map((beat, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-xs text-emerald-200 leading-relaxed">
                  🃏 {beat}
                </div>
              ))}
              {(!bibleData.comedy_beats || bibleData.comedy_beats.length === 0) && (
                <div className="text-xs text-slate-400 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center">
                  شوخی‌ها و دیالوگ‌ها پس از اجرای پرامپت در Google AI Studio و ثبت JSON به این بخش اضافه می‌شوند.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-indigo-400 flex items-center gap-2">
              <BookTemplate className="w-4 h-4" />
              استایل بصری (Visual Style)
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              {bibleData.visual_style || 'انیمیشن دو بعدی مدرن'}
            </p>
            <div className="text-xs text-slate-400 font-mono">
              نسبت تصویر: {bibleData.frame_aspect_ratio || '9:16'}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
              <Palette className="w-4 h-4" />
              جزئیات دست و تیپ‌ها (Hand & Archetypes)
            </h3>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 text-xs text-slate-300">
              <div><strong>نوع بازی:</strong> {bibleData.hand_details?.game_type || 'NLH'}</div>
              <div><strong>عمق استک:</strong> {bibleData.hand_details?.effective_stack_bb || 100} BB</div>
              <div><strong>کارت‌های هیرو:</strong> {bibleData.hand_details?.hero_cards || 'A♠ K♥'}</div>
              <div><strong>بورد فلاپ:</strong> {bibleData.hand_details?.flop_board || '8♠ 4♦ 2♣'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
