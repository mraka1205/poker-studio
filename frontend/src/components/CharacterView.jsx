import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Sparkles, 
  Copy, 
  Check, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  ExternalLink,
  Camera,
  Layers,
  RefreshCw,
  UserCheck
} from 'lucide-react';
import AiStudioBridge from './AiStudioBridge';
import { uploadAsset, fetchUniverse, syncUniverseCharacters, updateCharacterSeat } from '../api';

export default function CharacterView({
  characters = [],
  episodeId,
  stageStatus,
  onApproveStage,
  onUpdateCharacterStatus,
  onCharacterUpdated,
  onRefresh
}) {
  const [copiedPromptId, setCopiedPromptId] = useState(null);
  const [uploadingId, setUploadingId] = useState(null);
  const [universeChars, setUniverseChars] = useState([]);
  const [selectedUniverseIds, setSelectedUniverseIds] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState('');

  const handleSeatChange = async (charId, newSeat) => {
    try {
      await updateCharacterSeat(episodeId, charId, newSeat);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert('خطا در تنظیم صندلی کاراکتر: ' + err.message);
    }
  };

  useEffect(() => {
    loadUniverseData();
  }, [episodeId]);

  useEffect(() => {
    // Auto-select characters that are already in the episode
    if (universeChars.length > 0 && characters) {
      const epCharIds = new Set(characters.map(c => c.id));
      const epFlowTags = new Set(characters.map(c => c.flow_tag || `@${c.name_en}`));
      
      const preselected = universeChars
        .filter(uc => epCharIds.has(uc.id) || epFlowTags.has(uc.flow_tag))
        .map(uc => uc.id);
      
      // If none matched (e.g. new episode), default to all universe characters
      setSelectedUniverseIds(preselected.length > 0 ? preselected : universeChars.map(uc => uc.id));
    }
  }, [universeChars, characters]);

  const loadUniverseData = async () => {
    try {
      const data = await fetchUniverse();
      setUniverseChars(data.characters || []);
    } catch (err) {
      console.error('Error fetching universe characters:', err);
    }
  };

  const toggleSelectChar = (id) => {
    setSelectedUniverseIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleSyncSelected = async () => {
    if (selectedUniverseIds.length === 0) {
      alert('لطفاً حداقل یک کاراکتر را برای حضور بر سر میز انتخاب کنید.');
      return;
    }
    setSyncing(true);
    setSyncSuccessMsg('');
    try {
      const res = await syncUniverseCharacters(episodeId, selectedUniverseIds);
      setSyncSuccessMsg(res.message || 'کاراکترها با موفقیت همگام‌سازی شدند');
      if (onRefresh) onRefresh();
      setTimeout(() => setSyncSuccessMsg(''), 3000);
    } catch (err) {
      alert('خطا در همگام‌سازی کاراکترها: ' + err.message);
    } finally {
      setSyncing(false);
    }
  };

  const copyPrompt = (id, promptText) => {
    navigator.clipboard.writeText(promptText);
    setCopiedPromptId(id);
    setTimeout(() => setCopiedPromptId(null), 2000);
  };

  const handleFileUpload = async (charId, file) => {
    if (!file) return;
    setUploadingId(charId);
    try {
      const res = await uploadAsset(episodeId, 'characters', file);
      if (onCharacterUpdated) {
        onCharacterUpdated(charId, res.url);
      }
    } catch (err) {
      alert('خطا در آپلود فوتوشیت: ' + err.message);
    } finally {
      setUploadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* 1. AI Studio Bridge for Characters */}
      <AiStudioBridge
        episodeId={episodeId}
        stage="characters"
        stageTitle="مدل‌شیت و لنگر استایل کاراکترها"
        description="پرامپت مهارت ۰۳ را کپی کرده و در Gemini اجرا کنید تا پرامپت‌های مدل شیت چندزاویه‌ای کاراکترها (با ارجاع به Style Anchor) در قالب JSON تولید شود."
        onSuccess={() => {
          if (onRefresh) onRefresh();
          if (onApproveStage) onApproveStage();
        }}
      />

      {/* 2. Channel Universe Cast Selector (Roster Sync) */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-amber-500/30 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300 text-lg">
              🎭
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-black text-white">انتخاب از بانک کاراکترهای کانال (Channel Universe Cast)</h3>
                <span className="text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                  Google Flow @Ingredients
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-0.5">
                کاراکترهای حاضر بر سر میز این دست پوکر را انتخاب کرده و با یک کلیک به این اپیزود اضافه کنید:
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {syncSuccessMsg && (
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                <Check className="w-3.5 h-3.5" />
                {syncSuccessMsg}
              </span>
            )}
            <button
              onClick={handleSyncSelected}
              disabled={syncing || selectedUniverseIds.length === 0}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 text-xs font-black shadow-lg shadow-amber-500/20 transition-all hover:scale-105"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? 'در حال همگام‌سازی...' : 'همگام‌سازی کاراکترها با این اپیزود'}
            </button>
          </div>
        </div>

        {/* Universe Characters Quick Selector Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
          {universeChars.map((uc) => {
            const isSelected = selectedUniverseIds.includes(uc.id);
            const isAlreadyInEp = characters.some(c => c.id === uc.id || c.flow_tag === uc.flow_tag);

            return (
              <div
                key={uc.id}
                onClick={() => toggleSelectChar(uc.id)}
                className={`p-3 rounded-xl border cursor-pointer transition-all flex items-center gap-3 ${
                  isSelected
                    ? 'bg-amber-500/10 border-amber-500/50 ring-1 ring-amber-500/30 shadow-md'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 opacity-70'
                }`}
              >
                {/* Avatar / Turnaround Sheet Thumbnail */}
                <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-700 overflow-hidden flex-shrink-0 flex items-center justify-center">
                  {(uc.face_sheet_image_path || uc.body_sheet_image_path || uc.reference_image_path) ? (
                    <img
                      src={uc.face_sheet_image_path || uc.body_sheet_image_path || uc.reference_image_path}
                      alt={uc.name_fa}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-xl">👤</span>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white truncate">{uc.name_fa}</span>
                    <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-950 px-1.5 py-0.2 rounded border border-amber-800">
                      {uc.flow_tag}
                    </span>
                    <span className="text-[10px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 font-mono">
                      {uc.default_seat === 'seat_1' ? 'صندلی ۱' :
                       uc.default_seat === 'seat_2' ? 'صندلی ۲' :
                       uc.default_seat === 'seat_3' ? 'صندلی ۳' :
                       uc.default_seat === 'seat_4' ? 'صندلی ۴' :
                       uc.default_seat === 'seat_5' ? 'صندلی ۵' :
                       uc.default_seat === 'seat_6' ? 'صندلی ۶' : (uc.default_seat || 'صندلی ۱')}
                    </span>
                    {uc.is_style_anchor && (
                      <span className="text-[10px] text-amber-300" title="لنگر استایل">⭐</span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 truncate mt-0.5">{uc.archetype}</div>
                </div>

                {/* Checkbox badge */}
                <div className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold transition-all ${
                  isSelected
                    ? 'bg-amber-500 text-slate-950 shadow-sm'
                    : 'border border-slate-700 text-transparent'
                }`}>
                  ✓
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۴: کاراکترها و لنگر استایل (Character Anchors)
            </span>
            <span className="text-xs text-slate-400">
              یکدستی بصری (Visual Consistency) با مدل شیت و توکن‌های تصویری قفل‌شده
            </span>
          </div>
          <h2 className="text-xl font-black text-white">تیپ‌های شخصیتی و کاراکتر لنگر (Style Anchor)</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            برای تولید تصاویر صحنه‌ها در Midjourney یا Flux، از کاراکتر لنگر به عنوان رفرنس استایل استفاده می‌شود.
          </p>
        </div>

        {stageStatus === 'approved' ? (
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            کاراکترها تایید شدند ✓
          </div>
        ) : (
          <button
            onClick={onApproveStage}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-black shadow-lg shadow-purple-600/20 transition-all hover:scale-105"
          >
            <Check className="w-4 h-4" />
            تایید کلی کاراکترها (Approve Stage)
          </button>
        )}
      </div>

      {/* Style Consistency Callout Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-300 text-lg">
            ⭐
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">قانون لنگر استایل (Root Style Anchor)</h4>
            <p className="text-xs text-slate-300">
              کاراکتر <strong className="text-amber-400">{characters.find(c => c.is_style_anchor)?.name_fa || 'آرش (@Arash)'}</strong> به عنوان لنگر گرافیکی تعریف شده و همه صحنه‌ها از پالت و آرت ۲ بعدی او الهام می‌گیرند.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-indigo-300 bg-indigo-950 px-3 py-1.5 rounded-lg border border-indigo-800">
            Midjourney: --cref [Anchor_URL] --cw 80
          </span>
        </div>
      </div>

      {/* Character Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {characters.map((char) => {
          const isAnchor = char.is_style_anchor;
          const isApproved = char.status === 'approved';

          return (
            <div
              key={char.id}
              className={`rounded-2xl border transition-all flex flex-col justify-between overflow-hidden ${
                isAnchor
                  ? 'bg-slate-900/90 border-amber-500/40 ring-1 ring-amber-500/20 shadow-xl shadow-amber-500/5'
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              
              {/* Card Header & Badges */}
              <div className="p-5 pb-3 space-y-3">
                <div className="flex items-center justify-between">
                  {isAnchor ? (
                    <span className="flex items-center gap-1 text-[11px] font-black px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 shadow-md">
                      ⭐ لنگر استایل (Style Anchor)
                    </span>
                  ) : (
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                      {char.role}
                    </span>
                  )}

                  {/* Status toggle */}
                  <button
                    onClick={() => onUpdateCharacterStatus(char.id, isApproved ? 'waiting_approval' : 'approved')}
                    className={`flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg transition-all ${
                      isApproved
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                        : 'bg-amber-500/10 text-amber-300 border border-amber-500/30 hover:bg-amber-500/20'
                    }`}
                  >
                    {isApproved ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        تایید شده
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        نیاز به تایید
                      </>
                    )}
                  </button>
                </div>

                {/* Name & Tagline */}
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-black text-white">{char.name_fa}</h3>
                    {char.flow_tag && (
                      <span className="text-[11px] font-mono font-bold text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded-lg border border-amber-800">
                        {char.flow_tag}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 font-mono ltr-content">{char.name_en}</div>
                  {char.tagline && (
                    <p className="text-xs text-amber-300/90 mt-1 italic font-medium">
                      «{char.tagline}»
                    </p>
                  )}
                </div>

                {/* 6-Max Table Seat Selector */}
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <span>🪑</span>
                    صندلی میز ۶ نفره:
                  </label>
                  <select
                    value={char.assigned_seat || char.default_seat || 'seat_1'}
                    onChange={(e) => handleSeatChange(char.id, e.target.value)}
                    className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs font-bold text-amber-300 focus:outline-none focus:border-amber-500 cursor-pointer"
                  >
                    <option value="seat_1">صندلی ۱ (@Seat_1 - قفسه کتاب)</option>
                    <option value="seat_2">صندلی ۲ (@Seat_2 - قاب هنری)</option>
                    <option value="seat_3">صندلی ۳ (@Seat_3 - پرده ضخیم)</option>
                    <option value="seat_4">صندلی ۴ (@Seat_4 - تخته‌نرد و گیاه)</option>
                    <option value="seat_5">صندلی ۵ (@Seat_5 - چای ایرانی و پسته)</option>
                    <option value="seat_6">صندلی ۶ (@Seat_6 - عمق اتاق و نئون)</option>
                  </select>
                </div>

                {/* Image / Turnaround Sheet Viewport */}
                <div className="relative aspect-square rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center group">
                  <img
                    src={char.face_sheet_image_path || char.body_sheet_image_path || char.turnaround_sheet || char.avatar_url}
                    alt={char.name_fa}
                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                  />

                  {/* Overlay Upload Button */}
                  <label className="absolute inset-0 bg-slate-950/70 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 cursor-pointer p-4 text-center">
                    <Camera className="w-6 h-6 text-amber-400" />
                    <span className="text-xs font-bold text-white">آپلود فوتوشیت جدید</span>
                    <span className="text-[10px] text-slate-300">فرمت PNG یا JPG استاپ‌موشن ۹:۱۶</span>
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => handleFileUpload(char.id, e.target.files?.[0])}
                    />
                  </label>

                  {uploadingId === char.id && (
                    <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center text-xs font-bold text-amber-400">
                      در حال آپلود...
                    </div>
                  )}
                </div>
              </div>

              {/* Locked Prompts & Footer */}
              <div className="p-5 pt-0 space-y-3">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 font-medium">پرامپت‌های استاپ‌موشن:</span>
                    <div className="flex items-center gap-1.5">
                      {char.face_expressions_prompt_en && (
                        <button
                          onClick={() => copyPrompt(`${char.id}_face`, char.face_expressions_prompt_en)}
                          className="flex items-center gap-1 text-[10px] font-bold text-amber-400 hover:text-amber-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800"
                          title="کپی پرامپت شیت صورت"
                        >
                          {copiedPromptId === `${char.id}_face` ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
                          شیت صورت
                        </button>
                      )}
                      <button
                        onClick={() => copyPrompt(char.id, char.full_body_prompt_en || char.style_prompt || char.character_sheet_prompt_en)}
                        className="flex items-center gap-1 text-[10px] font-bold text-amber-400 hover:text-amber-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800"
                        title="کپی پرامپت شیت تمام‌قد"
                      >
                        {copiedPromptId === char.id ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
                        شیت تمام‌قد
                      </button>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300 ltr-content leading-relaxed max-h-24 overflow-y-auto">
                    {char.full_body_prompt_en || char.style_prompt || char.character_sheet_prompt_en}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[11px] text-slate-400">
                  <span>شناسه صدا: <span className="font-mono text-slate-300">{char.voice_id}</span></span>
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
