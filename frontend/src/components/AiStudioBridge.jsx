import React, { useState } from 'react';
import { 
  Sparkles, 
  Copy, 
  Check, 
  ArrowDownToLine, 
  Code2, 
  ChevronDown, 
  ChevronUp, 
  Bot,
  CheckCircle2
} from 'lucide-react';
import { buildAiStudioPrompt, importAiStudioJson } from '../api';

export default function AiStudioBridge({
  episodeId,
  stage,
  stageTitle = "این مرحله",
  description = "کپی پرامپت مهارت برای اجرای مستقیم توسط عامل هوشمند Antigravity یا ورود مستقیم خروجی JSON.",
  onSuccess
}) {
  const [showManualJson, setShowManualJson] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [jsonInput, setJsonInput] = useState('');
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [submittingJson, setSubmittingJson] = useState(false);

  // Status & Feedback
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleCopyPrompt = async () => {
    setLoadingPrompt(true);
    setErrorMsg('');
    try {
      const res = await buildAiStudioPrompt(episodeId, stage);
      await navigator.clipboard.writeText(res.prompt);
      setCopiedPrompt(true);
      setTimeout(() => setCopiedPrompt(false), 2500);
    } catch (err) {
      setErrorMsg('خطا در دریافت پرامپت: ' + err.message);
    } finally {
      setLoadingPrompt(false);
    }
  };

  const handleImportJson = async () => {
    if (!jsonInput.trim()) {
      setErrorMsg('لطفاً ابتدا خروجی JSON را در کادر متنی پیست کنید.');
      return;
    }

    setSubmittingJson(true);
    setErrorMsg('');
    try {
      const res = await importAiStudioJson(episodeId, stage, jsonInput);
      setSuccessMsg(res.message || 'داده‌ها با موفقیت اعتبارسنجی و ذخیره شد!');
      setJsonInput('');
      if (onSuccess) {
        onSuccess(res.state);
      }
    } catch (err) {
      setErrorMsg('خطا در ثبت JSON: ' + err.message);
    } finally {
      setSubmittingJson(false);
    }
  };

  return (
    <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-amber-500/30 p-5 space-y-4 shadow-xl shadow-amber-500/5">
      
      {/* Primary Row: Title & Action Button */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Bot className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-extrabold text-white flex items-center gap-1.5">
              <span>دستور اجرای {stageTitle} در آنتی‌گرویتی</span>
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Antigravity Native
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
            {description}
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Copy Prompt for Antigravity Agent */}
          <button
            onClick={handleCopyPrompt}
            disabled={loadingPrompt}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md ${
              copiedPrompt
                ? 'bg-emerald-500 text-slate-950 font-black'
                : 'bg-amber-500 hover:bg-amber-400 text-slate-950 hover:scale-102 shadow-amber-500/20'
            }`}
          >
            {copiedPrompt ? (
              <>
                <Check className="w-4 h-4 text-slate-950" />
                پرامپت کپی شد!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 text-slate-950" />
                {loadingPrompt ? 'در حال آماده‌سازی...' : 'کپی پرامپت اجرای این مرحله'}
              </>
            )}
          </button>

          {/* Toggle Manual JSON Import */}
          <button
            onClick={() => setShowManualJson(!showManualJson)}
            className="flex items-center gap-1 px-3 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
          >
            <Code2 className="w-3.5 h-3.5 text-amber-400" />
            ورود دستی JSON
            {showManualJson ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Messages */}
      {successMsg && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold">
          {errorMsg}
        </div>
      )}

      {/* Collapsible Manual JSON Import Area */}
      {showManualJson && (
        <div className="pt-3 border-t border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Code2 className="w-3.5 h-3.5 text-indigo-400" />
              خروجی JSON مرحله را در کادر زیر پیست کرده و ذخیره نمایید:
            </span>
          </div>

          <textarea
            rows={5}
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder='{\n  "key": "value"...\n}'
            className="w-full p-3 rounded-xl bg-[#070b13] border border-slate-800 text-xs font-mono text-emerald-400 focus:outline-none focus:border-amber-500 ltr-content leading-relaxed"
          />

          <div className="flex justify-end">
            <button
              onClick={handleImportJson}
              disabled={submittingJson || !jsonInput.trim()}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-slate-950 font-bold text-xs shadow-md transition-all hover:scale-102"
            >
              <ArrowDownToLine className="w-4 h-4" />
              {submittingJson ? 'در حال ثبت و اعتبارسنجی...' : 'ذخیره و همگام‌سازی JSON'}
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
