import React, { useState, useEffect } from 'react';
import { 
  X, 
  Settings, 
  Key, 
  Cpu, 
  Check, 
  ExternalLink, 
  ShieldCheck, 
  AlertCircle, 
  RefreshCw,
  Sparkles,
  Bot,
  Search,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { fetchSettings, saveSettings, fetchGeminiModels, fetchOpenRouterModels } from '../api';

const POPULAR_OPENROUTER_MODELS = [
  'google/gemini-2.5-flash',
  'deepseek/deepseek-chat',
  'anthropic/claude-3.5-sonnet',
  'meta-llama/llama-3.3-70b-instruct',
  'qwen/qwen-2.5-72b-instruct'
];

const POPULAR_GEMINI_MODELS = [
  'gemini-2.5-flash',
  'gemini-2.5-pro',
  'gemini-2.0-flash',
  'gemini-1.5-pro',
  'gemini-1.5-flash'
];

export default function SettingsModal({ isOpen, onClose }) {
  // OpenRouter State
  const [openrouterApiKey, setOpenrouterApiKey] = useState('');
  const [openrouterModel, setOpenrouterModel] = useState('google/gemini-2.5-flash');
  const [hasOpenrouterKey, setHasOpenrouterKey] = useState(false);
  const [maskedOpenrouterKey, setMaskedOpenrouterKey] = useState('');
  
  // OpenRouter Live Models State
  const [availableOpenrouterModels, setAvailableOpenrouterModels] = useState([]);
  const [fetchingOpenrouterModels, setFetchingOpenrouterModels] = useState(false);
  const [openrouterModelsError, setOpenrouterModelsError] = useState('');
  const [openrouterSearchQuery, setOpenrouterSearchQuery] = useState('');
  const [showOpenrouterDropdown, setShowOpenrouterDropdown] = useState(false);

  // Gemini State
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [geminiModel, setGeminiModel] = useState('gemini-2.5-flash');
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [maskedGeminiKey, setMaskedGeminiKey] = useState('');
  
  // Gemini Live Models State
  const [availableGeminiModels, setAvailableGeminiModels] = useState([]);
  const [fetchingGeminiModels, setFetchingGeminiModels] = useState(false);
  const [geminiModelsError, setGeminiModelsError] = useState('');
  const [geminiSearchQuery, setGeminiSearchQuery] = useState('');
  const [showGeminiDropdown, setShowGeminiDropdown] = useState(false);

  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadCurrentSettings();
    }
  }, [isOpen]);

  const loadCurrentSettings = async () => {
    try {
      const data = await fetchSettings();
      setHasOpenrouterKey(data.has_openrouter_key || data.has_key);
      setMaskedOpenrouterKey(data.openrouter_api_key_masked || '');
      if (data.openrouter_model) {
        setOpenrouterModel(data.openrouter_model);
      }

      setHasGeminiKey(data.has_gemini_key);
      setMaskedGeminiKey(data.gemini_api_key_masked || '');
      if (data.gemini_model) {
        setGeminiModel(data.gemini_model);
      }
    } catch (err) {
      console.error('Error loading settings', err);
    }
  };

  const handleFetchGeminiModels = async () => {
    setFetchingGeminiModels(true);
    setGeminiModelsError('');
    try {
      const res = await fetchGeminiModels(geminiApiKey.trim() || null);
      if (res.models && res.models.length > 0) {
        setAvailableGeminiModels(res.models);
        setShowGeminiDropdown(true);
      } else {
        setGeminiModelsError('هیچ مدلی یافت نشد. لطفاً کلید API را بررسی کنید.');
      }
    } catch (err) {
      setGeminiModelsError(err.message || 'خطا در دریافت مدل‌های Gemini');
    } finally {
      setFetchingGeminiModels(false);
    }
  };

  const handleFetchOpenrouterModels = async () => {
    setFetchingOpenrouterModels(true);
    setOpenrouterModelsError('');
    try {
      const res = await fetchOpenRouterModels(openrouterApiKey.trim() || null);
      if (res.models && res.models.length > 0) {
        setAvailableOpenrouterModels(res.models);
        setShowOpenrouterDropdown(true);
      } else {
        setOpenrouterModelsError('هیچ مدلی از سرور OpenRouter بازگردانده نشد.');
      }
    } catch (err) {
      setOpenrouterModelsError(err.message || 'خطا در دریافت لیست مدل‌های OpenRouter');
    } finally {
      setFetchingOpenrouterModels(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSavedSuccess(false);
    setSaveSuccessMsg('');
    try {
      const res = await saveSettings(
        openrouterApiKey.trim() || undefined,
        openrouterModel.trim() || undefined,
        geminiApiKey.trim() || undefined,
        geminiModel.trim() || undefined
      );

      // Immediately update status badges from returned settings
      if (res && res.settings) {
        setHasOpenrouterKey(res.settings.has_openrouter_key);
        setMaskedOpenrouterKey(res.settings.openrouter_api_key_masked || '');
        setHasGeminiKey(res.settings.has_gemini_key);
        setMaskedGeminiKey(res.settings.gemini_api_key_masked || '');
        if (res.settings.gemini_model) setGeminiModel(res.settings.gemini_model);
        if (res.settings.openrouter_model) setOpenrouterModel(res.settings.openrouter_model);
      } else {
        await loadCurrentSettings();
      }

      setSavedSuccess(true);
      setSaveSuccessMsg('تنظیمات و کلیدهای هوش مصنوعی با موفقیت در .env ذخیره شد!');
      setOpenrouterApiKey('');
      setGeminiApiKey('');

      setTimeout(() => {
        setSavedSuccess(false);
      }, 4000);
    } catch (err) {
      alert('خطا در ذخیره تنظیمات: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filtered Gemini Models
  const filteredGeminiModels = availableGeminiModels.filter((m) => {
    const query = geminiSearchQuery.toLowerCase().trim();
    if (!query) return true;
    const cleanId = (m.id || m.clean_name || m.name || '').replace(/^models\//, '').toLowerCase();
    const dName = (m.displayName || m.display_name || '').toLowerCase();
    return cleanId.includes(query) || dName.includes(query);
  });

  // Filtered OpenRouter Models
  const filteredOpenrouterModels = availableOpenrouterModels.filter((m) => {
    const query = openrouterSearchQuery.toLowerCase().trim();
    if (!query) return true;
    const idMatch = m.id?.toLowerCase().includes(query);
    const nameMatch = m.name?.toLowerCase().includes(query);
    return idMatch || nameMatch;
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-6 max-h-[92vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">تنظیمات هوش مصنوعی (Google Gemini & OpenRouter)</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Success Toast */}
        {savedSuccess && (
          <div className="p-3.5 rounded-xl bg-emerald-950/80 border border-emerald-500/60 text-emerald-200 text-xs font-semibold flex items-center gap-2 shadow-lg animate-fade-in">
            <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{saveSuccessMsg || 'تنظیمات با موفقیت ذخیره شد!'}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6 text-xs">
          
          {/* ======================================================== */}
          {/* SECTION 1: Google Gemini (AI Studio) */}
          {/* ======================================================== */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-amber-500/30 space-y-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-black text-amber-300">
                  Google AI Studio (Gemini API مستقیم)
                </span>
              </div>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-amber-400 hover:underline flex items-center gap-1 text-[11px]"
              >
                دریافت کلید رایگان AI Studio
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            
            <p className="text-[11px] text-slate-400 leading-relaxed">
              برای تولید ۱-کلیک مراحل خلاقانه (مفهوم و جوک‌های پوکر، سناریوی دو متنی با اعراب TTS، و پرامپت‌های مدل‌شیت کاراکترها) مستقیماً با مدل‌های Gemini استفاده می‌شود.
            </p>

            {/* Status Badge */}
            <div className="flex items-center justify-between py-2 px-3 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 font-medium">وضعیت کلید Gemini:</span>
              {hasGeminiKey ? (
                <span className="flex items-center gap-1.5 text-emerald-400 font-bold font-mono">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  تنظیم شده ({maskedGeminiKey})
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-rose-400 font-bold">
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                  تنظیم نشده
                </span>
              )}
            </div>

            {/* Gemini API Key Input */}
            <div className="space-y-1">
              <label className="text-slate-300 font-bold block">
                کلید Gemini API (در فایل <code className="text-amber-400 font-mono">.env</code> ذخیره می‌شود):
              </label>
              <input
                type="password"
                placeholder={hasGeminiKey ? "برای تغییر کلید، کلید جدید را وارد کنید (AIzaSy...)" : "AIzaSy..."}
                value={geminiApiKey}
                onChange={(e) => setGeminiApiKey(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 font-mono ltr-content focus:border-amber-500 focus:outline-none text-xs"
              />
            </div>

            {/* Gemini Model ID Input + Fetch Button */}
            <div className="space-y-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-slate-300 font-bold flex items-center gap-1">
                  <Cpu className="w-3.5 h-3.5 text-amber-400" />
                  شناسه مدل Gemini (متن آزاد اسلاگ مدل):
                </label>
                <button
                  type="button"
                  onClick={handleFetchGeminiModels}
                  disabled={fetchingGeminiModels}
                  className="flex items-center gap-1.5 text-[11px] font-bold text-amber-300 hover:text-white bg-amber-500/20 hover:bg-amber-500/40 border border-amber-500/40 px-2.5 py-1 rounded-lg transition-all"
                >
                  <RefreshCw className={`w-3 h-3 ${fetchingGeminiModels ? 'animate-spin' : ''}`} />
                  {fetchingGeminiModels ? 'در حال دریافت مدل‌ها...' : 'دریافت مدل‌ها از کلید (Fetch Models)'}
                </button>
              </div>

              <input
                type="text"
                value={geminiModel}
                onChange={(e) => setGeminiModel(e.target.value)}
                placeholder="مثلاً gemini-2.5-flash یا gemini-2.5-pro"
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 font-mono ltr-content focus:border-amber-500 focus:outline-none"
              />

              {/* Quick model pills */}
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="text-[10px] text-slate-500 self-center">پیشنهادی:</span>
                {POPULAR_GEMINI_MODELS.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setGeminiModel(m)}
                    className={`px-2 py-0.5 rounded-md text-[10px] font-mono transition-all ${
                      geminiModel === m
                        ? 'bg-amber-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>

              {/* Toggle Gemini List */}
              {availableGeminiModels.length > 0 && (
                <div className="pt-1">
                  <button
                    type="button"
                    onClick={() => setShowGeminiDropdown(!showGeminiDropdown)}
                    className="flex items-center gap-1 text-[11px] font-semibold text-amber-400 hover:text-amber-300"
                  >
                    {showGeminiDropdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    <span>
                      {showGeminiDropdown 
                        ? 'بستن لیست مدل‌های Gemini' 
                        : `مشاهده مدل‌های زنده حساب شما (${availableGeminiModels.length} مدل فعال)`}
                    </span>
                  </button>
                </div>
              )}

              {/* SEARCHABLE GEMINI MODELS CHIPS / LIST */}
              {showGeminiDropdown && availableGeminiModels.length > 0 && (
                <div className="p-3 rounded-xl bg-slate-900 border border-amber-500/40 space-y-2 shadow-xl">
                  {/* Search Filter */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-2.5" />
                    <input
                      type="text"
                      value={geminiSearchQuery}
                      onChange={(e) => setGeminiSearchQuery(e.target.value)}
                      placeholder="فیلتر مدل‌های Gemini (مثلاً 2.5, pro, flash)..."
                      className="w-full pr-8 pl-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs focus:border-amber-500 focus:outline-none"
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 px-1">
                    <span>تعداد مدل‌های منطبق: {filteredGeminiModels.length}</span>
                    <span>برای انتخاب روی مدل کلیک کنید</span>
                  </div>

                  {/* Clickable chips/cards */}
                  <div className="max-h-52 overflow-y-auto space-y-1.5 pr-1">
                    {filteredGeminiModels.length === 0 ? (
                      <div className="text-center py-4 text-slate-500 text-xs">
                        مدلی با این عبارت پیدا نشد.
                      </div>
                    ) : (
                      filteredGeminiModels.map((m, idx) => {
                        const cleanId = (
                          m.id || 
                          m.clean_name || 
                          m.name || 
                          ''
                        ).replace(/^models\//, '');
                        
                        const displayName = m.displayName || m.display_name || cleanId;
                        const isSelected = geminiModel === cleanId;

                        return (
                          <div
                            key={cleanId || idx}
                            onClick={() => {
                              setGeminiModel(cleanId);
                              setShowGeminiDropdown(false);
                            }}
                            className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all ${
                              isSelected
                                ? 'bg-amber-500/20 border border-amber-500/50 text-amber-200'
                                : 'hover:bg-slate-800 text-slate-300'
                            }`}
                          >
                            <div className="space-y-0.5 truncate pr-2">
                              <div className="text-xs font-bold text-slate-200 truncate">
                                {displayName}
                              </div>
                              <div className="text-[10px] font-mono text-amber-400 truncate ltr-content">
                                {cleanId}
                              </div>
                            </div>

                            <div className="flex items-center gap-2 flex-shrink-0">
                              {isSelected ? (
                                <Check className="w-4 h-4 text-amber-400" />
                              ) : (
                                <span className="text-[10px] font-mono text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">
                                  انتخاب
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}

              {geminiModelsError && (
                <div className="text-[11px] text-rose-400 bg-rose-950/40 p-2 rounded-lg border border-rose-800/40">
                  {geminiModelsError}
                </div>
              )}
            </div>
          </div>

          {/* ======================================================== */}
          {/* SECTION 2: OpenRouter API */}
          {/* ======================================================== */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/30 space-y-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-black text-emerald-300">
                  OpenRouter API (استوری‌بورد و پرامپت‌های ویدیویی Google Flow)
                </span>
              </div>
              <a
                href="https://openrouter.ai/keys"
                target="_blank"
                rel="noreferrer"
                className="text-emerald-400 hover:underline flex items-center gap-1 text-[11px]"
              >
                دریافت کلید OpenRouter
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            {/* Status */}
            <div className="flex items-center justify-between py-2 px-3 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 font-medium">وضعیت کلید OpenRouter:</span>
              {hasOpenrouterKey ? (
                <span className="flex items-center gap-1.5 text-emerald-400 font-bold font-mono">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  تنظیم شده ({maskedOpenrouterKey})
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-rose-400 font-bold">
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                  تنظیم نشده
                </span>
              )}
            </div>

            {/* OpenRouter API Key Input */}
            <div className="space-y-1">
              <label className="text-slate-300 font-bold block">
                کلید OpenRouter API (در فایل <code className="text-emerald-400 font-mono">.env</code> ذخیره می‌شود):
              </label>
              <input
                type="password"
                placeholder={hasOpenrouterKey ? "برای تغییر، کلید جدید OpenRouter را وارد کنید (sk-or-v1-...)" : "sk-or-v1-..."}
                value={openrouterApiKey}
                onChange={(e) => setOpenrouterApiKey(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 font-mono ltr-content focus:border-emerald-500 focus:outline-none text-xs"
              />
            </div>

            {/* OpenRouter Model: Free-Text Input + Live Fetch Button */}
            <div className="space-y-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-slate-300 font-bold flex items-center gap-1">
                  <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                  شناسه مدل OpenRouter (ورود متن آزاد اسلاگ مدل):
                </label>

                <button
                  type="button"
                  onClick={handleFetchOpenrouterModels}
                  disabled={fetchingOpenrouterModels}
                  className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-300 hover:text-white bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/40 px-2.5 py-1 rounded-lg transition-all"
                >
                  <RefreshCw className={`w-3 h-3 ${fetchingOpenrouterModels ? 'animate-spin' : ''}`} />
                  {fetchingOpenrouterModels 
                    ? 'در حال دریافت مدل‌های زنده...' 
                    : 'دریافت لیست مدلهای زنده OpenRouter (Fetch Live Models)'}
                </button>
              </div>

              {/* Free-text input field for ANY exact slug */}
              <input
                type="text"
                value={openrouterModel}
                onChange={(e) => setOpenrouterModel(e.target.value)}
                placeholder="مثلاً deepseek/deepseek-chat یا google/gemini-2.5-flash یا anthropic/claude-3.5-sonnet"
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 font-mono ltr-content focus:border-emerald-500 focus:outline-none"
              />

              {/* Quick Model Pills */}
              <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                <span className="text-[10px] text-slate-500">پیشنهادی:</span>
                {POPULAR_OPENROUTER_MODELS.map((slug) => (
                  <button
                    key={slug}
                    type="button"
                    onClick={() => setOpenrouterModel(slug)}
                    className={`px-2 py-0.5 rounded-md text-[10px] font-mono transition-all ${
                      openrouterModel === slug
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {slug}
                  </button>
                ))}
              </div>

              {/* Toggle Searchable Dropdown if models are loaded */}
              {availableOpenrouterModels.length > 0 && (
                <div className="pt-1">
                  <button
                    type="button"
                    onClick={() => setShowOpenrouterDropdown(!showOpenrouterDropdown)}
                    className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300"
                  >
                    {showOpenrouterDropdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    <span>
                      {showOpenrouterDropdown ? 'بستن منوی جستجوی مدل‌ها' : `مشاهده و جستجو در لیست مدل‌های زنده (${availableOpenrouterModels.length} مدل دریافت شد)`}
                    </span>
                  </button>
                </div>
              )}

              {/* SEARCHABLE LIVE MODEL DROPDOWN */}
              {showOpenrouterDropdown && availableOpenrouterModels.length > 0 && (
                <div className="p-3 rounded-xl bg-slate-900 border border-emerald-500/40 space-y-2 shadow-xl">
                  {/* Search Filter Input */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-2.5" />
                    <input
                      type="text"
                      value={openrouterSearchQuery}
                      onChange={(e) => setOpenrouterSearchQuery(e.target.value)}
                      placeholder="فیلتر مدل‌ها (نام یا اسلاگ، مثلاً deepseek, gemini, claude, qwen)..."
                      className="w-full pr-8 pl-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs focus:border-emerald-500 focus:outline-none"
                    />
                  </div>

                  {/* Results Count & Model List */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400 px-1">
                    <span>نتایج مطابق: {filteredOpenrouterModels.length} مدل</span>
                    <span className="font-mono">برای انتخاب روی مدل کلیک کنید</span>
                  </div>

                  <div className="max-h-52 overflow-y-auto space-y-1 pr-1">
                    {filteredOpenrouterModels.length === 0 ? (
                      <div className="text-center py-4 text-slate-500 text-xs">
                        مدلی با این عبارت پیدا نشد.
                      </div>
                    ) : (
                      filteredOpenrouterModels.map((m) => {
                        const isSelected = openrouterModel === m.id;
                        return (
                          <div
                            key={m.id}
                            onClick={() => {
                              setOpenrouterModel(m.id);
                              setShowOpenrouterDropdown(false);
                            }}
                            className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all ${
                              isSelected
                                ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-200'
                                : 'hover:bg-slate-800 text-slate-300'
                            }`}
                          >
                            <div className="space-y-0.5 truncate pr-2">
                              <div className="text-xs font-bold text-slate-200 truncate">
                                {m.name}
                              </div>
                              <div className="text-[10px] font-mono text-emerald-400 truncate ltr-content">
                                {m.id}
                              </div>
                            </div>

                            <div className="flex items-center gap-2 flex-shrink-0">
                              {m.context_length && (
                                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                                  {Math.round(m.context_length / 1024)}k
                                </span>
                              )}
                              {isSelected && (
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                              )}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}

              {openrouterModelsError && (
                <div className="text-[11px] text-rose-400 bg-rose-950/40 p-2 rounded-lg border border-rose-800/40">
                  {openrouterModelsError}
                </div>
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium"
            >
              بستن
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`flex items-center gap-2 px-7 py-2.5 rounded-xl font-bold transition-all ${
                savedSuccess
                  ? 'bg-emerald-500 text-slate-950'
                  : 'bg-gradient-to-r from-amber-500 to-emerald-500 hover:from-amber-400 hover:to-emerald-400 text-slate-950 shadow-md shadow-amber-500/20'
              }`}
            >
              {savedSuccess ? (
                <>
                  <Check className="w-4 h-4" />
                  تنظیمات ذخیره شد!
                </>
              ) : (
                'ذخیره همه تنظیمات'
              )}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
