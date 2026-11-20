import React, { useState, useEffect } from 'react';
import { 
  Lightbulb, 
  Check, 
  CheckCircle2, 
  Sparkles, 
  Palette, 
  Save, 
  Users, 
  FileText 
} from 'lucide-react';
import AiStudioBridge from './AiStudioBridge';
import { saveEpisodeIdea } from '../api';

export default function IdeaBibleView({
  ideaData = {},
  bibleData = {},
  episodeId,
  stageStatus,
  onApproveStage,
  onRefresh
}) {
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

  const concept = bibleData?.concept_summary || {};
  const theme = concept.theme || ideaData?.theme || '';
  const lesson = concept.poker_lesson || ideaData?.core_lesson || '';
  const gtoVsExploit = concept.gto_vs_exploit || '';

  const hand = bibleData?.hand_details || {};
  const hasHandDetails = Object.keys(hand).length > 0;

  const archetypes = bibleData?.archetypes || [];
  const comedyBeats = bibleData?.comedy_beats || [];

  return (
    <div className="space-y-6">
      
      {/* AI Studio Bridge for Idea & Bible (Skill 01) */}
      <AiStudioBridge
        episodeId={episodeId}
        stage="bible"
        stageTitle="ایده و کتابچه استراتژی دست (Idea & Bible)"
        description="پرامپت مهارت ۰۱ را برای Gemini کپی کنید تا مفهوم GTO vs Exploit، جزئیات کامل دست و جوک‌های اصیل پوکر ایرانی بر اساس ایده خام ثبت‌شده در قالب JSON تولید شود."
        onSuccess={() => {
          if (onRefresh) onRefresh();
        }}
      />

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۱: ایده و کتابچه استراتژی دست (Idea & Bible)
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            تعریف دست، کانسپت کمدی، تحلیل GTO و کتابچه استراتژی اپیزود
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            ایده اولیه و دست پوکر را ویرایش کنید و کتابچه تولیدشده با هوش مصنوعی را بازبینی و تایید نمایید.
          </p>
        </div>

        {stageStatus === 'approved' ? (
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ایده و کتابچه تایید شد ✓
          </div>
        ) : (
          <button
            onClick={onApproveStage}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-black shadow-lg shadow-amber-500/20 transition-all hover:scale-102"
          >
            <Check className="w-4 h-4" />
            تایید ایده و کتابچه (Approve)
          </button>
        )}
      </div>

      {/* Row 1: Editable Raw Idea (Card 1) & Strategy / GTO vs Exploit (Card 2) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Card 1: Editable Raw Poker Hand & Idea */}
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
              rows={8}
              value={rawIdeaText}
              onChange={(e) => setRawIdeaText(e.target.value)}
              placeholder="شرح دست پوکر، اشتباه خنده‌دار هیرو، پوزیشن‌ها یا استراتژی مورد نظر را بنویسید..."
              className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-100 leading-relaxed focus:border-amber-500 focus:outline-none resize-y font-sans"
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
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20 transition-all hover:scale-102 disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              {isSaving ? 'در حال ذخیره...' : 'ذخیره ایده (Save Idea)'}
            </button>
          </div>
        </div>

        {/* Card 2: Strategy & GTO vs Exploit */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            استراتژی دست، درس کلیدی و تحلیل GTO vs Exploit
          </h3>

          {theme && (
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] font-bold text-amber-400 block mb-1">تم و پیام محوری:</span>
              <p className="text-xs text-slate-200 leading-relaxed">{theme}</p>
            </div>
          )}

          {lesson && (
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] font-bold text-emerald-400 block mb-1">درس طلایی و استراتژیک (Core Lesson):</span>
              <p className="text-xs text-slate-200 leading-relaxed">{lesson}</p>
            </div>
          )}

          {gtoVsExploit ? (
            <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/20 text-xs text-slate-300 leading-relaxed">
              <span className="text-[11px] font-bold text-indigo-400 block mb-1">تحلیل GTO در برابر Exploit:</span>
              <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed">{gtoVsExploit}</p>
            </div>
          ) : (
            !theme && !lesson && (
              <div className="text-xs text-slate-400 p-6 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center">
                کانسپت، درس استراتژیک و تحلیل GTO vs Exploit پس از ایمپورت JSON کتابچه در این بخش قرار می‌گیرد.
              </div>
            )
          )}
        </div>
      </div>

      {/* Row 2: Complete Hand Details (Card 3) & Archetypes & Comedy Beats (Card 4) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Card 3: Complete Hand Details */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
              <Palette className="w-4 h-4" />
              جزئیات دقیق دست پوکر (Hand Details)
            </h3>
            {hasHandDetails && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                {hand.game_type || 'NLH'}
              </span>
            )}
          </div>

          {hasHandDetails ? (
            <div className="space-y-3">
              {/* Meta stats bar */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">استک مؤثر</span>
                  <span className="font-bold text-slate-200 font-mono">{hand.effective_stack_bb ?? 100} BB</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">بلایندها</span>
                  <span className="font-bold text-slate-200 font-mono">{hand.blinds_bb || '1/2'}</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">پات نهایی</span>
                  <span className="font-bold text-emerald-400 font-mono">{hand.final_pot_bb ? `${hand.final_pot_bb} BB` : '-'}</span>
                </div>
              </div>

              {/* Player Holdings */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-amber-400 font-bold block mb-0.5">
                    هیرو ({hand.hero_position || 'BTN'}) {hand.hero_tag || ''}
                  </span>
                  <span className="text-slate-200 font-mono font-bold text-sm">{hand.hero_cards || '-'}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-rose-400 font-bold block mb-0.5">
                    حریف ({hand.villain_position || 'BB'}) {hand.villain_tag || ''}
                  </span>
                  <span className="text-slate-200 font-mono font-bold text-sm">{hand.villain_cards || '-'}</span>
                </div>
              </div>

              {/* Street by street action */}
              <div className="space-y-1.5 text-xs">
                {hand.preflop_action && (
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                    <strong className="text-amber-300 text-[11px] block">پیش‌فلاپ (Preflop):</strong>
                    <span className="text-slate-300">{hand.preflop_action}</span>
                  </div>
                )}
                {(hand.flop_board || hand.flop_action) && (
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                    <div className="flex items-center justify-between mb-0.5">
                      <strong className="text-emerald-300 text-[11px]">فلاپ (Flop):</strong>
                      <span className="font-mono font-bold text-emerald-400 text-xs">{hand.flop_board || ''}</span>
                    </div>
                    {hand.flop_action && <span className="text-slate-300">{hand.flop_action}</span>}
                  </div>
                )}
                {(hand.turn_board || hand.turn_action) && (
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                    <div className="flex items-center justify-between mb-0.5">
                      <strong className="text-blue-300 text-[11px]">ترن (Turn):</strong>
                      <span className="font-mono font-bold text-blue-400 text-xs">{hand.turn_board || ''}</span>
                    </div>
                    {hand.turn_action && <span className="text-slate-300">{hand.turn_action}</span>}
                  </div>
                )}
                {(hand.river_board || hand.river_action) && (
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                    <div className="flex items-center justify-between mb-0.5">
                      <strong className="text-purple-300 text-[11px]">ریور (River):</strong>
                      <span className="font-mono font-bold text-purple-400 text-xs">{hand.river_board || ''}</span>
                    </div>
                    {hand.river_action && <span className="text-slate-300">{hand.river_action}</span>}
                  </div>
                )}
                {hand.winning_hand && (
                  <div className="p-2 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-200">
                    <strong>دست برنده: </strong> {hand.winning_hand}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-400 p-6 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center">
              جزئیات فنی دست (نوع بازی، پوزیشن‌ها، کارت‌ها و اکشن خیابان‌ها) پس از ایمپورت کتابچه در این بخش نمایش داده می‌شود.
            </div>
          )}
        </div>

        {/* Card 4: Archetypes & Comedy Beats */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-indigo-400 flex items-center gap-2">
            <Users className="w-4 h-4" />
            تیپ‌های شخصیتی و شوخی‌های استخراج‌شده (Archetypes & Comedy Beats)
          </h3>

          {/* Archetypes */}
          {archetypes.length > 0 && (
            <div className="space-y-2">
              <span className="text-[11px] font-bold text-slate-400 block">کاراکترهای حاضر در دست:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {archetypes.map((arch, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-indigo-500/20 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-indigo-200">{arch.name || arch.flow_tag}</span>
                      <span className="text-[10px] text-amber-400 font-mono">{arch.flow_tag}</span>
                    </div>
                    {arch.role && <div className="text-[10px] text-slate-400 mb-0.5">{arch.role}</div>}
                    {arch.mindset && <div className="text-[11px] text-slate-300 leading-relaxed">{arch.mindset}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Comedy Beats */}
          <div className="space-y-2">
            <span className="text-[11px] font-bold text-slate-400 block">جوک‌ها و موقعیت‌های کمدی (Comedy Beats):</span>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {comedyBeats.map((beat, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed flex items-start gap-2">
                  <span className="w-5 h-5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span>{beat}</span>
                </div>
              ))}
              {comedyBeats.length === 0 && (
                <div className="text-xs text-slate-400 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center">
                  شوخی‌ها و دیالوگ‌ها پس از ایمپورت JSON در این بخش قرار می‌گیرند.
                </div>
              )}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
