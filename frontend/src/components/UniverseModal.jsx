import React, { useState, useEffect } from 'react';
import { 
  X, 
  Sparkles, 
  Globe, 
  Users, 
  Copy, 
  Check, 
  Upload, 
  Plus, 
  Trash2, 
  Save, 
  AlertCircle, 
  Camera,
  Layers,
  CheckCircle2
} from 'lucide-react';
import { fetchUniverse, saveUniverse, uploadUniverseAsset, generateCharacterPrompts } from '../api';

export default function UniverseModal({ isOpen, onClose, onUniverseUpdated }) {
  const [activeTab, setActiveTab] = useState('environment'); // 'environment' or 'characters'
  const [universe, setUniverse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [uploadingTarget, setUploadingTarget] = useState(null); // 'env' or `${charId}_face` or `${charId}_body` or `angle_${angleId}`
  const [generatingCharId, setGeneratingCharId] = useState(null);
  const [conceptInputs, setConceptInputs] = useState({});
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchUniverse();
      setUniverse(data);
    } catch (err) {
      alert('خطا در دریافت اطلاعات دنیای کانال: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const copyText = (id, text) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSave = async () => {
    if (!universe) return;
    setSaving(true);
    setSaveSuccess(false);
    try {
      await saveUniverse(universe);
      setSaveSuccess(true);
      if (onUniverseUpdated) onUniverseUpdated(universe);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      alert('خطا در ذخیره تغییرات دنیای کانال: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleUploadEnvImage = async (file) => {
    if (!file) return;
    setUploadingTarget('env');
    try {
      const res = await uploadUniverseAsset('environment', file);
      setUniverse(prev => ({
        ...prev,
        environment: {
          ...prev.environment,
          reference_image_path: res.url
        }
      }));
    } catch (err) {
      alert('خطا در آپلود عکس میز و محیط: ' + err.message);
    } finally {
      setUploadingTarget(null);
    }
  };

  const handleUploadCharSheet = async (charId, file, sheetType) => {
    if (!file) return;
    setUploadingTarget(`${charId}_${sheetType}`);
    try {
      const res = await uploadUniverseAsset('character', file, charId, null, sheetType);
      setUniverse(prev => ({
        ...prev,
        characters: prev.characters.map(c => {
          if (c.id !== charId) return c;
          if (sheetType === 'face') {
            return {
              ...c,
              face_sheet_image_path: res.url,
              reference_image_path: c.reference_image_path || res.url
            };
          } else {
            return {
              ...c,
              body_sheet_image_path: res.url,
              reference_image_path: res.url
            };
          }
        })
      }));
    } catch (err) {
      alert('خطا در آپلود شیت کاراکتر: ' + err.message);
    } finally {
      setUploadingTarget(null);
    }
  };

  const handleAiGeneratePrompts = async (charId) => {
    const targetChar = universe?.characters?.find(c => c.id === charId);
    if (!targetChar) return;
    const concept = conceptInputs[charId] || targetChar.persona_behavior_prompt || targetChar.personality_and_catchphrases_fa || '';
    setGeneratingCharId(charId);
    try {
      const res = await generateCharacterPrompts(charId, {
        concept_fa: concept,
        name_fa: targetChar.name_fa,
        archetype: targetChar.archetype,
        flow_tag: targetChar.flow_tag
      });
      setUniverse(prev => ({
        ...prev,
        characters: prev.characters.map(c => 
          c.id === charId ? {
            ...c,
            face_expressions_prompt_en: res.face_expressions_prompt_en,
            full_body_prompt_en: res.full_body_prompt_en,
            persona_behavior_prompt: res.persona_behavior_prompt,
            visual_prompt_en: res.full_body_prompt_en,
            personality_and_catchphrases_fa: res.persona_behavior_prompt
          } : c
        )
      }));
    } catch (err) {
      alert('خطا در تولید ۳ پرامپت با هوش مصنوعی: ' + err.message);
    } finally {
      setGeneratingCharId(null);
    }
  };

  const handleAddCharacter = () => {
    const newIdx = (universe?.characters?.length || 0) + 1;
    const newChar = {
      id: `char_${Date.now()}`,
      name_fa: `کاراکتر جدید ${newIdx}`,
      flow_tag: `@Char${newIdx}`,
      archetype: 'Poker Player',
      default_seat: 'seat_1',
      face_expressions_prompt_en: 'Needle-felted wool stop-motion character head and facial expression sheet... solid neutral light-gray studio background, vertical 9:16 composition --ar 9:16 --v 6.1',
      full_body_prompt_en: 'Full-body character turnaround sheet of needle-felted stop-motion miniature puppet from head to toe... solid flat neutral light-gray studio background, vertical 9:16 composition --ar 9:16 --v 6.1',
      persona_behavior_prompt: 'پروفایل شخصیتی، تکیه‌کلام‌ها و زبان بدن فیزیکی کاراکتر برای بازیگری بی‌صدا در استاپ‌موشن...',
      personality_and_catchphrases_fa: 'پروفایل شخصیتی و تکیه‌کلام‌های کاراکتر...',
      visual_prompt_en: 'Full-body character turnaround sheet of needle-felted stop-motion miniature puppet... vertical 9:16 composition --ar 9:16 --v 6.1',
      reference_image_path: '',
      face_sheet_image_path: '',
      body_sheet_image_path: '',
      is_style_anchor: false
    };
    setUniverse(prev => ({
      ...prev,
      characters: [...(prev.characters || []), newChar]
    }));
  };

  const handleDeleteCharacter = (charId) => {
    if (!window.confirm('آیا از حذف این کاراکتر از دنیای ثابت کانال اطمینان دارید؟')) return;
    setUniverse(prev => ({
      ...prev,
      characters: prev.characters.filter(c => c.id !== charId)
    }));
  };

  const handleSetStyleAnchor = (charId) => {
    setUniverse(prev => ({
      ...prev,
      characters: prev.characters.map(c => ({
        ...c,
        is_style_anchor: c.id === charId
      }))
    }));
  };

  const handleUploadAngleImage = async (angleId, file) => {
    if (!file) return;
    setUploadingTarget(`angle_${angleId}`);
    try {
      const res = await uploadUniverseAsset('camera_angle', file, null, angleId);
      setUniverse(prev => ({
        ...prev,
        environment: {
          ...prev.environment,
          camera_angles: (prev.environment.camera_angles || []).map(a => 
            a.id === angleId ? { ...a, reference_image_path: res.url } : a
          )
        }
      }));
    } catch (err) {
      alert('خطا در آپلود عکس زاویه دوربین: ' + err.message);
    } finally {
      setUploadingTarget(null);
    }
  };

  const updateAngleField = (angleId, field, value) => {
    setUniverse(prev => ({
      ...prev,
      environment: {
        ...prev.environment,
        camera_angles: (prev.environment.camera_angles || []).map(a => 
          a.id === angleId ? { ...a, [field]: value } : a
        )
      }
    }));
  };

  const updateEnvField = (field, value) => {
    setUniverse(prev => ({
      ...prev,
      environment: {
        ...prev.environment,
        [field]: value
      }
    }));
  };

  const updateCharField = (charId, field, value) => {
    setUniverse(prev => ({
      ...prev,
      characters: prev.characters.map(c => 
        c.id === charId ? { ...c, [field]: value } : c
      )
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="bg-[#0e1424] border border-slate-700 w-full max-w-5xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        
        {/* Header */}
        <div className="p-5 px-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center text-white text-xl shadow-lg shadow-amber-500/10">
              🎭
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-black text-white">دنیای ثابت کانال (Channel Universe)</h2>
                <span className="text-[11px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                  Google Flow @Ingredients
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                محیط میز همیشگی و بانک بازیگران ثابت با هویت تصویری و کمدی پیوسته برای تمام اپیزودها
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pt-3 border-b border-slate-800/80 bg-slate-900/30 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('environment')}
              className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-xs font-bold transition-all ${
                activeTab === 'environment'
                  ? 'border-amber-400 text-amber-300 bg-amber-500/10 rounded-t-xl'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Globe className="w-4 h-4" />
              میز و محیط ثابت (<span className="font-mono text-amber-400">@PokerRoom</span>)
            </button>

            <button
              onClick={() => setActiveTab('characters')}
              className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-xs font-bold transition-all ${
                activeTab === 'characters'
                  ? 'border-amber-400 text-amber-300 bg-amber-500/10 rounded-t-xl'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Users className="w-4 h-4" />
              بانک کاراکترهای ثابت کانال ({universe?.characters?.length || 0})
            </button>
          </div>

          <div className="text-[11px] font-mono text-slate-400 hidden sm:block">
            projects/universe.json
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-20 text-center text-xs text-slate-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping inline-block ml-2" />
              در حال بارگذاری اطلاعات دنیای کانال...
            </div>
          ) : (
            <>
              {/* TAB 1: ENVIRONMENT & STYLE */}
              {activeTab === 'environment' && (
                <div className="space-y-6">
                  
                  {/* Top info badge */}
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-indigo-500/10 to-slate-900 border border-amber-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300 font-mono font-bold text-sm">
                        @PR
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-white flex items-center gap-2">
                          تگ اختصاصی گوگل فلو:
                          <span className="font-mono text-amber-300 font-black text-sm bg-amber-950/80 px-2 py-0.5 rounded-lg border border-amber-800">
                            {universe?.environment?.flow_tag || '@PokerRoom'}
                          </span>
                        </h4>
                        <p className="text-xs text-slate-300 mt-0.5">
                          تمامی پرامپت‌های استوری‌بورد و حرکتی به طور خودکار این تگ را به عنوان بستر ثابت اتاق پوکر فراخوانی می‌کنند.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left/Main Form Fields (8 cols) */}
                    <div className="lg:col-span-8 space-y-4">
                      
                      <div>
                        <label className="block text-xs font-bold text-slate-300 mb-1.5">
                          عنوان محیط / اتاق پوکر:
                        </label>
                        <input
                          type="text"
                          value={universe?.environment?.name || ''}
                          onChange={(e) => updateEnvField('name', e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-slate-300 mb-1.5">
                          شرح داستان و جزئیات محیطی (فارسی):
                        </label>
                        <textarea
                          rows={3}
                          value={universe?.environment?.description_fa || ''}
                          onChange={(e) => updateEnvField('description_fa', e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 leading-relaxed"
                          placeholder="توصیف اتاق، نورپردازی، جزئیات میز..."
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-slate-300 mb-1.5">
                          استایل بصری یکپارچه کانال (English Style Note):
                        </label>
                        <textarea
                          rows={2}
                          value={universe?.environment?.style_note_en || ''}
                          onChange={(e) => updateEnvField('style_note_en', e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono ltr-content focus:outline-none focus:border-amber-500 leading-relaxed"
                        />
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <label className="text-xs font-bold text-slate-300">
                            پرامپت انگلیسی فریم کلیدی میز ثابت (Master Reference Prompt - 9:16):
                          </label>
                          <button
                            type="button"
                            onClick={() => copyText('env_prompt', universe?.environment?.visual_prompt_en)}
                            className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                          >
                            {copiedId === 'env_prompt' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                            {copiedId === 'env_prompt' ? 'کپی شد!' : 'کپی پرامپت'}
                          </button>
                        </div>
                        <textarea
                          rows={5}
                          value={universe?.environment?.visual_prompt_en || ''}
                          onChange={(e) => updateEnvField('visual_prompt_en', e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono ltr-content focus:outline-none focus:border-amber-500 leading-relaxed"
                        />
                      </div>

                    </div>

                    {/* Right: Master Reference Image (4 cols) */}
                    <div className="lg:col-span-4 space-y-3">
                      <label className="block text-xs font-bold text-slate-300">
                        فریم کلیدی مرجع میز ثابت (@PokerRoom):
                      </label>

                      <div className="relative aspect-[9/16] max-h-[380px] mx-auto rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col items-center justify-center group shadow-xl">
                        {universe?.environment?.reference_image_path ? (
                          <img
                            src={universe.environment.reference_image_path}
                            alt="Master Poker Room"
                            className="w-full h-full object-cover transition-transform group-hover:scale-105"
                          />
                        ) : (
                          <div className="p-6 text-center space-y-2">
                            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500 text-xl">
                              🎴
                            </div>
                            <p className="text-xs font-bold text-slate-300">هنوز تصویری آپلود نشده</p>
                            <p className="text-[11px] text-slate-500">
                              پرامپت را در Midjourney / Flux تولید کنید و تصویر فریم اصلی را اینجا آپلود نمایید.
                            </p>
                          </div>
                        )}

                        {/* Upload Overlay */}
                        <label className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 cursor-pointer p-4 text-center">
                          <Camera className="w-6 h-6 text-amber-400" />
                          <span className="text-xs font-bold text-white">آپلود فریم اصلی میز</span>
                          <span className="text-[10px] text-slate-300">فرمت JPG یا PNG کادربندی عمودی ۹:۱۶</span>
                          <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => handleUploadEnvImage(e.target.files?.[0])}
                          />
                        </label>

                        {uploadingTarget === 'env' && (
                          <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-xs font-bold text-amber-400">
                            در حال آپلود تصویر...
                          </div>
                        )}
                      </div>

                      {universe?.environment?.reference_image_path && (
                        <div className="text-[11px] font-mono text-slate-400 text-center truncate">
                          {universe.environment.reference_image_path}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 6-Max Poker Table Camera Angles Grid */}
                  <div className="pt-6 border-t border-slate-800 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-black text-white">زوایای دوربین و لندمارک‌های میز ۶ نفره (6-Max Camera Angles)</h3>
                          <span className="text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                            تداوم فضایی ۳ بعدی
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">
                          برای جلوگیری از بک‌گراند تخت، ۶ زاویه صندلی با لندمارک‌های اختصاصی و ۳ زاویه سینمایی تعریف شده است.
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {(universe?.environment?.camera_angles || []).map((ang) => {
                        const isSeat = ang.id.startsWith('seat_');
                        const isUploading = uploadingTarget === `angle_${ang.id}`;

                        return (
                          <div
                            key={ang.id}
                            className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 flex flex-col justify-between space-y-3 transition-all"
                          >
                            <div className="space-y-2">
                              {/* Top tag & label */}
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <span className={`text-[11px] font-mono font-black px-2 py-0.5 rounded-lg border ${
                                    isSeat 
                                      ? 'bg-amber-950/80 text-amber-300 border-amber-700/60'
                                      : 'bg-indigo-950/80 text-indigo-300 border-indigo-700/60'
                                  }`}>
                                    {ang.flow_tag}
                                  </span>
                                  <span className="text-xs font-bold text-white">{ang.label_fa}</span>
                                </div>

                                <button
                                  type="button"
                                  onClick={() => copyText(`ang_${ang.id}`, ang.visual_prompt_en)}
                                  className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                                  title="کپی پرامپت"
                                >
                                  {copiedId === `ang_${ang.id}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                  {copiedId === `ang_${ang.id}` ? 'کپی شد!' : 'کپی'}
                                </button>
                              </div>

                              {/* Background landmarks summary */}
                              <div className="text-[11px] text-slate-300 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 leading-relaxed">
                                <span className="font-bold text-slate-400 block mb-0.5">لندمارک اختصاصی پس‌زمینه:</span>
                                {ang.background_landmarks_en}
                              </div>

                              {/* 9:16 Preview / Upload Slot */}
                              <div className="relative aspect-[9/16] max-h-[220px] mx-auto rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col items-center justify-center group shadow-md w-full">
                                {ang.reference_image_path ? (
                                  <img
                                    src={ang.reference_image_path}
                                    alt={ang.label_fa}
                                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                                  />
                                ) : (
                                  <div className="p-3 text-center space-y-1">
                                    <span className="text-2xl block text-slate-500">🎬</span>
                                    <span className="text-[10px] text-slate-400 font-bold block">بدون فریم مرجع</span>
                                    <span className="text-[9px] text-slate-600 block">جهت آپلود کلیک کنید</span>
                                  </div>
                                )}

                                <label className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1 cursor-pointer p-2 text-center">
                                  <Camera className="w-5 h-5 text-amber-400" />
                                  <span className="text-[10px] font-bold text-white">آپلود فریم زاویه</span>
                                  <span className="text-[9px] text-slate-300">عمودی ۹:۱۶</span>
                                  <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={(e) => handleUploadAngleImage(ang.id, e.target.files?.[0])}
                                  />
                                </label>

                                {isUploading && (
                                  <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-[11px] font-bold text-amber-400">
                                    در حال آپلود...
                                  </div>
                                )}
                              </div>

                              {/* Prompt text editable */}
                              <div>
                                <textarea
                                  rows={3}
                                  value={ang.visual_prompt_en || ''}
                                  onChange={(e) => updateAngleField(ang.id, 'visual_prompt_en', e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-[10px] text-slate-300 font-mono ltr-content focus:outline-none focus:border-amber-500 leading-relaxed"
                                  placeholder="Visual prompt for this camera angle..."
                                />
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                </div>
              )}

              {/* TAB 2: RECURRING CHARACTERS */}
              {activeTab === 'characters' && (
                <div className="space-y-6">
                  
                  {/* Top Action Bar */}
                  <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
                    <div>
                      <h3 className="text-xs font-bold text-white">بازیگران ثابت کانال ({universe?.characters?.length || 0} کاراکتر)</h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        این کاراکترها در تمام فیلم‌نامه‌ها، صحنه‌ها و پرامپت‌های ویدیویی Google Flow با تگ ثابت صدا زده می‌شوند.
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={handleAddCharacter}
                      className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-black shadow-md transition-all"
                    >
                      <Plus className="w-4 h-4" />
                      افزودن کاراکتر ثابت جدید
                    </button>
                  </div>

                  {/* Character Cards */}
                  <div className="space-y-6">
                    {(universe?.characters || []).map((char, idx) => {
                      const isAnchor = char.is_style_anchor;
                      const isGeneratingThis = generatingCharId === char.id;
                      const isUploadingFace = uploadingTarget === `${char.id}_face`;
                      const isUploadingBody = uploadingTarget === `${char.id}_body`;
                      
                      return (
                        <div
                          key={char.id}
                          className={`p-5 rounded-3xl border transition-all space-y-4 ${
                            isAnchor
                              ? 'bg-slate-900/90 border-amber-500/40 ring-1 ring-amber-500/20 shadow-xl'
                              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                          }`}
                        >
                          {/* 1. Header Row: Name, Flow Tag, Archetype, Default Seat, Actions */}
                          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 flex-1">
                              <div>
                                <label className="block text-[11px] font-bold text-slate-300 mb-1">نام فارسی:</label>
                                <input
                                  type="text"
                                  value={char.name_fa || ''}
                                  onChange={(e) => updateCharField(char.id, 'name_fa', e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500 font-bold"
                                />
                              </div>

                              <div>
                                <label className="block text-[11px] font-bold text-slate-300 mb-1">
                                  تگ گوگل فلو (<span className="text-amber-400 font-mono">@Tag</span>):
                                </label>
                                <input
                                  type="text"
                                  value={char.flow_tag || ''}
                                  onChange={(e) => updateCharField(char.id, 'flow_tag', e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-amber-400 font-mono focus:outline-none focus:border-amber-500 font-bold ltr-content"
                                />
                              </div>

                              <div>
                                <label className="block text-[11px] font-bold text-slate-300 mb-1">تیپ و نقش (Archetype):</label>
                                <input
                                  type="text"
                                  value={char.archetype || ''}
                                  onChange={(e) => updateCharField(char.id, 'archetype', e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-amber-500"
                                />
                              </div>

                              <div>
                                <label className="block text-[11px] font-bold text-slate-300 mb-1">صندلی پیش‌فرض میز ۶ نفره:</label>
                                <select
                                  value={char.default_seat || 'seat_1'}
                                  onChange={(e) => updateCharField(char.id, 'default_seat', e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-amber-300 focus:outline-none focus:border-amber-500 font-bold"
                                >
                                  <option value="seat_1">صندلی ۱ (قفسه کتاب)</option>
                                  <option value="seat_2">صندلی ۲ (قاب هنری)</option>
                                  <option value="seat_3">صندلی ۳ (پرده ضخیم)</option>
                                  <option value="seat_4">صندلی ۴ (تخته‌نرد و گیاه)</option>
                                  <option value="seat_5">صندلی ۵ (چای ایرانی و پسته)</option>
                                  <option value="seat_6">صندلی ۶ (عمق اتاق)</option>
                                </select>
                              </div>
                            </div>

                            <div className="flex items-center gap-2 self-end lg:self-center pt-2 lg:pt-0">
                              <button
                                type="button"
                                onClick={() => handleSetStyleAnchor(char.id)}
                                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                                  isAnchor
                                    ? 'bg-amber-500 text-slate-950 shadow-md font-black'
                                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                                }`}
                                title="تعیین به عنوان کاراکتر لنگر استایل استاپ‌موشن"
                              >
                                <span>⭐</span>
                                {isAnchor ? 'لنگر استایل' : 'انتخاب به عنوان لنگر'}
                              </button>

                              {universe.characters.length > 1 && (
                                <button
                                  type="button"
                                  onClick={() => handleDeleteCharacter(char.id)}
                                  className="p-1.5 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                                  title="حذف کاراکتر"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </div>

                          {/* 2. AI Generator Quick-Bar (تولید خودکار ۳ پرامپت با هوش مصنوعی) */}
                          <div className="p-3 rounded-2xl bg-gradient-to-r from-amber-500/10 via-indigo-500/10 to-slate-950 border border-amber-500/20 flex flex-col sm:flex-row items-center gap-3">
                            <div className="flex items-center gap-2 text-amber-300 font-bold text-xs whitespace-nowrap">
                              <Sparkles className="w-4 h-4 text-amber-400" />
                              تولید ۳ پرامپت استاپ‌موشن با AI:
                            </div>

                            <input
                              type="text"
                              value={conceptInputs[char.id] ?? ''}
                              onChange={(e) => setConceptInputs(prev => ({ ...prev, [char.id]: e.target.value }))}
                              placeholder="ایده یا خلاصه تیپ کاراکتر را اینجا بنویسید (مثلاً: جوان ۲۵ ساله تریدر عصبی و متکبر)..."
                              className="flex-1 w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                            />

                            <button
                              type="button"
                              onClick={() => handleAiGeneratePrompts(char.id)}
                              disabled={isGeneratingThis}
                              className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-xs shadow-md transition-all disabled:opacity-50 whitespace-nowrap flex items-center gap-1.5"
                            >
                              <Sparkles className={`w-3.5 h-3.5 ${isGeneratingThis ? 'animate-spin' : ''}`} />
                              {isGeneratingThis ? 'در حال تولید...' : 'تولید خودکار ۳ پرامپت'}
                            </button>
                          </div>

                          {/* 3. Two-Column Visual Prompts & Upload Slots */}
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            
                            {/* Column A: Prompt 1 - Face & Expressions Sheet */}
                            <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                                  <span>🎭</span>
                                  پرامپت ۱: شیت صورت و میمیک‌های چهره (9:16)
                                </span>
                                <button
                                  type="button"
                                  onClick={() => copyText(`${char.id}_face`, char.face_expressions_prompt_en)}
                                  className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                                >
                                  {copiedId === `${char.id}_face` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                  {copiedId === `${char.id}_face` ? 'کپی شد!' : 'کپی پرامپت'}
                                </button>
                              </div>

                              <textarea
                                rows={4}
                                value={char.face_expressions_prompt_en || ''}
                                onChange={(e) => updateCharField(char.id, 'face_expressions_prompt_en', e.target.value)}
                                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-[11px] text-slate-300 font-mono ltr-content focus:outline-none focus:border-amber-500 leading-relaxed"
                                placeholder="Face and 4 core expressions sheet prompt..."
                              />

                              {/* Upload Slot for Face Sheet */}
                              <div className="relative aspect-[9/16] max-h-[190px] mx-auto rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex flex-col items-center justify-center group shadow-md w-full">
                                {char.face_sheet_image_path ? (
                                  <img
                                    src={char.face_sheet_image_path}
                                    alt="Face Sheet"
                                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                                  />
                                ) : (
                                  <div className="p-3 text-center space-y-1">
                                    <span className="text-2xl block text-slate-500">🎭</span>
                                    <span className="text-[10px] text-slate-400 font-bold block">شیت صورت آپلود نشده</span>
                                    <span className="text-[9px] text-slate-600 block">کلیک جهت آپلود تصویر ۹:۱۶</span>
                                  </div>
                                )}

                                <label className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1 cursor-pointer p-2 text-center">
                                  <Camera className="w-5 h-5 text-amber-400" />
                                  <span className="text-[10px] font-bold text-white">آپلود فریم شیت صورت</span>
                                  <span className="text-[9px] text-slate-300">عمودی ۹:۱۶</span>
                                  <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={(e) => handleUploadCharSheet(char.id, e.target.files?.[0], 'face')}
                                  />
                                </label>

                                {isUploadingFace && (
                                  <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-[11px] font-bold text-amber-400">
                                    در حال آپلود...
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Column B: Prompt 2 - Full-Body Turnaround Sheet */}
                            <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                                  <span>🧍</span>
                                  پرامپت ۲: شیت تمام‌قد و لباس مینیاتوری (9:16)
                                </span>
                                <button
                                  type="button"
                                  onClick={() => copyText(`${char.id}_body`, char.full_body_prompt_en)}
                                  className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                                >
                                  {copiedId === `${char.id}_body` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                  {copiedId === `${char.id}_body` ? 'کپی شد!' : 'کپی پرامپت'}
                                </button>
                              </div>

                              <textarea
                                rows={4}
                                value={char.full_body_prompt_en || ''}
                                onChange={(e) => updateCharField(char.id, 'full_body_prompt_en', e.target.value)}
                                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-[11px] text-slate-300 font-mono ltr-content focus:outline-none focus:border-amber-500 leading-relaxed"
                                placeholder="Full-body puppet turnaround sheet prompt..."
                              />

                              {/* Upload Slot for Body Sheet */}
                              <div className="relative aspect-[9/16] max-h-[190px] mx-auto rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex flex-col items-center justify-center group shadow-md w-full">
                                {(char.body_sheet_image_path || char.reference_image_path) ? (
                                  <img
                                    src={char.body_sheet_image_path || char.reference_image_path}
                                    alt="Body Sheet"
                                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                                  />
                                ) : (
                                  <div className="p-3 text-center space-y-1">
                                    <span className="text-2xl block text-slate-500">🧍</span>
                                    <span className="text-[10px] text-slate-400 font-bold block">شیت تمام‌قد آپلود نشده</span>
                                    <span className="text-[9px] text-slate-600 block">کلیک جهت آپلود تصویر ۹:۱۶</span>
                                  </div>
                                )}

                                <label className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1 cursor-pointer p-2 text-center">
                                  <Camera className="w-5 h-5 text-amber-400" />
                                  <span className="text-[10px] font-bold text-white">آپلود فریم شیت تمام‌قد</span>
                                  <span className="text-[9px] text-slate-300">عمودی ۹:۱۶</span>
                                  <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={(e) => handleUploadCharSheet(char.id, e.target.files?.[0], 'body')}
                                  />
                                </label>

                                {isUploadingBody && (
                                  <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-[11px] font-bold text-amber-400">
                                    در حال آپلود...
                                  </div>
                                )}
                              </div>
                            </div>

                          </div>

                          {/* 4. Prompt 3: Persona, Catchphrases & Physical Behavior */}
                          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                                <span>🧠</span>
                                پرامپت ۳: شخصیت، نحوه صحبت و زبان بدن فیزیکی (Silent Acting Persona)
                              </span>
                              <button
                                type="button"
                                onClick={() => copyText(`${char.id}_persona`, char.persona_behavior_prompt)}
                                className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                              >
                                {copiedId === `${char.id}_persona` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                {copiedId === `${char.id}_persona` ? 'کپی شد!' : 'کپی پروفایل'}
                              </button>
                            </div>

                            <textarea
                              rows={3}
                              value={char.persona_behavior_prompt || char.personality_and_catchphrases_fa || ''}
                              onChange={(e) => updateCharField(char.id, 'persona_behavior_prompt', e.target.value)}
                              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 leading-relaxed"
                              placeholder="تکیه‌کلام‌های فارسی، رفتار روانشناختی، سرعت تکلم و حرکات فیزیکی بدنی..."
                            />
                          </div>

                        </div>
                      );
                    })}
                  </div>

                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 px-6 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {saveSuccess && (
              <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-xl">
                <CheckCircle2 className="w-4 h-4" />
                تغییرات دنیای کانال با موفقیت در universe.json ذخیره شد!
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              بستن
            </button>

            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-black text-slate-950 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 shadow-lg shadow-amber-500/20 transition-all hover:scale-105"
            >
              <Save className="w-4 h-4" />
              {saving ? 'در حال ذخیره‌سازی...' : 'ذخیره تغییرات دنیای کانال'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
