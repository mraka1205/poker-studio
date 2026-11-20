import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  CheckCircle2, 
  Copy, 
  Check, 
  ArrowLeft, 
  UserCheck, 
  FileText, 
  Film, 
  Bot,
  User
} from 'lucide-react';
import { buildAiStudioPrompt } from '../api';
import { copyText as writeClipboard } from '../utils/clipboard';

export default function CommandCenter({
  projectState,
  onNavigateToStage,
  onApproveStage,
  onRefresh
}) {
  const [agentPromptData, setAgentPromptData] = useState(null);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedAnchor, setCopiedAnchor] = useState(false);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [promptError, setPromptError] = useState('');

  useEffect(() => {
    const epId = projectState?.episode_id;
    if (!epId) return;
    const PROMPT_STAGES = { 1: 'bible', 2: 'script', 3: 'characters', 5: 'scenes' };
    const stage = PROMPT_STAGES[projectState.current_stage];
    setPromptError('');
    if (!stage) {
      setAgentPromptData(null);
      setPromptError('برای این مرحله پرامپت ایجنت تعریف نشده است.');
      return;
    }
    let cancelled = false;
    setLoadingPrompt(true);
    buildAiStudioPrompt(epId, stage)
      .then(d => { if (!cancelled) setAgentPromptData(d); })
      .catch(e => { if (!cancelled) { setAgentPromptData(null); setPromptError('خطا در دریافت پرامپت: ' + e.message); } })
      .finally(() => { if (!cancelled) setLoadingPrompt(false); });
    return () => { cancelled = true; };
  }, [projectState?.episode_id, projectState?.current_stage]);

  const copyToClipboard = (text, setFlag) => {
    writeClipboard(text);
    setFlag(true);
    setTimeout(() => setFlag(false), 2000);
  };

  const currentStageNum = projectState?.current_stage || 1;
  const currentStageObj = projectState?.stages?.find(s => s.stage_number === currentStageNum);

  // Human Tasks: Find any stages or items waiting for user approval
  const waitingStages = (projectState?.stages || []).filter(s => s.status === 'waiting_approval' || s.status === 'in_progress');
  const waitingCharacters = (projectState?.characters || []).filter(c => c.status === 'waiting_approval');
  const waitingScenes = (projectState?.scenes || []).filter(sc => sc.status === 'ready_for_review');

  const anchorCharacter = (projectState?.characters || []).find(c => c.is_style_anchor);
  const anchorPrompt = anchorCharacter?.dna_block_en || anchorCharacter?.style_prompt || '';

  return (
    <div className="space-y-6">
      
      {/* Top Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl -z-10" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                استودیو امروز (Command Center)
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {projectState?.episode_id}
              </span>
            </div>
            
            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              {projectState?.title}
            </h2>

            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              {projectState?.idea?.core_lesson || "تولید قسمت جدید کمدی و آموزشی با سیستم مشارکتی انسان و هوش مصنوعی"}
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-3 bg-slate-900/80 p-3 rounded-xl border border-slate-800 backdrop-blur-sm self-start md:self-auto">
            <div className="text-center px-3 border-l border-slate-800">
              <div className="text-xs text-slate-400 font-medium">مرحله فعال</div>
              <div className="text-base font-bold text-amber-400">
                {currentStageObj?.name_fa} ({currentStageNum}/۸)
              </div>
            </div>
            <div className="text-center px-3 border-l border-slate-800">
              <div className="text-xs text-slate-400 font-medium">نسبت تصویر</div>
              <div className="text-base font-bold text-slate-200 font-mono">9:16 Shorts</div>
            </div>
            <div className="text-center px-3">
              <div className="text-xs text-slate-400 font-medium">وضعیت مرحله</div>
              <div className="text-xs font-bold text-emerald-400 mt-1">
                {currentStageObj?.status === 'approved' ? 'تایید شده ✓' : 'آماده اجرا / تایید'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: 2 Columns (Human Tasks vs Agent Turn) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* RIGHT COLUMN: Human Tasks ("منتظر تایید تو") */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <User className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white">منتظر تایید تو (Human in the Loop)</h3>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
              {waitingStages.length + waitingCharacters.length + waitingScenes.length} مورد
            </span>
          </div>

          <div className="space-y-3">
            {/* Stage approval card */}
            {currentStageObj && (
              <div className="p-4 rounded-xl bg-slate-900/90 border border-amber-500/30 hover:border-amber-500/50 transition-all space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
                      تایید مرحله جاری
                    </span>
                    <h4 className="text-sm font-bold text-slate-100">
                      مرحله {currentStageNum}: {currentStageObj.name_fa} ({currentStageObj.name_en})
                    </h4>
                    <p className="text-xs text-slate-400">
                      {currentStageObj.notes || "بررسی و صحه‌گذاری خروجی قبل از ورود به فاز بعدی"}
                    </p>
                  </div>
                  
                  {currentStageObj.status === 'approved' ? (
                    <span className="flex items-center gap-1 text-xs text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded-lg">
                      <CheckCircle2 className="w-4 h-4" />
                      تایید شد
                    </span>
                  ) : (
                    <button
                      onClick={() => onApproveStage(currentStageNum)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-600/20 transition-all"
                    >
                      <Check className="w-3.5 h-3.5" />
                      تایید مرحله (Approve)
                    </button>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-slate-400">مشاهده محتوای این مرحله:</span>
                  <button
                    onClick={() => onNavigateToStage(currentStageNum)}
                    className="text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1"
                  >
                    نمایش پنل اختصاصی
                    <ArrowLeft className="w-3 h-3" />
                  </button>
                </div>
              </div>
            )}

            {/* Waiting Characters approval */}
            {waitingCharacters.map(char => (
              <div key={char.id} className="p-3.5 rounded-xl bg-slate-900 border border-purple-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <img 
                      src={char.avatar_url || char.turnaround_sheet || char.face_sheet_image_path || ''} 
                      alt={char.name_fa} 
                      className="w-8 h-8 rounded-lg bg-slate-800 border border-purple-500/30"
                    />
                    <div>
                      <h5 className="text-xs font-bold text-slate-100">{char.name_fa}</h5>
                      <span className="text-[10px] text-purple-300">بررسی فوتوشیت کاراکتر</span>
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigateToStage(3)}
                    className="px-2.5 py-1 rounded-md bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 text-xs font-semibold"
                  >
                    بررسی در کاراکترها
                  </button>
                </div>
              </div>
            ))}

            {/* Waiting Scenes approval */}
            {waitingScenes.map(scene => (
              <div key={scene.scene_id || scene.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300 text-xs font-bold">
                      #{scene.beat_index ?? ''}
                    </div>
                    <div>
                      <h5 className="text-xs font-bold text-slate-200">{scene.scene_title_fa || scene.title || scene.scene_id}</h5>
                      <span className="text-[10px] text-slate-400">{scene.duration_sec ?? '?'}s • {scene.sfx_cue}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigateToStage(5)}
                    className="text-xs text-amber-400 hover:text-amber-300 font-medium"
                  >
                    مشاهده بیت بصری
                  </button>
                </div>
              </div>
            ))}

            {waitingStages.length === 0 && waitingCharacters.length === 0 && waitingScenes.length === 0 && (
              <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800 text-center space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                <p className="text-xs font-bold text-slate-200">همه وظایف تایید شده‌اند!</p>
                <p className="text-[11px] text-slate-400">می‌توانید پرامپت ایجنت را برای ادامه پایپ‌لاین کپی کنید.</p>
              </div>
            )}
          </div>

          {/* Style Anchor Info Card */}
          {anchorCharacter && (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-indigo-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-base">⭐</span>
                  <div>
                    <h4 className="text-xs font-bold text-indigo-200">لنگر استایل بصری (Style Anchor)</h4>
                    <p className="text-[10px] text-slate-400">{anchorCharacter.name_fa} ({anchorCharacter.role})</p>
                  </div>
                </div>

                <button
                  onClick={() => copyToClipboard(anchorPrompt, setCopiedAnchor)}
                  disabled={!anchorPrompt}
                  className="px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 text-xs font-semibold flex items-center gap-1 transition-colors"
                >
                  {copiedAnchor ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copiedAnchor ? 'کپی شد!' : 'کپی توکن استایل'}
                </button>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] font-mono text-slate-300 ltr-content line-clamp-2">
                {anchorPrompt}
              </div>
            </div>
          )}
        </div>

        {/* LEFT COLUMN: Agent Turn ("نوبت ایجنت") */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">نوبت ایجنت (Agent Turn Generator)</h3>
                <p className="text-xs text-slate-400">تولید خودکار پرامپت قدم بعدی متناسب با مهارت (Skill) و وضعیت فعلی پروژه</p>
              </div>
            </div>

            {agentPromptData && (
              <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-amber-300 border border-slate-700 font-mono">
                {agentPromptData.skill_file}
              </span>
            )}
          </div>

          {/* Prompt Generator Box */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs font-bold text-slate-200">
                  پرامپت مرحله {currentStageNum}: {agentPromptData?.stage_desc || 'در حال آماده‌سازی...'}
                </span>
              </div>

              <button
                onClick={() => copyToClipboard(agentPromptData?.prompt || '', setCopiedPrompt)}
                disabled={!agentPromptData?.prompt}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl font-bold text-xs transition-all shadow-lg ${
                  copiedPrompt
                    ? 'bg-emerald-500 text-slate-950'
                    : 'bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/20 hover:scale-[1.02]'
                }`}
              >
                {copiedPrompt ? (
                  <>
                    <Check className="w-4 h-4" />
                    پرامپت کپی شد!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    کپی پرامپت برای ایجنت (Copy Prompt)
                  </>
                )}
              </button>
            </div>

            {/* Prompt Viewport (Scrollable) */}
            <div className="relative">
              <pre className="p-4 rounded-xl bg-[#070b13] border border-slate-800/80 text-xs text-slate-300 font-mono overflow-x-auto max-h-[340px] whitespace-pre-wrap leading-relaxed ltr-content select-all">
                {loadingPrompt ? 'در حال کامپایل پرامپت اختصاصی مرحله...' : (agentPromptData?.prompt || promptError || 'پرامپتی یافت نشد.')}
              </pre>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
              <span>💡 این پرامپت را مستقیماً در چت ایجنت پیست کنید تا خروجی دقیق را تولید کند.</span>
              <button 
                onClick={onRefresh}
                className="text-slate-400 hover:text-white transition-colors"
              >
                بروزرسانی داده‌ها ↻
              </button>
            </div>
          </div>

          {/* Quick Stage Shortcuts */}
          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => onNavigateToStage(2)}
              className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 text-right group transition-all"
            >
              <div className="flex items-center justify-between mb-1">
                <FileText className="w-4 h-4 text-amber-400" />
                <span className="text-[10px] text-slate-500 font-mono">مرحله ۲</span>
              </div>
              <div className="text-xs font-bold text-slate-200 group-hover:text-amber-400 transition-colors">نمایش سناریو ۲ زبانه</div>
              <div className="text-[10px] text-slate-400 mt-0.5">زیرنویس و آوانویسی TTS</div>
            </button>

            <button
              onClick={() => onNavigateToStage(3)}
              className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 text-right group transition-all"
            >
              <div className="flex items-center justify-between mb-1">
                <UserCheck className="w-4 h-4 text-purple-400" />
                <span className="text-[10px] text-slate-500 font-mono">مرحله ۳</span>
              </div>
              <div className="text-xs font-bold text-slate-200 group-hover:text-purple-400 transition-colors">کاراکترها و لنگر استایل</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{`${projectState?.characters?.length ?? 0} کاراکتر`}</div>
            </button>

            <button
              onClick={() => onNavigateToStage(5)}
              className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 text-right group transition-all"
            >
              <div className="flex items-center justify-between mb-1">
                <Film className="w-4 h-4 text-emerald-400" />
                <span className="text-[10px] text-slate-500 font-mono">مرحله ۵</span>
              </div>
              <div className="text-xs font-bold text-slate-200 group-hover:text-emerald-400 transition-colors">بیت‌های ۱.۵ تا ۲.۵ ثانیه‌ای (استوری‌بورد)</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{`${projectState?.scenes?.length ?? 0} صحنه با وضعیت میز و SFX`}</div>
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}
