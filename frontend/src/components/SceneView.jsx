import React, { useState } from 'react';
import { 
  Film, 
  Copy, 
  Check, 
  Upload, 
  CheckCircle2, 
  Clock, 
  Volume2, 
  Camera, 
  ExternalLink,
  Video,
  Save,
  Image as ImageIcon,
  MoveHorizontal,
  ZoomIn,
  ZoomOut,
  Zap,
  RefreshCw,
  Sparkles,
  Bot,
  Play
} from 'lucide-react';
import { 
  uploadAsset, 
  uploadSceneVideo, 
  updateSceneDetails
} from '../api';

export default function SceneView({
  scenes = [],
  episodeId,
  stageStatus,
  onApproveStage,
  onUpdateSceneStatus,
  onSceneAssetUpdated,
  onRefresh
}) {
  const [copiedExecutionCmd, setCopiedExecutionCmd] = useState(false);
  const [copiedSingleCmdId, setCopiedSingleCmdId] = useState(null);
  const [copiedPromptId, setCopiedPromptId] = useState(null);
  const [copiedMotionId, setCopiedMotionId] = useState(null);
  const [uploadingImageId, setUploadingImageId] = useState(null);
  const [uploadingVideoId, setUploadingVideoId] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Track images that failed to load to fall back to alternative paths or placeholders
  const [imgErrorMap, setImgErrorMap] = useState({});

  // Local editable motion prompts map: { [sceneId]: text }
  const [editedMotionPrompts, setEditedMotionPrompts] = useState({});
  const [savingPromptId, setSavingPromptId] = useState(null);

  const copyText = (id, text, type = 'image') => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    if (type === 'image') {
      setCopiedPromptId(id);
      setTimeout(() => setCopiedPromptId(null), 2000);
    } else {
      setCopiedMotionId(id);
      setTimeout(() => setCopiedMotionId(null), 2000);
    }
  };

  const handleCopyFullExecutionCommand = async () => {
    const cmd = `لطفاً مرحله ۶ (کارگردانی استوری‌بورد و تولید کامل تصاویر) را برای اپیزود "${episodeId}" طبق سند .agent/skills/04-scene-director.md به طور کامل و انتها به انتها اجرا کن:
۱. سناریو و چیدمان صندلی‌های اپیزود "${episodeId}" را بخوان و استوری‌بورد کامل و دقیق با کادربندی ۹:۱۶ عمودی، جزئیات بالا (حداقل ۸۰ تا ۱۲۰ کلمه برای هر پرامپت)، همسایگان صندلی (adjacent_players) و وضعیت زنده میز (table_state_en) بنویس و در projects/${episodeId}/state.json ذخیره کن.
۲. سپس با استفاده از ابزار image-generator، تک تک فریم‌های کلیدی (scene_01.png تا scene_N.png) را به صورت متوالی و با اعمال رفرنس‌های تصویری روی دیسک (برای صحنه ۱: رفرنس @Room_Master و شیت‌های کاراکترها؛ برای صحنه‌های ۲ به بعد: تصویر scene_01.png به عنوان Episode Master Reference + رفرنس زاویه صندلی @Seat_X) تولید کن و مستقیماً در فولدر projects/${episodeId}/assets/images/ ذخیره نما.
۳. پس از تولید، از وجود و کیفیت فایل‌ها مطمئن شو و state.json را با مسیرهای نهایی بروزرسانی کن.`;

    await navigator.clipboard.writeText(cmd);
    setCopiedExecutionCmd(true);
    setTimeout(() => setCopiedExecutionCmd(false), 3500);
  };

  const handleCopySingleFrameCommand = async (scene, idx) => {
    const sId = scene.id || scene.scene_id || `scene_${String(idx + 1).padStart(2, '0')}`;
    const visualPrompt = scene.visual_prompt_en || scene.visual_prompt || '';
    const cameraAngle = scene.camera || scene.camera_angle || '@Seat_X';
    const chars = (scene.characters_present || []).join(', ');
    const adjacent = Array.isArray(scene.adjacent_players) ? scene.adjacent_players.join(', ') : (scene.adjacent_players || 'مطابق چیدمان صندلی');
    const tableState = scene.table_state_en || '';

    const cmd = `لطفاً فریم کلیدی صحنه "${sId}" اپیزود "${episodeId}" را طبق دستورالعمل .agent/skills/04-scene-director.md با استفاده از ابزار image-generator بازسازی کن:
- فایل خروجی مقصد: projects/${episodeId}/assets/images/${sId}.png
- زاویه دوربین: ${cameraAngle}
- کاراکترهای حاضر: ${chars}
- همسایگان صندلی: ${adjacent}
- وضعیت میز: ${tableState}
- رفرنس پیوستگی: ${idx === 0 ? 'رفرنس @Room_Master و شیت‌های کاراکترها' : `تصویر projects/${episodeId}/assets/images/scene_01.png (Episode Master Reference) + رفرنس زاویه صندلی`}
- پرامپت دقیق تصویر:
${visualPrompt}
پس از تولید، فایل را در projects/${episodeId}/assets/images/${sId}.png ذخیره و state.json را بروزرسانی کن.`;

    await navigator.clipboard.writeText(cmd);
    setCopiedSingleCmdId(sId);
    setTimeout(() => setCopiedSingleCmdId(null), 2500);
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    setImgErrorMap({});
    try {
      if (onRefresh) {
        await onRefresh();
      }
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  const handleKeyframeImageUpload = async (sceneId, file) => {
    if (!file) return;
    setUploadingImageId(sceneId);
    try {
      const res = await uploadAsset(episodeId, 'scenes', file);
      if (onSceneAssetUpdated) {
        onSceneAssetUpdated(sceneId, res.url);
      }
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در آپلود فریم کلیدی: ' + err.message);
    } finally {
      setUploadingImageId(null);
    }
  };

  const handleVideoUpload = async (sceneId, file) => {
    if (!file) return;
    setUploadingVideoId(sceneId);
    try {
      await uploadSceneVideo(episodeId, sceneId, file);
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در آپلود ویدیوی متحرک: ' + err.message);
    } finally {
      setUploadingVideoId(null);
    }
  };

  const handleToggleShotMode = async (sceneId, newMode) => {
    try {
      await updateSceneDetails(episodeId, sceneId, { shot_mode: newMode });
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در تغییر حالت نما: ' + err.message);
    }
  };

  const handleCameraEffectChange = async (sceneId, newEffect) => {
    try {
      await updateSceneDetails(episodeId, sceneId, { camera_effect: newEffect });
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در تغییر افکت دوربین: ' + err.message);
    }
  };

  const handleSaveMotionPrompt = async (sceneId, fallbackCurrentPrompt) => {
    const newText = editedMotionPrompts[sceneId] !== undefined ? editedMotionPrompts[sceneId] : fallbackCurrentPrompt;
    setSavingPromptId(sceneId);
    try {
      await updateSceneDetails(episodeId, sceneId, { motion_prompt_en: newText, shot_mode: 'ai_video' });
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در ذخیره پرامپت حرکت: ' + err.message);
    } finally {
      setSavingPromptId(null);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner with Antigravity Native Pipeline Execution Button */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-amber-500/30 shadow-2xl">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5" />
              مرحله ۶: کارگردانی یکپارچه استوری‌بورد و تصاویر (Antigravity Native)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              تعداد نماها: {scenes.length} کات سریع (~۲s)
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            کارگردانی نماهای سریع عمودی و تولید مستقیم تصاویر در آنتی‌گرویتی
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
            تقطیع سناریو طبق استاندارد <span className="text-amber-300 font-mono font-semibold">04-scene-director.md</span>: کادربندی عمودی ۹:۱۶، همسایگان صندلی، وضعیت زنده میز و تولید مستقیم تک‌تک فریم‌ها در <span className="text-emerald-300 font-mono">/projects/{episodeId}/assets/images/</span> با حفظ کامل پیوستگی صحنه ۱.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap flex-shrink-0">
          
          {/* Prominent Action Button: Full Storyboard & Image Generation in Antigravity */}
          <button
            onClick={handleCopyFullExecutionCommand}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl font-black text-xs shadow-xl transition-all hover:scale-105 active:scale-95 ${
              copiedExecutionCmd
                ? 'bg-emerald-400 text-slate-950 shadow-emerald-500/30 ring-2 ring-emerald-300'
                : 'bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 shadow-amber-500/25'
            }`}
          >
            {copiedExecutionCmd ? (
              <>
                <Check className="w-4 h-4 text-slate-950" />
                <span>دستور کپی شد! در چت آنتی‌گرویتی ارسال کنید ✓</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-slate-950" />
                <span>🎬 دستور اجرای کامل صحنه‌سازی و تولید تصاویر در آنتی‌گرویتی</span>
              </>
            )}
          </button>

          {/* Refresh / Sync Images Button */}
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3.5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all hover:scale-102"
            title="همگام‌سازی و بارگذاری مجدد فایل‌های تصویر از روی دیسک"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-amber-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'در حال همگام‌سازی...' : 'همگام‌سازی تصاویر ↻'}</span>
          </button>

          {/* External Link to Google Flow */}
          <a
            href="https://labs.google/fx/tools/flow"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 font-bold text-xs border border-slate-700 transition-all hover:scale-102"
            title="محیط Google Flow برای متحرک‌سازی کلیپ‌های ویدیویی"
          >
            <span>Google Flow</span>
            <ExternalLink className="w-3.5 h-3.5 text-indigo-400" />
          </a>

          {/* Stage Approval Badge */}
          {stageStatus === 'approved' ? (
            <div className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              تایید شد ✓
            </div>
          ) : (
            <button
              onClick={onApproveStage}
              className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/20 transition-all hover:scale-105"
            >
              <Check className="w-4 h-4" />
              تایید کلی صحنه‌ها
            </button>
          )}
        </div>
      </div>

      {/* Empty State Banner if no scenes yet */}
      {scenes.length === 0 && (
        <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <Film className="w-12 h-12 text-slate-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-200">هنوز استوری‌بورد این اپیزود تولید نشده است</h3>
            <p className="text-xs text-slate-400 max-w-lg mx-auto">
              روی دکمه طلایی بالا کلیک کنید تا دستور اجرای کامل مهارت ۰۴ در کلیپ‌بورد کپی شود و آن را در چت آنتی‌گرویتی ارسال نمایید تا همه صحنه‌ها و تصاویر به صورت محلی و دقیق ساخته شوند.
            </p>
          </div>
          <button
            onClick={handleCopyFullExecutionCommand}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs shadow-lg transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>کپی دستور اجرای کامل در آنتی‌گرویتی</span>
          </button>
        </div>
      )}

      {/* Scenes Grid: Responsive 9:16 Vertical Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scenes.map((scene, idx) => {
          const sceneId = scene.id || scene.scene_id || `scene_${String(idx + 1).padStart(2, '0')}`;
          const isApproved = scene.status === 'approved';
          const isReady = scene.status === 'ready_for_review';
          const tableState = scene.poker_table_state || {};
          const visualPrompt = scene.visual_prompt_en || scene.visual_prompt || '';
          
          const motionPrompt = editedMotionPrompts[sceneId] !== undefined
            ? editedMotionPrompts[sceneId]
            : (scene.motion_prompt_en || '');
          const shotMode = scene.shot_mode || (motionPrompt.trim() || scene.video_path ? 'ai_video' : 'static_zoom');
          const isAiVideo = shotMode === 'ai_video';

          const cameraEffect = scene.camera_effect || 'zoom_in';
          const duration = scene.duration_sec ? Number(scene.duration_sec).toFixed(1) : '2.0';

          const videoUrl = scene.video_path || scene.video_asset;
          
          // Image resolution order:
          // 1. Explicit scene.image_path if valid and not errored
          // 2. Default native assets path: /media/${episodeId}/assets/images/${sceneId}.png
          // 3. Fallback to /media/${episodeId}/scenes/${sceneId}.png
          // 4. scene.visual_asset
          const errorCount = imgErrorMap[sceneId] || 0;
          let imageUrl = null;
          if (errorCount === 0) {
            imageUrl = scene.image_path || `/media/${episodeId}/assets/images/${sceneId}.png`;
          } else if (errorCount === 1) {
            imageUrl = scene.visual_asset || `/media/${episodeId}/scenes/${sceneId}.png`;
          } else {
            imageUrl = null; // show placeholder
          }

          const isSingleCommandCopied = copiedSingleCmdId === sceneId;

          return (
            <div
              key={sceneId}
              className={`rounded-2xl border transition-all flex flex-col justify-between overflow-hidden shadow-lg group ${
                isAiVideo 
                  ? 'bg-slate-900 border-indigo-500/30 ring-1 ring-indigo-500/10'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700/80'
              }`}
            >
              
              {/* Card Header */}
              <div className="p-4 border-b border-slate-800/80 space-y-3 bg-slate-950/40">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold text-xs flex items-center justify-center font-mono">
                      #{scene.beat_index || idx + 1}
                    </span>
                    <span className="text-xs font-mono text-slate-300 flex items-center gap-1 font-semibold">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {duration}s
                    </span>
                    {scene.camera && (
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700 ltr-content">
                        🎥 {scene.camera}
                      </span>
                    )}
                    {idx === 0 || scene.beat_index === 1 ? (
                      <span className="text-[10px] font-bold text-amber-300 bg-amber-500/15 border border-amber-500/30 px-2 py-0.5 rounded">
                        ⭐ نمای معرف مستر
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium text-slate-400 bg-slate-800/80 border border-slate-700/60 px-2 py-0.5 rounded">
                        🔗 پیوسته با صحنه ۱
                      </span>
                    )}
                  </div>

                  {/* Status Toggle Badge */}
                  <button
                    onClick={() => onUpdateSceneStatus(sceneId, isApproved ? 'ready_for_review' : 'approved')}
                    className={`flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-lg transition-all ${
                      isApproved
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                        : isReady
                        ? 'bg-purple-500/10 text-purple-300 border border-purple-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {isApproved ? 'تایید شد ✓' : isReady ? 'آماده بازبینی' : 'در صف ساخت'}
                  </button>
                </div>

                {/* Scene Title */}
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <span>{scene.title || scene.scene_title_fa || `صحنه #${idx + 1}`}</span>
                </h3>

                {/* Mode Switcher Segmented Control */}
                <div className="flex items-center p-1 rounded-xl bg-slate-950 border border-slate-800/90 text-xs">
                  <button
                    type="button"
                    onClick={() => handleToggleShotMode(sceneId, 'static_zoom')}
                    className={`flex-1 py-1.5 px-2 rounded-lg font-bold transition-all flex items-center justify-center gap-1.5 ${
                      !isAiVideo
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <ImageIcon className="w-3.5 h-3.5 text-amber-400" />
                    <span>تصویر + موشن FFmpeg (~2s)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleToggleShotMode(sceneId, 'ai_video')}
                    className={`flex-1 py-1.5 px-2 rounded-lg font-bold transition-all flex items-center justify-center gap-1.5 ${
                      isAiVideo
                        ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/50 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Video className="w-3.5 h-3.5 text-indigo-400" />
                    <span>ویدیو متحرک (~2s)</span>
                  </button>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 space-y-4 flex-1">

                {/* ======================================================== */}
                {/* STEP 1: KEYFRAME IMAGE */}
                {/* ======================================================== */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-md bg-amber-500 text-slate-950 text-[11px] font-black flex items-center justify-center">
                        ۱
                      </span>
                      <span className="text-xs font-bold text-amber-300">
                        فریم کلیدی (Keyframe Image)
                      </span>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap justify-end">
                      {/* 1-Click Rebuild Frame in Antigravity */}
                      <button
                        onClick={() => handleCopySingleFrameCommand(scene, idx)}
                        className={`flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-md transition-all shadow-sm ${
                          isSingleCommandCopied
                            ? 'bg-emerald-500 text-slate-950 font-black'
                            : 'bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300'
                        }`}
                        title="کپی دستور بازسازی این فریم کلیدی در آنتی‌گرویتی"
                      >
                        {isSingleCommandCopied ? (
                          <>
                            <Check className="w-3 h-3 text-slate-950" />
                            <span>دستور کپی شد!</span>
                          </>
                        ) : (
                          <>
                            <Bot className="w-3 h-3 text-amber-400" />
                            <span>بازسازی این فریم در آنتی‌گرویتی</span>
                          </>
                        )}
                      </button>

                      {/* Image Prompt Copy */}
                      <button
                        onClick={() => copyText(sceneId, visualPrompt, 'image')}
                        className="flex items-center gap-1 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-md transition-colors"
                        title="کپی پرامپت متنی انگلیسی"
                      >
                        {copiedPromptId === sceneId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedPromptId === sceneId ? 'کپی شد!' : 'پرامپت'}</span>
                      </button>

                      {/* Image Upload Button */}
                      <label className="flex items-center gap-1 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded-md cursor-pointer transition-colors">
                        <Upload className="w-3 h-3 text-amber-400" />
                        <span>آپلود دستی</span>
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handleKeyframeImageUpload(sceneId, e.target.files?.[0])}
                        />
                      </label>
                    </div>
                  </div>

                  {/* Continuity lock badge for Scene 2+ */}
                  {(scene.beat_index > 1 || idx > 0) && (
                    <div className="text-[10px] font-bold text-amber-300/90 bg-amber-950/60 border border-amber-800/60 px-2.5 py-1 rounded-lg flex items-center gap-1.5 shadow-sm">
                      <span>🔗</span>
                      <span>قفل پیوستگی: رفرنس به تصویر صحنه ۱ (Master) + زاویه صندلی</span>
                    </div>
                  )}

                  {/* Image Display & Preview (Vertical 9:16) */}
                  <div className="relative aspect-[9/16] w-full max-h-[380px] mx-auto bg-[#070b13] rounded-xl border border-slate-800 overflow-hidden flex items-center justify-center shadow-inner">
                    {imageUrl ? (
                      <img
                        src={imageUrl}
                        alt={scene.title || 'Keyframe Preview'}
                        onError={() => {
                          setImgErrorMap(prev => ({
                            ...prev,
                            [sceneId]: (prev[sceneId] || 0) + 1
                          }));
                        }}
                        className="w-full h-full object-contain transition-transform group-hover:scale-101"
                      />
                    ) : (
                      <div className="p-4 text-center space-y-2">
                        <Camera className="w-8 h-8 text-slate-600 mx-auto" />
                        <span className="text-xs font-bold text-slate-300 block">فریم کلیدی ۹:۱۶ موجود نیست</span>
                        <p className="text-[10px] text-slate-500 max-w-[200px] mx-auto leading-relaxed">
                          با کلیک روی «بازسازی این فریم در آنتی‌گرویتی»، دستور آن را برای ایجنت ارسال کنید یا تصویر را دستی آپلود نمایید.
                        </p>
                      </div>
                    )}

                    {/* SFX Floating Badge */}
                    {scene.sfx_cue && (
                      <div className="absolute top-2 left-2 bg-rose-950/90 border border-rose-700 text-rose-200 text-[10px] font-mono font-bold px-2 py-0.5 rounded-md flex items-center gap-1 shadow-lg backdrop-blur-sm ltr-content">
                        <Volume2 className="w-3 h-3 text-rose-400" />
                        {scene.sfx_cue}
                      </div>
                    )}

                    {/* Poker HUD Overlay floating card */}
                    {tableState && (tableState.action_badge || tableState.board || tableState.pot_bb) && (
                      <div className="absolute bottom-2 right-2 left-2 bg-slate-950/90 border border-slate-700/80 text-amber-300 text-[10px] font-bold p-1.5 rounded-lg backdrop-blur-sm space-y-0.5 ltr-content">
                        <div className="flex items-center justify-between text-slate-300 font-mono">
                          <span>{tableState.hero_hand ? `Hand: ${tableState.hero_hand}` : 'Hero Hand'}</span>
                          <span className="text-amber-400">{tableState.pot_bb ? `Pot: ${tableState.pot_bb} BB` : ''}</span>
                        </div>
                        {tableState.board && (
                          <div className="text-emerald-300 font-mono truncate">
                            Board: {Array.isArray(tableState.board) ? tableState.board.join(' ') : tableState.board}
                          </div>
                        )}
                        {tableState.action_badge && (
                          <div className="text-amber-200 font-sans truncate">
                            🃏 {tableState.action_badge}
                          </div>
                        )}
                      </div>
                    )}

                    {uploadingImageId === sceneId && (
                      <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center text-xs font-bold text-amber-400">
                        در حال بارگذاری تصویر...
                      </div>
                    )}
                  </div>

                  {/* Persistent Table State & Adjacent Seated Players HUD */}
                  {(scene.table_state_en || (scene.adjacent_players && scene.adjacent_players.length > 0)) && (
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1.5 text-[11px]">
                      {scene.table_state_en && (
                        <div className="text-emerald-300/90 font-mono text-[10px] ltr-content flex items-start gap-1.5 leading-snug">
                          <span className="text-amber-400 font-bold flex-shrink-0">🎲 Table:</span>
                          <span className="leading-tight">{scene.table_state_en}</span>
                        </div>
                      )}
                      {scene.adjacent_players && scene.adjacent_players.length > 0 && (
                        <div className="text-slate-300 font-mono text-[10px] ltr-content flex items-center gap-1.5 flex-wrap">
                          <span className="text-indigo-400 font-bold flex-shrink-0">👥 Neighbors:</span>
                          <span className="text-slate-400">
                            {Array.isArray(scene.adjacent_players) ? scene.adjacent_players.join(', ') : scene.adjacent_players}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Image Prompt Textbox */}
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 text-[11px] font-mono text-slate-300 ltr-content leading-relaxed max-h-24 overflow-y-auto">
                    {visualPrompt || 'هنوز پرامپت تصویری برای این صحنه تولید نشده است.'}
                  </div>
                </div>

                {/* ======================================================== */}
                {/* CONDITIONAL BODY: STATIC ZOOM vs AI VIDEO */}
                {/* ======================================================== */}
                {!isAiVideo ? (
                  /* MODE A: STATIC ZOOM (FFMPEG CAMERA MOTION) */
                  <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800/80 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300">
                        <ImageIcon className="w-4 h-4 text-amber-400" />
                        <span>حرکت دوربین FFmpeg (Ken Burns)</span>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        تصویر ثابت + حرکت دوربین
                      </span>
                    </div>

                    {/* Camera Effect Buttons */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {[
                        { id: 'zoom_in', label: '🔍 زوم به داخل (Dramatic Push)', icon: ZoomIn },
                        { id: 'zoom_out', label: '🔎 زوم به خارج (Establish)', icon: ZoomOut },
                        { id: 'pan_left', label: '↔️ حرکت افقی (Pan)', icon: MoveHorizontal },
                        { id: 'shake', label: '⚡ لرزش شدید (Tilt/Shock)', icon: Zap },
                      ].map((eff) => (
                        <button
                          key={eff.id}
                          type="button"
                          onClick={() => handleCameraEffectChange(sceneId, eff.id)}
                          className={`p-2 rounded-lg text-start transition-all border ${
                            cameraEffect === eff.id
                              ? 'bg-amber-500/15 border-amber-500/50 text-amber-300 font-bold'
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                          }`}
                        >
                          <div className="text-[11px] leading-snug">{eff.label}</div>
                        </button>
                      ))}
                    </div>

                    <p className="text-[10px] text-slate-500 leading-relaxed">
                      💡 در تدوین نهایی FFmpeg، تصویر فریم کلیدی بالا به مدت ~{duration} ثانیه با افکت انتخابی متحرک می‌شود.
                    </p>
                  </div>
                ) : (
                  /* MODE B: AI VIDEO (VIDU / GOOGLE FLOW ~2s) */
                  <div className="p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-3">
                    
                    {/* Header */}
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-md bg-indigo-500 text-white text-[11px] font-black flex items-center justify-center">
                          ۲
                        </span>
                        <span className="text-xs font-bold text-indigo-300">
                          کلیپ متحرک Vidu / Google Flow
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                          هایلایت: ~{duration}s
                        </span>

                        {motionPrompt && (
                          <button
                            onClick={() => copyText(sceneId, motionPrompt, 'motion')}
                            className="flex items-center gap-1 text-[11px] font-bold text-indigo-300 hover:text-white bg-indigo-600 hover:bg-indigo-500 px-2.5 py-1 rounded-md transition-all shadow-sm shadow-indigo-600/30"
                          >
                            {copiedMotionId === sceneId ? <Check className="w-3 h-3 text-emerald-300" /> : <Copy className="w-3 h-3" />}
                            <span>{copiedMotionId === sceneId ? 'کپی شد!' : 'کپی پرامپت حرکت'}</span>
                          </button>
                        )}

                        {motionPrompt && (
                          <button
                            onClick={() => handleSaveMotionPrompt(sceneId, motionPrompt)}
                            disabled={savingPromptId === sceneId}
                            title="ذخیره ویرایش پرامپت حرکت"
                            className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
                          >
                            <Save className={`w-3.5 h-3.5 ${savingPromptId === sceneId ? 'animate-spin' : ''}`} />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Motion Prompt Textarea */}
                    <div className="space-y-1">
                      <label className="text-[10px] text-slate-400 font-medium block">
                        پرامپت حرکت (بازیگری بی‌صدا، بدون فلگ زمانی در متن):
                      </label>
                      <textarea
                        rows={2}
                        value={motionPrompt}
                        onChange={(e) => setEditedMotionPrompts({ ...editedMotionPrompts, [sceneId]: e.target.value })}
                        placeholder="پرامپت حرکت ۲ ثانیه‌ای برای Google Flow / Vidu..."
                        className="w-full p-2.5 rounded-lg bg-slate-950 border border-indigo-900/60 text-[11px] font-mono text-indigo-100 focus:border-indigo-400 focus:outline-none ltr-content leading-relaxed resize-y"
                      />
                    </div>

                    {/* Inline Video Player OR Upload Dropzone */}
                    <div className="space-y-2">
                      {videoUrl ? (
                        <div className="space-y-2">
                          {/* Video Display (Vertical 9:16) */}
                          <div className="relative aspect-[9/16] w-full max-h-[380px] mx-auto rounded-xl overflow-hidden border border-indigo-500/40 bg-black flex items-center justify-center shadow-lg">
                            <video
                              src={videoUrl}
                              controls
                              className="w-full h-full object-contain"
                            />
                          </div>

                          {/* Replace Video Button */}
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-emerald-400 font-bold flex items-center gap-1 font-mono">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              کلیپ متحرک بارگذاری شده
                            </span>

                            <label className="flex items-center gap-1 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded cursor-pointer transition-colors">
                              <Video className="w-3 h-3 text-indigo-400" />
                              <span>تغییر فایل MP4</span>
                              <input
                                type="file"
                                accept="video/mp4,video/*"
                                className="hidden"
                                onChange={(e) => handleVideoUpload(sceneId, e.target.files?.[0])}
                              />
                            </label>
                          </div>
                        </div>
                      ) : (
                        <div className="p-3 rounded-xl border border-dashed border-indigo-500/40 bg-indigo-950/20 text-center space-y-1.5">
                          <Video className="w-6 h-6 text-indigo-400 mx-auto" />
                          <div>
                            <span className="text-xs font-bold text-slate-200 block">
                              آپلود کلیپ متحرک ۹:۱۶ (.mp4)
                            </span>
                            <p className="text-[10px] text-slate-400">
                              کلیپ دانلودی از Google Flow / Vidu را اینجا قرار دهید.
                            </p>
                          </div>

                          <label className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs cursor-pointer shadow-md shadow-indigo-600/20 transition-all hover:scale-102">
                            <Upload className="w-3.5 h-3.5" />
                            <span>انتخاب فایل MP4</span>
                            <input
                              type="file"
                              accept="video/mp4,video/*"
                              className="hidden"
                              onChange={(e) => handleVideoUpload(sceneId, e.target.files?.[0])}
                            />
                          </label>

                          {uploadingVideoId === sceneId && (
                            <div className="text-xs font-bold text-amber-400 pt-1">
                              در حال آپلود و پردازش ویدیو...
                            </div>
                          )}
                        </div>
                      )}
                    </div>

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
