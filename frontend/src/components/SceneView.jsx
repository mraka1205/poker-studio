import React, { useState } from 'react';
import { 
  Film, 
  Copy, 
  Check, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Volume2, 
  Camera, 
  Layers, 
  Sparkles,
  Bot,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Video,
  Play,
  Save,
  Wand2,
  Image as ImageIcon,
  MoveHorizontal,
  ZoomIn,
  ZoomOut,
  Zap,
  RefreshCw
} from 'lucide-react';
import AiStudioBridge from './AiStudioBridge';
import { 
  uploadAsset, 
  uploadSceneVideo, 
  runOpenRouterTask, 
  saveProjectState, 
  fetchProjectState, 
  rewriteScenePrompt,
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
  const [copiedPromptId, setCopiedPromptId] = useState(null);
  const [copiedMotionId, setCopiedMotionId] = useState(null);
  const [uploadingImageId, setUploadingImageId] = useState(null);
  const [uploadingVideoId, setUploadingVideoId] = useState(null);
  const [isGeneratingScenes, setIsGeneratingScenes] = useState(false);
  const [showAiStudioBridge, setShowAiStudioBridge] = useState(false);
  
  // Local editable motion prompts map: { [sceneId]: text }
  const [editedMotionPrompts, setEditedMotionPrompts] = useState({});
  const [savingPromptId, setSavingPromptId] = useState(null);

  // Scene-Level Human-in-the-Loop Feedback state
  const [imageFeedback, setImageFeedback] = useState({});
  const [motionFeedback, setMotionFeedback] = useState({});
  const [isRewriting, setIsRewriting] = useState(null); // `${sceneId}_${target}`

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

  const handleGenerateScenes = async () => {
    setIsGeneratingScenes(true);
    try {
      await runOpenRouterTask(episodeId, 'generate_scenes');
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در تولید خودکار استوری‌بورد: ' + err.message);
    } finally {
      setIsGeneratingScenes(false);
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

  const handleRewritePrompt = async (sceneId, target, customFeedback = null) => {
    const feedback = customFeedback || (target === 'image' ? imageFeedback[sceneId] : motionFeedback[sceneId]);
    if (!feedback || !feedback.trim()) return;

    const rewriteKey = `${sceneId}_${target}`;
    setIsRewriting(rewriteKey);
    try {
      const res = await rewriteScenePrompt(episodeId, sceneId, target, feedback.trim());
      if (target === 'image') {
        setImageFeedback((prev) => ({ ...prev, [sceneId]: '' }));
      } else {
        setMotionFeedback((prev) => ({ ...prev, [sceneId]: '' }));
        setEditedMotionPrompts((prev) => ({ ...prev, [sceneId]: res.rewritten_prompt }));
      }
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در بازنویسی پرامپت با هوش مصنوعی: ' + err.message);
    } finally {
      setIsRewriting(null);
    }
  };

  const handleGenerateSingleMotion = (sceneId) => {
    handleRewritePrompt(
      sceneId, 
      'motion', 
      'تولید یک پرامپت حرکت کوتاه و پرانرژی برای هایلایت ۲ ثانیه‌ای بر اساس کاراکترهای صحنه، بازیگری بی‌صدا، و بدون اشیاء معلق'
    );
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner with Unified 1-Click Action */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۶: کارگردانی یکپارچه استوری‌بورد و حرکت (Unified Storyboard & Motion)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              تعداد نماها: {scenes.length} کات سریع (~۲s)
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            کارگردانی نماهای سریع عمودی (کات‌های ~۲ ثانیه‌ای Shorts / Reels)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
            تقطیع سناریو به کات‌های ضرب‌الاجلی: ~۷۰٪ تصاویر ثابت با زوم و موشن FFmpeg و ~۳۰٪ هایلایت‌های متحرک Vidu / Google Flow برای پانچ‌لاین‌ها و اوج خنده‌ها.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap flex-shrink-0">
          
          {/* Unified Action: Generate Complete Storyboard in 1 Click */}
          <button
            onClick={handleGenerateScenes}
            disabled={isGeneratingScenes}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-xs shadow-lg shadow-amber-500/20 transition-all hover:scale-105 disabled:opacity-50"
          >
            <Wand2 className={`w-4 h-4 text-slate-950 ${isGeneratingScenes ? 'animate-spin' : ''}`} />
            {isGeneratingScenes ? 'در حال تولید خودکار استوری‌بورد (صحنه + حرکت)...' : 'تولید خودکار استوری‌بورد (صحنه + حرکت)'}
          </button>

          {/* External Link to Google Flow */}
          <a
            href="https://labs.google/fx/tools/flow"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all hover:scale-102"
          >
            <span>Google Flow</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          {/* Toggle Manual AI Studio Bridge */}
          <button
            onClick={() => setShowAiStudioBridge(!showAiStudioBridge)}
            className="flex items-center gap-1 px-3 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            AI Studio دستی
            {showAiStudioBridge ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {/* Stage Approval Badge */}
          {stageStatus === 'approved' ? (
            <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              تایید شد ✓
            </div>
          ) : (
            <button
              onClick={onApproveStage}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/20 transition-all hover:scale-105"
            >
              <Check className="w-4 h-4" />
              تایید کلی صحنه‌ها
            </button>
          )}
        </div>
      </div>

      {/* Collapsible AI Studio Bridge */}
      {showAiStudioBridge && (
        <AiStudioBridge
          episodeId={episodeId}
          stage="scenes"
          stageTitle="استوری‌بورد و پرامپت صحنه‌ها"
          description="اگر ترجیح می‌دهید سناریو را مستقیماً در Google AI Studio به بیت‌های بصری تبدیل کنید، از این پل ارتباطی استفاده نمایید."
          onSuccess={() => {
            if (onRefresh) onRefresh();
          }}
        />
      )}

      {/* Scenes Grid: Responsive 9:16 Vertical Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scenes.map((scene, idx) => {
          const isApproved = scene.status === 'approved';
          const isReady = scene.status === 'ready_for_review';
          const tableState = scene.poker_table_state || {};
          const visualPrompt = scene.visual_prompt_en || scene.visual_prompt || '';
          
          // Determine shot mode: default to static_zoom if empty and no motion prompt
          const motionPrompt = editedMotionPrompts[scene.id] !== undefined
            ? editedMotionPrompts[scene.id]
            : (scene.motion_prompt_en || '');
          const shotMode = scene.shot_mode || (motionPrompt.trim() || scene.video_path ? 'ai_video' : 'static_zoom');
          const isAiVideo = shotMode === 'ai_video';

          const cameraEffect = scene.camera_effect || 'zoom_in';
          const duration = scene.duration_sec ? Number(scene.duration_sec).toFixed(1) : '2.0';

          const videoUrl = scene.video_path || scene.video_asset;
          const imageUrl = scene.visual_asset || scene.image_path;

          return (
            <div
              key={scene.id || scene.scene_id || idx}
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
                    onClick={() => onUpdateSceneStatus(scene.id, isApproved ? 'ready_for_review' : 'approved')}
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
                    onClick={() => handleToggleShotMode(scene.id, 'static_zoom')}
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
                    onClick={() => handleToggleShotMode(scene.id, 'ai_video')}
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
                {/* STEP 1: KEYFRAME IMAGE (برای هر دو حالت نمایش داده می‌شود) */}
                {/* ======================================================== */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-md bg-amber-500 text-slate-950 text-[11px] font-black flex items-center justify-center">
                        ۱
                      </span>
                      <span className="text-xs font-bold text-amber-300">
                        فریم کلیدی (Keyframe Image)
                      </span>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap justify-end">
                      {/* Continuity badge for Scene 2+ */}
                      {(scene.beat_index > 1 || idx > 0) && (
                        <span 
                          title="تصویر فریم کلیدی صحنه ۱ را به عنوان مرجع پیوستگی به همراه زاویه صندلی در Google Flow قرار دهید"
                          className="text-[10px] font-bold text-amber-300/95 bg-amber-950/70 border border-amber-700/80 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-sm"
                        >
                          🔗 مرجع پیوستگی: تصویر صحنه ۱ (Master) + زاویه صندلی
                        </span>
                      )}

                      {/* Image Prompt Copy */}
                      <button
                        onClick={() => copyText(scene.id, visualPrompt, 'image')}
                        className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-md transition-colors"
                      >
                        {copiedPromptId === scene.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        {copiedPromptId === scene.id ? 'کپی شد!' : 'کپی پرامپت'}
                      </button>

                      {/* Image Upload Button */}
                      <label className="flex items-center gap-1 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded-md cursor-pointer transition-colors">
                        <Upload className="w-3 h-3 text-amber-400" />
                        <span>آپلود تصویر</span>
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handleKeyframeImageUpload(scene.id, e.target.files?.[0])}
                        />
                      </label>
                    </div>
                  </div>

                  {/* Image Display & Preview (Vertical 9:16) */}
                  <div className="relative aspect-[9/16] w-full max-h-[380px] mx-auto bg-[#070b13] rounded-xl border border-slate-800 overflow-hidden flex items-center justify-center shadow-inner">
                    {imageUrl ? (
                      <img
                        src={imageUrl}
                        alt={scene.title || 'Keyframe Preview'}
                        className="w-full h-full object-contain transition-transform group-hover:scale-101"
                      />
                    ) : (
                      <div className="p-4 text-center space-y-1.5">
                        <Camera className="w-7 h-7 text-slate-600 mx-auto" />
                        <span className="text-xs font-bold text-slate-400 block">فریم کلیدی ۹:۱۶ آپلود نشده</span>
                        <p className="text-[10px] text-slate-500">
                          پرامپت عمودی را در ابزار تصویرسازی اجرا کرده و تصویر را اینجا آپلود کنید.
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

                    {uploadingImageId === scene.id && (
                      <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center text-xs font-bold text-amber-400">
                        در حال بارگذاری تصویر...
                      </div>
                    )}
                  </div>

                  {/* Persistent Table State & Adjacent Seated Players HUD */}
                  {(scene.table_state_en || (scene.adjacent_players && scene.adjacent_players.length > 0)) && (
                    <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1 text-[11px]">
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
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 text-[11px] font-mono text-slate-300 ltr-content leading-relaxed max-h-20 overflow-y-auto">
                    {visualPrompt || 'هنوز پرامپت تصویری برای این صحنه تولید نشده است.'}
                  </div>

                  {/* Human-in-the-Loop Image Prompt Rewrite */}
                  <div className="pt-2 border-t border-slate-800/80 space-y-1">
                    <div className="flex gap-1.5">
                      <input
                        type="text"
                        value={imageFeedback[scene.id] || ''}
                        onChange={(e) => setImageFeedback({ ...imageFeedback, [scene.id]: e.target.value })}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRewritePrompt(scene.id, 'image');
                        }}
                        placeholder="فیدبک برای اصلاح پرامپت تصویر... مثلاً: کلوزآپتر باشه"
                        className="flex-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder:text-slate-500 focus:border-amber-500 focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => handleRewritePrompt(scene.id, 'image')}
                        disabled={isRewriting === `${scene.id}_image` || !imageFeedback[scene.id]?.trim()}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-slate-950 font-bold text-[11px] shadow-sm transition-all flex-shrink-0"
                      >
                        <Wand2 className={`w-3.5 h-3.5 ${isRewriting === `${scene.id}_image` ? 'animate-spin' : ''}`} />
                        {isRewriting === `${scene.id}_image` ? 'در حال بازنویسی...' : 'بازنویسی پرامپت'}
                      </button>
                    </div>
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
                        بدون نیاز به هوش مصنوعی ویدیویی
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
                          onClick={() => handleCameraEffectChange(scene.id, eff.id)}
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
                            onClick={() => copyText(scene.id, motionPrompt, 'motion')}
                            className="flex items-center gap-1 text-[11px] font-bold text-indigo-300 hover:text-white bg-indigo-600 hover:bg-indigo-500 px-2.5 py-1 rounded-md transition-all shadow-sm shadow-indigo-600/30"
                          >
                            {copiedMotionId === scene.id ? <Check className="w-3 h-3 text-emerald-300" /> : <Copy className="w-3 h-3" />}
                            {copiedMotionId === scene.id ? 'کپی شد!' : 'کپی پرامپت'}
                          </button>
                        )}

                        {motionPrompt && (
                          <button
                            onClick={() => handleSaveMotionPrompt(scene.id, motionPrompt)}
                            disabled={savingPromptId === scene.id}
                            title="ذخیره ویرایش پرامپت حرکت"
                            className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
                          >
                            <Save className={`w-3.5 h-3.5 ${savingPromptId === scene.id ? 'animate-spin' : ''}`} />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Empty Motion Prompt Generator Callout */}
                    {!motionPrompt ? (
                      <div className="p-3 rounded-lg bg-slate-950 border border-indigo-900/60 text-center space-y-2">
                        <p className="text-xs text-slate-300">
                          هنوز پرامپت حرکتی برای این هایلایت ثبت نشده است.
                        </p>
                        <button
                          type="button"
                          onClick={() => handleGenerateSingleMotion(scene.id)}
                          disabled={isRewriting === `${scene.id}_motion`}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all disabled:opacity-50"
                        >
                          <Wand2 className={`w-3.5 h-3.5 ${isRewriting === `${scene.id}_motion` ? 'animate-spin' : ''}`} />
                          {isRewriting === `${scene.id}_motion` ? 'در حال تولید پرامپت...' : 'تولید خودکار پرامپت حرکت ۲s'}
                        </button>
                      </div>
                    ) : (
                      <>
                        {/* Motion Prompt Textarea */}
                        <div className="space-y-1">
                          <label className="text-[10px] text-slate-400 font-medium block">
                            پرامپت حرکت (بازیگری بی‌صدا، بدون فلگ زمانی در متن):
                          </label>
                          <textarea
                            rows={2}
                            value={motionPrompt}
                            onChange={(e) => setEditedMotionPrompts({ ...editedMotionPrompts, [scene.id]: e.target.value })}
                            placeholder="پرامپت حرکت ۲ ثانیه‌ای برای Google Flow / Vidu..."
                            className="w-full p-2.5 rounded-lg bg-slate-950 border border-indigo-900/60 text-[11px] font-mono text-indigo-100 focus:border-indigo-400 focus:outline-none ltr-content leading-relaxed resize-y"
                          />
                        </div>

                        {/* Rewrite Box */}
                        <div className="pt-2 border-t border-indigo-900/40 space-y-1">
                          <div className="flex gap-1.5">
                            <input
                              type="text"
                              value={motionFeedback[scene.id] || ''}
                              onChange={(e) => setMotionFeedback({ ...motionFeedback, [scene.id]: e.target.value })}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') handleRewritePrompt(scene.id, 'motion');
                              }}
                              placeholder="فیدبک برای اصلاح حرکت... مثلاً: پوزخند مغرورانه‌تر"
                              className="flex-1 px-3 py-1.5 rounded-lg bg-slate-950 border border-indigo-900/60 text-xs text-slate-200 placeholder:text-slate-500 focus:border-indigo-400 focus:outline-none"
                            />
                            <button
                              type="button"
                              onClick={() => handleRewritePrompt(scene.id, 'motion')}
                              disabled={isRewriting === `${scene.id}_motion` || !motionFeedback[scene.id]?.trim()}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-bold text-[11px] shadow-sm transition-all flex-shrink-0"
                            >
                              <Sparkles className={`w-3.5 h-3.5 ${isRewriting === `${scene.id}_motion` ? 'animate-spin' : ''}`} />
                              {isRewriting === `${scene.id}_motion` ? 'در حال بازنویسی...' : 'بازنویسی'}
                            </button>
                          </div>
                        </div>
                      </>
                    )}

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
                                onChange={(e) => handleVideoUpload(scene.id, e.target.files?.[0])}
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
                              کلیپ ۴s یا ۵s دانلودی در تدوین نهایی خودکار به ۲ ثانیه اول تریم می‌شود.
                            </p>
                          </div>

                          <label className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs cursor-pointer shadow-md shadow-indigo-600/20 transition-all hover:scale-102">
                            <Upload className="w-3.5 h-3.5" />
                            <span>انتخاب فایل MP4</span>
                            <input
                              type="file"
                              accept="video/mp4,video/*"
                              className="hidden"
                              onChange={(e) => handleVideoUpload(scene.id, e.target.files?.[0])}
                            />
                          </label>

                          {uploadingVideoId === scene.id && (
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
