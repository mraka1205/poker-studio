import React, { useState, useEffect, useRef } from 'react';
import { 
  FileText, 
  Check, 
  CheckCircle2, 
  Copy, 
  Volume2, 
  Clock 
} from 'lucide-react';
import AiStudioBridge from './AiStudioBridge';
import { copyText as writeClipboard } from '../utils/clipboard';

const SPEAKER_STYLES = {
  narrator: { bg: 'bg-indigo-500/10', border: 'border-indigo-500/30', text: 'text-indigo-400', label: 'راوی (Narrator)' },
  narration: { bg: 'bg-indigo-500/10', border: 'border-indigo-500/30', text: 'text-indigo-400', label: 'راوی (Narrator)' },
  arash: { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', label: 'آرش (@Arash)' },
  kambiz: { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', label: 'کامبیز جیتیاو' },
  hero: { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', label: 'هیرو (HERO)' },
  bijan: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', label: 'بیژن (@Bijan)' },
  asghar: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', label: 'اصغر فیش' },
  villain: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', label: 'ویلن (VILLAIN)' },
  rahim: { bg: 'bg-sky-500/10', border: 'border-sky-500/30', text: 'text-sky-400', label: 'آقا رحیم (@Rahim)' },
  farzad: { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400', label: 'فرزاد (@Farzad)' },
  keyvan: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-400', label: 'کیوان (@Keyvan)' },
  behrouz: { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400', label: 'بهروز نیت (The Rock)' }
};

function getSpeakerStyle(speaker) {
  const key = String(speaker || '').replace(/^@/, '').trim().toLowerCase();
  return SPEAKER_STYLES[key] || {
    bg: 'bg-slate-500/10', border: 'border-slate-500/30', text: 'text-slate-300',
    label: speaker || 'نامشخص'
  };
}

export default function ScriptView({
  scriptData = {},
  episodeId,
  stageStatus,
  onApprove,
  onSaveScript,
  onRefresh
}) {
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [copiedAll, setCopiedAll] = useState(false);
  const [activeTab, setActiveTab] = useState('dual'); // 'dual', 'subtitle_only', 'tts_only'

  const [draft, setDraft] = useState(scriptData?.segments || []);
  const [saveState, setSaveState] = useState('idle'); // idle | dirty | saving | saved | error
  const draftRef = useRef(draft);
  const dirtyRef = useRef(false);
  const timerRef = useRef(null);
  const scriptRef = useRef(scriptData);
  useEffect(() => { scriptRef.current = scriptData; });

  useEffect(() => {
    if (!dirtyRef.current) {
      const next = scriptData?.segments || [];
      draftRef.current = next;
      setDraft(next);
    }
  }, [scriptData]);

  const flush = async () => {
    clearTimeout(timerRef.current);
    if (!dirtyRef.current) return;
    dirtyRef.current = false;
    setSaveState('saving');
    const ok = await onSaveScript({ ...scriptRef.current, segments: draftRef.current });
    if (ok === false) { dirtyRef.current = true; setSaveState('error'); } else { setSaveState('saved'); }
  };
  const flushRef = useRef(flush);
  flushRef.current = flush;
  useEffect(() => () => { if (dirtyRef.current) flushRef.current(); }, []);

  const copyText = (text, idx) => {
    writeClipboard(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const copyFullScript = () => {
    const text = JSON.stringify(scriptData, null, 2);
    writeClipboard(text);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const handleUpdateSegment = (idx, field, value) => {
    const next = draftRef.current.map((s, i) => (i === idx ? { ...s, [field]: value } : s));
    draftRef.current = next;
    setDraft(next);
    dirtyRef.current = true;
    setSaveState('dirty');
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => flushRef.current(), 800);
  };
  const segments = draft;

  return (
    <div className="space-y-6">
      
      {/* 1. AI Studio Bridge for Scriptwriting */}
      <AiStudioBridge
        episodeId={episodeId}
        stage="script"
        stageTitle="سناریونویسی"
        description="پرامپت مهندسی‌شده را برای Google AI Studio کپی کنید و خروجی ساختاریافته JSON شامل subtitle_fa و tts_fa را اینجا ثبت نمایید."
        onSuccess={() => {
          if (onRefresh) onRefresh();
        }}
      />

      {/* Script Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۳: سناریوی دو متنی (Dual-Text Script)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              تعداد بخش‌ها: {segments.length} سگمنت
            </span>
          </div>
          <h2 className="text-xl font-black text-white">{scriptData?.title || 'سناریوی کمدی اپیزود'}</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            می‌توانید متون زیرنویس و تلفظ TTS را مستقیماً ویرایش کرده یا با عامل هوشمند Antigravity اعراب‌گذاری آن را بروزرسانی نمایید.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-auto flex-wrap">
          {/* View Filter Switcher */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveTab('dual')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === 'dual' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              نمایش دوگانه
            </button>
            <button
              onClick={() => setActiveTab('subtitle_only')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === 'subtitle_only' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              فقط زیرنویس
            </button>
            <button
              onClick={() => setActiveTab('tts_only')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === 'tts_only' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              فقط TTS اعراب‌دار
            </button>
          </div>

          <button
            onClick={copyFullScript}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            {copiedAll ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copiedAll ? 'کپی شد!' : 'کپی کل JSON'}
          </button>

          <span className="text-[11px] text-slate-400 font-mono">
            {saveState === 'dirty' ? 'ذخیره نشده…' : saveState === 'saving' ? 'در حال ذخیره…' : saveState === 'saved' ? 'ذخیره شد ✓' : saveState === 'error' ? 'خطا در ذخیره' : ''}
          </span>

          {/* Approve Button */}
          {stageStatus === 'approved' ? (
            <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              سناریو تایید شد ✓
            </div>
          ) : (
            <button
              onClick={onApprove}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/20 transition-all hover:scale-105"
            >
              <Check className="w-4 h-4" />
              تایید سناریو (Approve)
            </button>
          )}
        </div>
      </div>

      {/* Script Segments List */}
      <div className="space-y-4">
        {segments.map((seg, idx) => {
          const spk = getSpeakerStyle(seg.speaker);

          return (
            <div
              key={seg.id || idx}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all space-y-4"
            >
              {/* Segment Metadata Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-lg bg-slate-800 flex items-center justify-center text-xs font-mono font-bold text-slate-400">
                    {idx + 1}
                  </span>

                  <span className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${spk.bg} ${spk.border} ${spk.text}`}>
                    {spk.label}
                  </span>

                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {seg.act || `بخش ${idx+1}`}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    مدت: {seg.estimated_duration_sec || seg.duration_est_sec || 5} ثانیه
                  </span>

                  {seg.emotion && (
                    <span className="text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800 font-mono text-[11px] ltr-content">
                      🎭 {seg.emotion}
                    </span>
                  )}

                  <button
                    onClick={() => copyText(seg.subtitle_fa, idx)}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                    title="کپی متن سگمنت"
                  >
                    {copiedIndex === idx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Poker Context Tag */}
              {seg.poker_context && (
                <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/90 flex items-center gap-2 text-xs">
                  <span className="text-amber-400 font-bold">🃏 وضعیت دست:</span>
                  <span className="text-slate-300 font-mono text-[11px] ltr-content">
                    {seg.poker_context}
                  </span>
                </div>
              )}

              {/* Dual-Text Display & Inline Editing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* 1. Subtitle Persian (Editable) */}
                {(activeTab === 'dual' || activeTab === 'subtitle_only') && (
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-400">
                      <span className="flex items-center gap-1 text-slate-300">
                        <FileText className="w-3.5 h-3.5 text-indigo-400" />
                        متن تمیز زیرنویس (Subtitle FA)
                      </span>
                      <span className="text-slate-500">قابل ویرایش</span>
                    </div>

                    <textarea
                      rows={2}
                      value={seg.subtitle_fa || ''}
                      onChange={(e) => handleUpdateSegment(idx, 'subtitle_fa', e.target.value)}
                      className="w-full p-3 rounded-xl bg-[#0b101c] border border-slate-800 text-sm font-medium text-slate-100 leading-relaxed focus:border-amber-500 focus:outline-none resize-y"
                    />
                  </div>
                )}

                {/* 2. TTS Phonetic Persian (Editable) */}
                {(activeTab === 'dual' || activeTab === 'tts_only') && (
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-400">
                      <span className="flex items-center gap-1 text-amber-300">
                        <Volume2 className="w-3.5 h-3.5 text-amber-400" />
                        متن آوانویسی شده هوش مصنوعی (TTS FA - اعراب‌دار)
                      </span>
                      <span className="text-amber-500/80 font-mono text-[10px]">ElevenLabs Optimized</span>
                    </div>

                    <textarea
                      rows={2}
                      value={seg.tts_fa || ''}
                      onChange={(e) => handleUpdateSegment(idx, 'tts_fa', e.target.value)}
                      className="w-full p-3 rounded-xl bg-amber-950/10 border border-amber-500/30 text-sm font-medium text-amber-100 leading-relaxed focus:border-amber-500 focus:outline-none resize-y"
                    />
                  </div>
                )}

              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
