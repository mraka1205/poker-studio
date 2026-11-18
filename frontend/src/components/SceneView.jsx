import React, { useState, useEffect, useRef } from 'react';
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
  Play,
  Sliders,
  Compass,
  FileText,
  Palette,
  Loader2,
  AlertCircle,
  Terminal,
  ChevronDown,
  ChevronUp,
  XCircle
} from 'lucide-react';
import { 
  uploadAsset, 
  uploadSceneVideo, 
  updateSceneDetails,
  triggerStoryboardGeneration,
  triggerImagesGeneration,
  triggerSceneRegeneration,
  fetchTaskStatus,
  cancelTask
} from '../api';
import { copyText as writeClipboard } from '../utils/clipboard';

const MOTION_TYPE_CONFIG = {
  slow_zoom_in: { label: '🔍 زوم آرام به داخل (Slow Push-In)', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
  fast_punch_in: { label: '⚡ زوم ضربه‌ای سریع (Punch-In)', color: 'text-rose-400 bg-rose-500/10 border-rose-500/30' },
  slow_zoom_out: { label: '🔎 زوم آرام به خارج (Pull-Out)', color: 'text-blue-400 bg-blue-500/10 border-blue-500/30' },
  pan_left_to_right: { label: '➡️ حرکت افقی چپ به راست (Pan R)', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
  pan_right_to_left: { label: '⬅️ حرکت افقی راست به چپ (Pan L)', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
  tilt_up: { label: '⬆️ حرکت عمودی به بالا (Tilt Up)', color: 'text-purple-400 bg-purple-500/10 border-purple-500/30' },
  tilt_down: { label: '⬇️ حرکت عمودی به پایین (Tilt Down)', color: 'text-purple-400 bg-purple-500/10 border-purple-500/30' },
  subtle_tilt_shake: { label: '💓 لرزش اضطراب (Subtle Shake)', color: 'text-amber-300 bg-amber-500/20 border-amber-500/40' },
  static_hold: { label: '⏸️ قاب ثابت بدون حرکت (Static Hold)', color: 'text-slate-300 bg-slate-800 border-slate-700' },
};

export default function SceneView({
  scenes = [],
  episodeId,
  stageStatus,
  onApproveStage,
  onUpdateSceneStatus,
  onSceneAssetUpdated,
  onRefresh
}) {
  // Live Antigravity Task State
  const [taskState, setTaskState] = useState({
    status: 'idle',
    task_type: 'idle',
    current_step: '',
    progress: 0,
    total_scenes: scenes.length,
    completed_scenes: 0,
    conversation_id: null,
    logs: [],
    error_message: null,
    generated_images: []
  });

  const [isTriggeringStoryboard, setIsTriggeringStoryboard] = useState(false);
  const [isTriggeringImages, setIsTriggeringImages] = useState(false);
  const [regeneratingSceneId, setRegeneratingSceneId] = useState(null);
  const [showLogs, setShowLogs] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);

  // Single card copy & upload states
  const [copiedPromptId, setCopiedPromptId] = useState(null);
  const [copiedMotionId, setCopiedMotionId] = useState(null);
  const [copiedCameraPromptId, setCopiedCameraPromptId] = useState(null);
  const [uploadingImageId, setUploadingImageId] = useState(null);
  const [uploadingVideoId, setUploadingVideoId] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Track images that failed to load to fall back to alternative paths or placeholders
  const [imgErrorMap, setImgErrorMap] = useState({});

  // Local editable motion prompts map: { [sceneId]: text }
  const [editedMotionPrompts, setEditedMotionPrompts] = useState({});
  const [savingMotionId, setSavingMotionId] = useState(null);

  // Local editable camera direction prompt map: { [sceneId]: text }
  const [editedCameraPrompts, setEditedCameraPrompts] = useState({});
  const [savingCameraPromptId, setSavingCameraPromptId] = useState(null);

  const lastImageCountRef = useRef(0);
  const onRefreshRef = useRef(onRefresh);
  useEffect(() => { onRefreshRef.current = onRefresh; });
  useEffect(() => { setImgErrorMap({}); }, [taskState.completed_scenes, taskState.status]);

  // Check initial task status on mount
  useEffect(() => {
    let mounted = true;
    async function checkInitialStatus() {
      if (!episodeId) return;
      try {
        const status = await fetchTaskStatus(episodeId);
        if (mounted) {
          setTaskState(status);
          lastImageCountRef.current = (status.generated_images || []).length;
        }
      } catch (e) {
        // Silent fail on initial poll
      }
    }
    checkInitialStatus();
    return () => { mounted = false; };
  }, [episodeId]);

  // Polling loop when task is running
  useEffect(() => {
    if (!episodeId || taskState.status !== 'running') return;
    setBannerDismissed(false);
    let failures = 0;
    const interval = setInterval(async () => {
      try {
        const status = await fetchTaskStatus(episodeId);
        failures = 0;
        setTaskState(status);
        const count = (status.generated_images || []).length;
        if (count !== lastImageCountRef.current || status.status !== 'running') {
          lastImageCountRef.current = count;
          if (onRefreshRef.current) onRefreshRef.current();
        }
      } catch (err) {
        failures += 1;
        if (failures >= 5) {
          setTaskState(prev => ({ ...prev, status: 'error', error_message: 'ارتباط با سرور قطع شد.', current_step: 'خطای ارتباط' }));
        }
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [episodeId, taskState.status]);

  const copyText = (id, text, type = 'image') => {
    if (!text) return;
    writeClipboard(text);
    if (type === 'image') {
      setCopiedPromptId(id);
      setTimeout(() => setCopiedPromptId(null), 2000);
    } else if (type === 'motion') {
      setCopiedMotionId(id);
      setTimeout(() => setCopiedMotionId(null), 2000);
    } else if (type === 'camera') {
      setCopiedCameraPromptId(id);
      setTimeout(() => setCopiedCameraPromptId(null), 2000);
    }
  };

  // Button 1: Launch Real Antigravity Background Storyboard Task
  const handleStartStoryboard = async () => {
    try {
      setIsTriggeringStoryboard(true);
      setBannerDismissed(false);
      setTaskState(prev => ({
        ...prev,
        task_type: 'storyboard',
        status: 'running',
        current_step: 'راه‌اندازی ایجنت کارگردان آنتی‌گرویتی برای نگارش استوری‌بورد...',
        error_message: null,
        progress: 5
      }));
      const res = await triggerStoryboardGeneration(episodeId);
      setTaskState(res);
    } catch (err) {
      setTaskState(prev => ({
        ...prev,
        status: 'error',
        error_message: err.message,
        current_step: 'خطا در راه‌اندازی ایجنت استوری‌بورد'
      }));
    } finally {
      setIsTriggeringStoryboard(false);
    }
  };

  // Button 2: Launch Real Antigravity Background Sequential Image Generation
  const handleStartImages = async () => {
    try {
      setIsTriggeringImages(true);
      setBannerDismissed(false);
      setTaskState(prev => ({
        ...prev,
        task_type: 'images',
        status: 'running',
        current_step: 'راه‌اندازی ایجنت تولید تصویر بومی آنتی‌گرویتی...',
        error_message: null,
        progress: 5
      }));
      const res = await triggerImagesGeneration(episodeId);
      setTaskState(res);
    } catch (err) {
      setTaskState(prev => ({
        ...prev,
        status: 'error',
        error_message: err.message,
        current_step: 'خطا در راه‌اندازی ایجنت تصویرسازی'
      }));
    } finally {
      setIsTriggeringImages(false);
    }
  };

  // Single Scene Card: Regenerate Single Frame Image
  const handleRegenerateScene = async (sceneId) => {
    try {
      setRegeneratingSceneId(sceneId);
      setBannerDismissed(false);
      setTaskState(prev => ({
        ...prev,
        task_type: 'regenerate_scene',
        target_scene_id: sceneId,
        status: 'running',
        current_step: `راه‌اندازی ایجنت برای بازسازی فریم ${sceneId}...`,
        error_message: null,
        progress: 10
      }));
      const res = await triggerSceneRegeneration(episodeId, sceneId);
      setTaskState(res);
    } catch (err) {
      setTaskState(prev => ({
        ...prev,
        status: 'error',
        error_message: err.message,
        current_step: `خطا در بازسازی فریم ${sceneId}`
      }));
    } finally {
      setRegeneratingSceneId(null);
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      if (onRefresh) {
        await onRefresh();
      }
      const status = await fetchTaskStatus(episodeId);
      setTaskState(status);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleImageUpload = async (sceneId, file) => {
    if (!file) return;
    try {
      setUploadingImageId(sceneId);
      const res = await uploadAsset(episodeId, 'scene_image', file);
      const updatedPath = res.image_path || res.asset_path || res.url;
      if (onSceneAssetUpdated) {
        onSceneAssetUpdated(sceneId, 'image_path', updatedPath);
      }
      setImgErrorMap(prev => ({ ...prev, [sceneId]: false }));
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در آپلود تصویر صحنه: ' + err.message);
    } finally {
      setUploadingImageId(null);
    }
  };

  const handleVideoUpload = async (sceneId, file) => {
    if (!file) return;
    try {
      setUploadingVideoId(sceneId);
      const res = await uploadSceneVideo(episodeId, sceneId, file);
      if (onSceneAssetUpdated) {
        onSceneAssetUpdated(sceneId, 'video_path', res.video_path || res.asset_path);
      }
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در آپلود ویدیوی صحنه: ' + err.message);
    } finally {
      setUploadingVideoId(null);
    }
  };

  const handleSaveMotionPrompt = async (sceneId, newPrompt) => {
    try {
      setSavingMotionId(sceneId);
      await updateSceneDetails(episodeId, sceneId, { motion_prompt_en: newPrompt });
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در ذخیره پرامپت حرکت: ' + err.message);
    } finally {
      setSavingMotionId(null);
    }
  };

  const handleSaveCameraPrompt = async (sceneId, newPrompt, currentCamDir) => {
    try {
      setSavingCameraPromptId(sceneId);
      const updatedDir = {
        ...(currentCamDir || {
          motion_type: 'slow_zoom_in',
          start_focus_region: 'wide framing',
          end_focus_region: 'tighter facial focus',
          zoom_intensity: 1.15,
          easing: 'smooth'
        }),
        camera_prompt_en: newPrompt
      };
      await updateSceneDetails(episodeId, sceneId, { camera_direction: updatedDir });
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      alert('خطا در ذخیره حرکت دوربین: ' + err.message);
    } finally {
      setSavingCameraPromptId(null);
    }
  };

  const handleCancelTask = async () => {
    try { await cancelTask(episodeId); } catch (err) { alert('خطا در توقف عملیات: ' + err.message); }
  };

  const isRunning = taskState.status === 'running';

  return (
    <div className="space-y-6">
      
      {/* Top Banner with Direct Antigravity CLI Execution */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-amber-500/30 shadow-2xl">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5" />
              مرحله ۶: کارگردانی یکپارچه و اجرای بومی آنتی‌گرویتی (Antigravity CLI)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              تعداد نماها: {scenes.length} کات (~۲s)
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            فرآیند دو مرحله‌ای خودکار: تولید استوری‌بورد ➔ تولید تصاویر متوالی
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
            کلیک روی دکمه‌ها مستقیماً ایجنت پس‌زمینه <span className="text-amber-300 font-bold">Antigravity CLI</span> را فراخوانی می‌کند و تصاویر فریم‌ها را بدون نیاز به کپی-پیست در پوشه پروژه ذخیره می‌سازد.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap flex-shrink-0">
          
          {/* BUTTON 1: Real Storyboard Generation */}
          <button
            onClick={handleStartStoryboard}
            disabled={isRunning || isTriggeringStoryboard}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl font-black text-xs shadow-lg transition-all hover:scale-105 active:scale-95 ${
              isRunning && taskState.task_type === 'storyboard'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500 animate-pulse cursor-wait'
                : 'bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/40 hover:border-amber-400 disabled:opacity-50 disabled:cursor-not-allowed'
            }`}
            title="اجرای مستقیم ایجنت آنتی‌گرویتی برای نوشتن پرامپت‌ها و جهت‌دهی دوربین در state.json"
          >
            {isTriggeringStoryboard || (isRunning && taskState.task_type === 'storyboard') ? (
              <>
                <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                <span>در حال نگارش استوری‌بورد...</span>
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 text-amber-400" />
                <span>📝 ۱. تولید استوری‌بورد و پرامپت‌ها</span>
              </>
            )}
          </button>

          {/* BUTTON 2: Real Sequential Images Generation */}
          <button
            onClick={handleStartImages}
            disabled={isRunning || isTriggeringImages}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl font-black text-xs shadow-xl transition-all hover:scale-105 active:scale-95 ${
              isRunning && taskState.task_type === 'images'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400 animate-pulse cursor-wait'
                : 'bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500 hover:from-emerald-400 hover:to-teal-300 text-slate-950 shadow-emerald-500/25 disabled:opacity-50 disabled:cursor-not-allowed'
            }`}
            title="اجرای مستقیم ایجنت آنتی‌گرویتی برای ساخت متوالی تصاویر با حفظ پیوستگی فریم ۱"
          >
            {isTriggeringImages || (isRunning && taskState.task_type === 'images') ? (
              <>
                <Loader2 className="w-4 h-4 text-slate-950 animate-spin" />
                <span>در حال ساخت فریم‌ها در آنتی‌گرویتی...</span>
              </>
            ) : (
              <>
                <Palette className="w-4 h-4 text-slate-950" />
                <span>🎨 ۲. تولید مستقیم تصاویر صحنه‌ها</span>
              </>
            )}
          </button>

          {/* Refresh / Sync Images Button */}
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all hover:scale-102"
            title="همگام‌سازی و بارگذاری مجدد فایل‌های تصویر از روی دیسک"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-amber-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'همگام‌سازی...' : 'همگام‌سازی ↻'}</span>
          </button>

          {/* External Link to Google Flow */}
          <a
            href="https://labs.google/fx/tools/flow"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 font-bold text-xs border border-slate-700 transition-all hover:scale-102"
            title="محیط Google Flow برای متحرک‌سازی دستی کلیپ‌های ویدیویی"
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

      {/* ======================================================== */}
      {/* LIVE ANTIGRAVITY TASK PROGRESS BANNER & LOG CONSOLE */}
      {/* ======================================================== */}
      {taskState.status !== 'idle' && !bannerDismissed && (
        <div className={`p-4 rounded-2xl border transition-all shadow-xl ${
          isRunning
            ? 'bg-slate-900/95 border-amber-500/40 shadow-amber-500/10'
            : taskState.status === 'completed'
            ? 'bg-emerald-950/40 border-emerald-500/40 shadow-emerald-500/10'
            : 'bg-rose-950/40 border-rose-500/40 shadow-rose-500/10'
        }`}>
          <div className="flex items-center justify-between gap-4 flex-wrap mb-3">
            <div className="flex items-center gap-3">
              {isRunning ? (
                <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              ) : taskState.status === 'completed' ? (
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              ) : (
                <div className="w-8 h-8 rounded-lg bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
                  <AlertCircle className="w-5 h-5" />
                </div>
              )}

              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black text-white">
                    {taskState.task_type === 'storyboard'
                      ? '📝 نگارش استوری‌بورد و پرامپت‌ها در آنتی‌گرویتی'
                      : taskState.task_type === 'images'
                      ? '🎨 تولید مستقیم تصاویر کلیدی فریم‌ها'
                      : `🔄 بازسازی فریم ${taskState.target_scene_id || ''}`}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                    isRunning 
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : taskState.status === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}>
                    {taskState.status === 'running' ? 'در حال اجرا' : taskState.status === 'completed' ? 'تکمیل شد ✓' : taskState.status === 'cancelled' ? 'لغو شد' : 'خطا'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 font-mono mt-0.5">
                  {taskState.current_step || 'در حال انجام عملیات...'}
                </p>
                {taskState.status === 'error' && taskState.error_message && (
                  <div className="mt-1.5 p-2 rounded-lg bg-rose-950/80 border border-rose-800 text-[10px] font-mono text-rose-200 whitespace-pre-wrap break-all text-start" dir="ltr">
                    {taskState.error_message}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono border border-slate-700"
              >
                <Terminal className="w-3.5 h-3.5 text-amber-400" />
                <span>لاگ ایجنت ({taskState.logs?.length || 0})</span>
                {showLogs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {isRunning && (
                <button onClick={handleCancelTask}
                  className="px-2.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-bold border border-rose-500/40">
                  توقف پایش
                </button>
              )}

              {!isRunning && (
                <button
                  onClick={() => setBannerDismissed(true)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                  title="بستن اعلان"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>پیشرفت فرآیند</span>
              <span className="text-amber-300 font-bold">
                {taskState.progress}% {taskState.task_type === 'images' && `(${taskState.completed_scenes} از ${taskState.total_scenes} فریم)`}
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
              <div 
                className={`h-full transition-all duration-500 rounded-full ${
                  taskState.status === 'completed'
                    ? 'bg-emerald-400'
                    : taskState.status === 'error'
                    ? 'bg-rose-500'
                    : 'bg-gradient-to-r from-amber-500 via-emerald-400 to-amber-400'
                }`}
                style={{ width: `${Math.max(4, Math.min(100, taskState.progress))}%` }}
              />
            </div>
          </div>

          {/* Collapsible Logs Drawer */}
          {showLogs && taskState.logs && taskState.logs.length > 0 && (
            <div className="mt-3 p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[10px] text-slate-300 max-h-48 overflow-y-auto space-y-1.5 text-start" dir="ltr">
              {taskState.logs.map((logLine, idx) => (
                <div key={idx} className="leading-relaxed text-slate-300 whitespace-pre-wrap break-all">
                  <span className="text-amber-400 mr-2 font-bold">›</span>
                  {logLine}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Grid of Storyboard Scenes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scenes.map((scene, idx) => {
          const sceneId = scene.scene_id || scene.id || `scene_${String(idx + 1).padStart(2, '0')}`;
          const isAiVideo = scene.media_type === 'ai_video' || scene.shot_mode === 'ai_video';
          const visualPrompt = scene.visual_prompt_en || scene.visual_prompt || '';
          
          // Motion Prompt State (for ai_video)
          const motionPrompt = editedMotionPrompts[sceneId] !== undefined 
            ? editedMotionPrompts[sceneId] 
            : (scene.motion_prompt_en || scene.motion_prompt || '');
          
          // Camera Direction State (for static_image)
          const cameraDir = scene.camera_direction || {};
          const motionType = cameraDir.motion_type || 'slow_zoom_in';
          const motionConfig = MOTION_TYPE_CONFIG[motionType] || MOTION_TYPE_CONFIG.slow_zoom_in;
          const cameraPrompt = editedCameraPrompts[sceneId] !== undefined
            ? editedCameraPrompts[sceneId]
            : (cameraDir.camera_prompt_en || '');

          const duration = scene.duration_sec || scene.duration || 2.0;
          const cameraAngle = scene.camera_angle || '@Room_Master';
          const tableState = scene.poker_table_state || {};
          
          // Image path resolution
          const baseImagePath = scene.image_path || scene.visual_asset || `/media/${episodeId}/assets/images/${sceneId}.png`;
          const resolvedImagePath = `${baseImagePath}${baseImagePath.includes('?') ? '&' : '?'}v=${scene.image_version || 0}`;
          const isImgError = imgErrorMap[sceneId];
          const hasImage = !isImgError && Boolean(resolvedImagePath);
          const hasVideo = Boolean(scene.video_path);
          const isCurrentRegenerating = isRunning && taskState.task_type === 'regenerate_scene' && taskState.target_scene_id === sceneId;

          return (
            <div 
              key={sceneId}
              className="flex flex-col rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl hover:border-slate-700 transition-all duration-200"
            >
              {/* Scene Card Header */}
              <div className="p-4 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <span className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 font-mono font-black text-xs flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <div>
                    <h3 className="text-sm font-black text-slate-100 flex items-center gap-1.5">
                      <span>{sceneId}</span>
                      <span className="text-[10px] text-slate-500 font-normal">| {cameraAngle}</span>
                    </h3>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono mt-0.5">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {duration}s
                      </span>
                      <span>•</span>
                      <span className="text-indigo-400">{scene.focal_character || 'All Players'}</span>
                    </div>
                  </div>
                </div>

                {/* Media Type Badge */}
                <div className="flex items-center gap-1.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 border ${
                    isAiVideo 
                      ? 'bg-purple-500/15 border-purple-500/40 text-purple-300'
                      : 'bg-amber-500/15 border-amber-500/40 text-amber-300'
                  }`}>
                    {isAiVideo ? (
                      <>
                        <Video className="w-3 h-3 text-purple-400" />
                        ویدیو هوش‌مصنوعی
                      </>
                    ) : (
                      <>
                        <ImageIcon className="w-3 h-3 text-amber-400" />
                        تصویر استاتیک
                      </>
                    )}
                  </span>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-4">
                
                {/* 1. KEYFRAME IMAGE SECTION */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="w-5 h-5 rounded-md bg-amber-500 text-slate-950 text-[11px] font-black flex items-center justify-center">
                        ۱
                      </span>
                      <span className="text-xs font-bold text-amber-300">
                        فریم کلیدی (Keyframe Image)
                      </span>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap justify-end">
                      {/* Real Rebuild Frame in Antigravity Button */}
                      <button
                        onClick={() => handleRegenerateScene(sceneId)}
                        disabled={isRunning || regeneratingSceneId === sceneId}
                        className={`flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-md transition-all shadow-sm ${
                          isCurrentRegenerating
                            ? 'bg-amber-400 text-slate-950 font-black animate-pulse cursor-wait'
                            : 'bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 disabled:opacity-50 disabled:cursor-not-allowed'
                        }`}
                        title="اجرای مستقیم ایجنت آنتی‌گرویتی برای بازسازی این فریم کلیدی"
                      >
                        {isCurrentRegenerating ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin text-slate-950" />
                            <span>در حال ساخت فریم...</span>
                          </>
                        ) : (
                          <>
                            <Bot className="w-3 h-3 text-amber-400" />
                            <span>بازسازی این تصویر</span>
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
                    </div>
                  </div>

                  {/* Image Viewer Container (9:16 Vertical Ratio) */}
                  <div className="relative aspect-[9/16] w-full max-h-64 rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center group">
                    {hasImage ? (
                      <img 
                        src={resolvedImagePath}
                        alt={`Scene ${sceneId}`}
                        onError={() => setImgErrorMap(prev => ({ ...prev, [sceneId]: true }))}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                      />
                    ) : (
                      <div className="text-center p-4 space-y-2">
                        <ImageIcon className="w-8 h-8 text-slate-600 mx-auto" />
                        <span className="text-xs font-bold text-slate-300 block">فریم کلیدی ۹:۱۶ موجود نیست</span>
                        <p className="text-[10px] text-slate-500 max-w-[200px] mx-auto leading-relaxed">
                          با کلیک روی «بازسازی این تصویر»، ایجنت آنتی‌گرویتی فریم را تولید می‌کند یا تصویر را دستی آپلود نمایید.
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
                {/* CONDITIONAL BODY: AUTOMATED CAMERA DIRECTION vs AI VIDEO */}
                {/* ======================================================== */}
                {!isAiVideo ? (
                  /* MODE A: AUTOMATED FFMPEG CAMERA DIRECTION (Ken Burns) */
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-amber-500/20 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <span className="w-5 h-5 rounded-md bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[11px] font-black flex items-center justify-center">
                          ۲
                        </span>
                        <span className="text-xs font-bold text-amber-300">
                          جهت‌دهی خودکار حرکت دوربین (FFmpeg Direction)
                        </span>
                      </div>
                      
                      {(cameraPrompt || editedCameraPrompts[sceneId] !== undefined) && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleSaveCameraPrompt(sceneId, cameraPrompt, cameraDir)}
                            disabled={savingCameraPromptId === sceneId}
                            title="ذخیره ویرایش دستور دوربین"
                            className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
                          >
                            <Save className={`w-3.5 h-3.5 ${savingCameraPromptId === sceneId ? 'animate-spin' : ''}`} />
                          </button>
                          <button
                            onClick={() => copyText(sceneId, cameraPrompt, 'camera')}
                            className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
                            title="کپی دستور دوربین"
                          >
                            {copiedCameraPromptId === sceneId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      )}
                    </div>

                    {/* AI-Determined Motion Type Badge */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className={`px-2.5 py-1 rounded-lg text-xs font-bold border flex items-center gap-1.5 ${motionConfig.color}`}>
                        <Compass className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>{motionConfig.label}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
                        {cameraDir.zoom_intensity && (
                          <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                            Zoom: {cameraDir.zoom_intensity}x
                          </span>
                        )}
                        {cameraDir.easing && (
                          <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                            Ease: {cameraDir.easing}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Focus Regions Flow */}
                    {(cameraDir.start_focus_region || cameraDir.end_focus_region) && (
                      <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-[10px] space-y-1 font-mono ltr-content">
                        {cameraDir.start_focus_region && (
                          <div className="text-slate-400 flex items-start gap-1">
                            <span className="text-amber-400 font-bold flex-shrink-0">Start:</span>
                            <span className="truncate">{cameraDir.start_focus_region}</span>
                          </div>
                        )}
                        {cameraDir.end_focus_region && (
                          <div className="text-emerald-400 flex items-start gap-1">
                            <span className="text-emerald-400 font-bold flex-shrink-0">End:</span>
                            <span className="truncate">{cameraDir.end_focus_region}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Editable Camera Direction Prompt */}
                    <div className="space-y-1">
                      <label className="text-[10px] text-slate-400 font-medium block">
                        دستور حرکت دوربین FFmpeg (تولید خودکار بر اساس کشمکش داستان - قابل ویرایش):
                      </label>
                      <textarea
                        rows={2}
                        value={cameraPrompt}
                        onChange={(e) => setEditedCameraPrompts({ ...editedCameraPrompts, [sceneId]: e.target.value })}
                        placeholder="دستور حرکت دوربین Ken Burns..."
                        className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-amber-200/90 focus:border-amber-400 focus:outline-none ltr-content leading-relaxed resize-y"
                      />
                    </div>

                    <p className="text-[10px] text-slate-500 leading-relaxed">
                      💡 در تدوین نهایی، FFmpeg تصویر فریم کلیدی بالا را به مدت ~{duration}s با مسیر، شدت و فکوس مشخص‌شده بالا متحرک می‌سازد.
                    </p>
                  </div>
                ) : (
                  /* MODE B: AI VIDEO CLIP SECTION */
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-purple-500/20 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <span className="w-5 h-5 rounded-md bg-purple-500 text-slate-950 text-[11px] font-black flex items-center justify-center">
                          ۲
                        </span>
                        <span className="text-xs font-bold text-purple-300">
                          پرامپت حرکت ویدیو (Google Flow / Runway)
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-1">
                        {(motionPrompt || editedMotionPrompts[sceneId] !== undefined) && (
                          <button
                            onClick={() => handleSaveMotionPrompt(sceneId, motionPrompt)}
                            disabled={savingMotionId === sceneId}
                            title="ذخیره ویرایش پرامپت حرکت"
                            className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
                          >
                            <Save className={`w-3.5 h-3.5 ${savingMotionId === sceneId ? 'animate-spin' : ''}`} />
                          </button>
                        )}
                        <button
                          onClick={() => copyText(sceneId, motionPrompt, 'motion')}
                          disabled={!motionPrompt}
                          className="flex items-center gap-1 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-md transition-colors disabled:opacity-40"
                          title="کپی پرامپت حرکت ویدیو"
                        >
                          {copiedMotionId === sceneId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                          <span>{copiedMotionId === sceneId ? 'کپی شد!' : 'حرکت'}</span>
                        </button>
                      </div>
                    </div>

                    {/* Editable Motion Prompt Area */}
                    <div className="relative">
                      <textarea
                        rows={3}
                        value={motionPrompt}
                        onChange={(e) => setEditedMotionPrompts({ ...editedMotionPrompts, [sceneId]: e.target.value })}
                        placeholder="پرامپت حرکت عروسک (اکشن فیزیکی و ری‌اکشن‌ها)..."
                        className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-purple-200/90 focus:border-purple-400 focus:outline-none ltr-content leading-relaxed resize-y"
                      />
                    </div>

                    {/* Video Upload & Preview Dropzone */}
                    <div className="pt-1">
                      {hasVideo ? (
                        <div className="space-y-2">
                          <video 
                            src={scene.video_path} 
                            controls 
                            className="w-full max-h-48 rounded-lg bg-black border border-slate-800"
                          />
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-emerald-400 font-bold flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              ویدیوی نهایی متصل شد
                            </span>
                            <label className="cursor-pointer text-slate-400 hover:text-slate-200 underline text-[10px]">
                              جایگزینی ویدیو
                              <input 
                                type="file" 
                                accept="video/*" 
                                className="hidden" 
                                onChange={(e) => handleVideoUpload(sceneId, e.target.files[0])}
                              />
                            </label>
                          </div>
                        </div>
                      ) : (
                        <label className="flex flex-col items-center justify-center p-3 rounded-lg border border-dashed border-slate-800 hover:border-purple-500/50 hover:bg-purple-500/5 cursor-pointer transition-colors text-center group">
                          <Upload className="w-4 h-4 text-slate-500 group-hover:text-purple-400 mb-1" />
                          <span className="text-[11px] font-bold text-slate-300 group-hover:text-purple-200">
                            {uploadingVideoId === sceneId ? 'در حال بارگذاری ویدیو...' : 'آپلود فایل ویدیوی تولیدشده (MP4)'}
                          </span>
                          <span className="text-[9px] text-slate-500">
                            کلیپ رندرشده از Google Flow یا Runway را اینجا بکشید
                          </span>
                          <input 
                            type="file" 
                            accept="video/*" 
                            className="hidden" 
                            disabled={uploadingVideoId === sceneId}
                            onChange={(e) => handleVideoUpload(sceneId, e.target.files[0])}
                          />
                        </label>
                      )}
                    </div>
                  </div>
                )}

                {/* Upload Manual Image Replacement Option */}
                <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500 border-t border-slate-800/60">
                  <span>جایگزینی دستی تصویر:</span>
                  <label className="cursor-pointer text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1">
                    <Upload className="w-3 h-3" />
                    <span>آپلود PNG/JPG</span>
                    <input 
                      type="file" 
                      accept="image/*" 
                      className="hidden" 
                      onChange={(e) => handleImageUpload(sceneId, e.target.files[0])}
                    />
                  </label>
                </div>

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
