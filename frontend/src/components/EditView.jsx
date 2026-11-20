import React, { useState } from 'react';
import { 
  Terminal, 
  Check, 
  Copy, 
  FileText, 
  CheckCircle2, 
  Video, 
  Type 
} from 'lucide-react';
import { generateSubtitles, fetchFfmpegCommand } from '../api';
import { copyText as writeClipboard } from '../utils/clipboard';

export default function EditView({
  editData = {},
  episodeId,
  stageStatus,
  onApproveStage
}) {
  const [srtOutput, setSrtOutput] = useState(null);
  const [ffmpegCmd, setFfmpegCmd] = useState(null);
  const [sceneClipCmds, setSceneClipCmds] = useState([]);
  const [copiedClipId, setCopiedClipId] = useState(null);
  const [loadingSrt, setLoadingSrt] = useState(false);
  const [loadingFfmpeg, setLoadingFfmpeg] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState(false);
  const [copiedSrt, setCopiedSrt] = useState(false);

  const subConfig = editData?.subtitle_settings || {
    font: 'Vazirmatn',
    font_size: 42,
    direction: 'rtl',
    libass_harfbuzz: true
  };

  const handleGenerateSrt = async () => {
    setLoadingSrt(true);
    try {
      const res = await generateSubtitles(episodeId, false);
      setSrtOutput(res.srt_content);
    } catch (err) {
      alert('خطا در تولید فایل زیرنویس: ' + err.message);
    } finally {
      setLoadingSrt(false);
    }
  };

  const handleFetchFfmpeg = async () => {
    setLoadingFfmpeg(true);
    try {
      const res = await fetchFfmpegCommand(episodeId);
      setFfmpegCmd(res.ffmpeg_command);
      setSceneClipCmds(res.scene_clip_commands || []);
    } catch (err) {
      alert('خطا در دریافت دستور FFmpeg: ' + err.message);
    } finally {
      setLoadingFfmpeg(false);
    }
  };

  const copyToClipboard = (text, setFlag) => {
    writeClipboard(text);
    setFlag(true);
    setTimeout(() => setFlag(false), 2000);
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۶: تدوین و زیرنویس فارسی (Edit & RTL Subtitles)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              موتور رندر: FFmpeg + libass + HarfBuzz
            </span>
          </div>
          <h2 className="text-xl font-black text-white">پیکربندی فونت وزیرمتن و خط فارسی بدون قطعی حروف</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            تضمین چسبیدگی و اتصال صحیح حروف فارسی در فیلتر ساب‌تایتل FFmpeg و عدم برعکس شدن کلمات تخصصی پوکر.
          </p>
        </div>

        {stageStatus === 'approved' ? (
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            تدوین تایید شد ✓
          </div>
        ) : (
          <button
            onClick={onApproveStage}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/20 transition-all hover:scale-105"
          >
            <Check className="w-4 h-4" />
            تایید مرحله تدوین (Approve Stage)
          </button>
        )}
      </div>

      {/* Subtitle RTL Engine Specs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-medium">فونت استاندارد فارسی</div>
          <div className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Type className="w-4 h-4 text-amber-400" />
            {subConfig.font || 'Vazirmatn'}
          </div>
          <div className="text-[11px] text-slate-500">حروف‌چینی خوانا برای موبایل (سایز {subConfig.font_size || 42})</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-medium">موتور تصحیح دوجهته (Bidi Shaping)</div>
          <div className="text-base font-bold text-emerald-400 font-mono">
            libass (HarfBuzz RTL)
          </div>
          <div className="text-[11px] text-slate-500">جلوگیری از گسستگی و معکوس شدن عبارات فارسی/انگلیسی</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-medium">ابعاد و موقعیت زیرنویس</div>
          <div className="text-base font-bold text-amber-400 font-mono">
            1080x1920 (9:16)
          </div>
          <div className="text-[11px] text-slate-500">Alignment=2 (پایین وسط، فاصله حاشیه عمودی ۱۱۰ پیکسل)</div>
        </div>
      </div>

      {/* Live Preview Box of Subtitle Styling */}
      <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-950 to-[#041a13] border border-emerald-900/60 relative overflow-hidden flex flex-col items-center justify-center min-h-[200px] shadow-2xl">
        <div className="absolute top-3 right-3 text-[11px] font-mono text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded-md border border-emerald-800">
          نمای آزمایشی زیرنویس ویدیویی (Preview Mock)
        </div>

        <div className="text-center space-y-3 max-w-lg mt-4">
          <p className="text-2xl font-black text-white leading-relaxed drop-shadow-[0_4px_10px_rgba(0,0,0,0.9)] tracking-wide">
            فکر کردی با دست <span className="text-amber-400 font-extrabold px-1.5 py-0.5 rounded bg-black/40 border border-amber-400/40">آس و شاه (AK)</span> شدی پادشاه کل کازینو؟
          </p>
          <span className="inline-block text-xs text-emerald-300 font-mono bg-black/50 px-3 py-1 rounded-full border border-emerald-500/30">
            [Vazirmatn • RTL Connected • Safe Margin 110px]
          </span>
        </div>
      </div>

      {/* Action Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={handleGenerateSrt}
          disabled={loadingSrt}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition-all hover:scale-102"
        >
          <FileText className="w-4 h-4" />
          {loadingSrt ? 'در حال تولید...' : 'تولید فایل زیرنویس فارسی (.SRT)'}
        </button>

        <button
          onClick={handleFetchFfmpeg}
          disabled={loadingFfmpeg}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-colors"
        >
          <Terminal className="w-4 h-4 text-emerald-400" />
          {loadingFfmpeg ? 'در حال دریافت...' : 'دریافت دستور رندر نهایی FFmpeg'}
        </button>
      </div>

      {/* FFmpeg Command Terminal Box */}
      {ffmpegCmd && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5" />
              دستور آماده اجرای رندر ویدیوی نهایی (FFmpeg CLI):
            </span>

            <button
              onClick={() => copyToClipboard(ffmpegCmd, setCopiedCmd)}
              className="flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300"
            >
              {copiedCmd ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copiedCmd ? 'کپی شد!' : 'کپی دستور'}
            </button>
          </div>

          <pre className="p-3.5 rounded-lg bg-black text-xs font-mono text-emerald-300 ltr-content overflow-x-auto whitespace-pre-wrap leading-relaxed select-all">
            {ffmpegCmd}
          </pre>
        </div>
      )}

      {/* Per-Scene Ken Burns Commands */}
      {sceneClipCmds.length > 0 && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
              <Video className="w-3.5 h-3.5" />
              دستورات رندر کلیپ‌های حرکتی صحنه‌ها (Ken Burns Clips):
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              {sceneClipCmds.length} صحنه
            </span>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {sceneClipCmds.map((clip) => (
              <div key={clip.scene_id} className="p-2.5 rounded-lg bg-black/60 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold text-slate-300">
                    {clip.scene_id}
                  </span>
                  <button
                    onClick={() => {
                      copyToClipboard(clip.command, () => {});
                      setCopiedClipId(clip.scene_id);
                      setTimeout(() => setCopiedClipId(null), 2000);
                    }}
                    className="flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                  >
                    {copiedClipId === clip.scene_id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedClipId === clip.scene_id ? 'کپی شد!' : 'کپی'}
                  </button>
                </div>
                <pre className="text-[10px] font-mono text-slate-300 ltr-content overflow-x-auto whitespace-pre-wrap select-all">
                  {clip.command}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated SRT Content Viewer */}
      {srtOutput && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-amber-400" />
              محتوای فایل تولید شده: <code className="text-amber-400">projects/{episodeId}/exports/persian_subtitles.srt</code>
            </span>

            <button
              onClick={() => copyToClipboard(srtOutput, setCopiedSrt)}
              className="flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300"
            >
              {copiedSrt ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copiedSrt ? 'کپی شد!' : 'کپی متن SRT'}
            </button>
          </div>

          <pre className="p-3.5 rounded-lg bg-black text-xs font-mono text-slate-300 overflow-x-auto max-h-64 whitespace-pre-wrap leading-relaxed select-all">
            {srtOutput}
          </pre>
        </div>
      )}

    </div>
  );
}
