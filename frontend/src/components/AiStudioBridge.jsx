import React, { useState } from 'react';
import { 
  Sparkles, 
  Copy, 
  Check, 
  ExternalLink, 
  ArrowDownToLine, 
  Code2, 
  AlertCircle, 
  ChevronDown, 
  ChevronUp, 
  Bot,
  Zap,
  CheckCircle2
} from 'lucide-react';
import { buildAiStudioPrompt, importAiStudioJson, runGeminiStage } from '../api';

export default function AiStudioBridge({
  episodeId,
  stage,
  stageTitle = "این مرحله",
  description = "تولید سریع با یک کلیک از طریق اتصال مستقیم به Google Gemini API یا استفاده از حالت دستی AI Studio.",
  onSuccess
}) {
  // Direct Gemini API state
  const [isRunningGemini, setIsRunningGemini] = useState(false);
  
  // Manual Bridge state
  const [showManualMode, setShowManualMode] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [jsonInput, setJsonInput] = useState('');
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [submittingJson, setSubmittingJson] = useState(false);

  // Status & Feedback
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleRunGemini = async () => {
    setIsRunningGemini(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await runGeminiStage(episodeId, stage);
      setSuccessMsg(res.message || 'با موفقیت توسط Gemini API تولید و ثبت شد!');
      if (onSuccess) {
        onSuccess(res.state);
      }
    } catch (err) {
      setErrorMsg(
        err.message?.includes('کلید Google Gemini API تنظیم نشده')
          ? 'کلید Gemini API یافت نشد. لطفاً از طریق آیکون چرخ‌دنده (بالای صفحه) کلید Google AI Studio خود را وارد کنید.'
          : 'خطا در اجرای Gemini API: ' + err.message
      );
    } finally {
      setIsRunningGemini(false);
    }
  };

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
      
      {/* Primary Row: Title, 1-Click Gemini Button & Manual Toggle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Info & Title */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-amber-500 via-orange-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-amber-500/25 flex-shrink-0">
            <Zap className="w-5 h-5 text-slate-950 fill-current" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-sm font-black text-white">
                تولید هوشمند با Google AI Studio (Gemini)
              </h3>
              <span className="text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-md">
                مرحله: {stageTitle}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">{description}</p>
          </div>
        </div>

        {/* Action Buttons: 1-Click Primary Gemini + Manual Accordion Toggle */}
        <div className="flex items-center gap-2.5 flex-wrap self-start md:self-auto flex-shrink-0">
          
          {/* Primary 1-Click Button */}
          <button
            onClick={handleRunGemini}
            disabled={isRunningGemini}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-orange-400 hover:from-amber-400 hover:to-orange-300 text-slate-950 text-xs font-black shadow-lg shadow-amber-500/25 transition-all hover:scale-102 disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 ${isRunningGemini ? 'animate-spin' : ''}`} />
            {isRunningGemini ? 'در حال تولید خودکار با Gemini API...' : 'تولید خودکار با Gemini API (AI Studio)'}
          </button>

          {/* Collapsible Manual Toggle */}
          <button
            type="button"
            onClick={() => setShowManualMode(!showManualMode)}
            className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Code2 className="w-3.5 h-3.5 text-amber-400" />
            حالت دستی (Manual JSON Paste)
            {showManualMode ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Success Alert */}
      {successMsg && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/50 text-emerald-200 text-xs font-semibold flex items-center gap-2 shadow-lg">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Error Alert */}
      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-200 text-xs font-semibold flex items-center gap-2.5 shadow-lg">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span className="leading-relaxed">{errorMsg}</span>
        </div>
      )}

      {/* Collapsible Manual Mode Section */}
      {showManualMode && (
        <div className="pt-4 border-t border-slate-800/80 space-y-3 bg-slate-950/40 p-4 rounded-xl border border-slate-800">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
              <span>📋</span> روش دستی: کپی پرامپت و پیست JSON خروجی
            </span>
            <div className="flex items-center gap-2">
              <a
                href="https://aistudio.google.com/app/prompts/new_chat"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] font-semibold text-slate-200 transition-colors"
              >
                باز کردن وب‌سایت AI Studio
                <ExternalLink className="w-3 h-3 text-amber-400" />
              </a>

              <button
                type="button"
                onClick={handleCopyPrompt}
                disabled={loadingPrompt}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-black transition-all ${
                  copiedPrompt
                    ? 'bg-emerald-500 text-slate-950'
                    : 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                }`}
              >
                {copiedPrompt ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    پرامپت کپی شد!
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    {loadingPrompt ? 'در حال دریافت...' : 'کپی پرامپت کامل مهارت'}
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-2 pt-1">
            <textarea
              rows={3}
              placeholder='خروجی JSON دریافت شده از AI Studio را اینجا Paste کنید (مثال: { "segments": [...] } یا { "concept_summary": ... })...'
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              className="flex-1 p-3 rounded-xl bg-slate-950 border border-slate-700 text-xs font-mono text-slate-200 focus:border-amber-500 focus:outline-none ltr-content resize-y"
            />

            <button
              type="button"
              onClick={handleImportJson}
              disabled={submittingJson || !jsonInput.trim()}
              className="sm:w-44 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2 transition-all self-end sm:self-auto"
            >
              <ArrowDownToLine className="w-4 h-4" />
              {submittingJson ? 'در حال ثبت...' : 'ثبت و تایید JSON خروجی'}
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
