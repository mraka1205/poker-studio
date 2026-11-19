import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  Play, 
  Pause, 
  Upload, 
  Check, 
  CheckCircle2 
} from 'lucide-react';
import { uploadAsset } from '../api';

export default function AudioView({
  audioData = {},
  episodeId,
  stageStatus,
  onApproveStage,
  onAudioUpdated
}) {
  const [playingTrack, setPlayingTrack] = useState(null);
  const audioRef = useRef({});
  const [uploadingSegmentId, setUploadingSegmentId] = useState(null);
  const [activeEngine, setActiveEngine] = useState('elevenlabs'); // 'elevenlabs' or 'custom_voiceover'

  useEffect(() => () => { Object.values(audioRef.current).forEach(a => a.pause()); }, []);

  const tracks = audioData?.tracks || [];

  const togglePlay = (segmentId, audioUrl) => {
    if (!audioUrl) return;
    if (playingTrack === segmentId) {
      audioRef.current[segmentId]?.pause();
      setPlayingTrack(null);
      return;
    }
    if (playingTrack && audioRef.current[playingTrack]) audioRef.current[playingTrack].pause();
    let audio = audioRef.current[segmentId];
    if (!audio || audio.dataset.src !== audioUrl) {
      audio = new Audio(audioUrl);
      audio.dataset.src = audioUrl;
      audioRef.current[segmentId] = audio;
    }
    audio.onended = () => setPlayingTrack(null);
    audio.play().catch(e => console.error('Audio playback error', e));
    setPlayingTrack(segmentId);
  };

  const handleVoiceoverUpload = async (segmentId, file) => {
    if (!file) return;
    setUploadingSegmentId(segmentId);
    try {
      const res = await uploadAsset(episodeId, 'audio', file, { segment_id: segmentId });
      if (onAudioUpdated) {
        onAudioUpdated(segmentId, res.url);
      }
    } catch (err) {
      alert('خطا در آپلود ویس‌اور: ' + err.message);
    } finally {
      setUploadingSegmentId(null);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله ۵: صداگذاری و میکس (Audio & Mix)
            </span>
            <span className="text-xs text-slate-400 font-mono">
              تعداد تراک‌ها: {tracks.length} قطعه
            </span>
          </div>
          <h2 className="text-xl font-black text-white">ضبط صدای واقعی (Voiceover) یا تولید هوش مصنوعی (ElevenLabs)</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            آوانویسی اعراب‌دار فارسی برای لهجه طبیعی و عدم گلیچ در کلمات تخصصی پوکر (فِلاپ، تِریبِت، چِک‌رِیز، آل‌آین).
          </p>
        </div>

        <div className="flex items-center gap-3">
          {stageStatus === 'approved' ? (
            <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              صدا و میکس تایید شد ✓
            </div>
          ) : (
            <button
              onClick={onApproveStage}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/20 transition-all hover:scale-105"
            >
              <Check className="w-4 h-4" />
              تایید بخش صدا (Approve Stage)
            </button>
          )}
        </div>
      </div>

      {/* Mode Switcher Banner: Custom Voiceover vs ElevenLabs */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">متد ضبط و خروجی صدا</h4>
            <p className="text-xs text-slate-400">می‌توانید صدای ضبط‌شده خودتان را بارگذاری کنید یا خروجی هوش مصنوعی را تست نمایید.</p>
          </div>
        </div>

        <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveEngine('elevenlabs')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeEngine === 'elevenlabs' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            تولید هوش مصنوعی (ElevenLabs TTS)
          </button>
          <button
            onClick={() => setActiveEngine('custom_voiceover')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeEngine === 'custom_voiceover' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            ویس‌اور استودیویی (آپلود فایل صوتی)
          </button>
        </div>
      </div>

      {/* Audio Tracks List */}
      <div className="space-y-3">
        {tracks.map((track, idx) => {
          const trackId = track.segment_id || track.id;
          const isPlaying = playingTrack === trackId;

          return (
            <div
              key={trackId || idx}
              className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              
              {/* Left/Start: Speaker & Texts */}
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-md bg-slate-800 flex items-center justify-center text-xs font-mono font-bold text-slate-400">
                    {idx + 1}
                  </span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-amber-300">
                    {track.speaker}
                  </span>
                  <span className="text-xs font-mono text-slate-500">
                    مدت: {track.duration_sec || 5} ثانیه
                  </span>
                </div>

                <div className="space-y-1">
                  <p className="text-xs text-slate-300 font-medium leading-relaxed">
                    <span className="text-slate-500 font-normal ml-1">زیرنویس:</span>
                    {track.subtitle_text}
                  </p>
                  <div className={`text-xs font-medium leading-relaxed p-2 rounded-lg transition-all ${
                    activeEngine === 'elevenlabs'
                      ? 'bg-amber-950/40 border border-amber-500/40 text-amber-200 shadow-sm'
                      : 'text-amber-200/90'
                  }`}>
                    <span className="text-amber-500/80 font-bold ml-1">متن TTS اعراب‌دار:</span>
                    {track.tts_text}
                  </div>
                </div>
              </div>

              {/* Right/End: Audio Playback & Actions */}
              <div className="flex items-center gap-3 self-end md:self-auto flex-shrink-0">
                {/* Audio Play/Pause Button */}
                <button
                  onClick={() => togglePlay(trackId, track.audio_file)}
                  disabled={!track.audio_file}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all disabled:opacity-40 ${
                    isPlaying
                      ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                  }`}
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-4 h-4" />
                      توقف پخش
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 text-emerald-400" />
                      تست صدا (Play)
                    </>
                  )}
                </button>

                {/* Upload Own Voiceover Button */}
                <label className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition-all border ${
                  activeEngine === 'custom_voiceover'
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400 shadow-lg shadow-amber-500/20'
                    : 'bg-slate-800/80 hover:bg-slate-700 border-slate-700 text-slate-200'
                }`}>
                  <Upload className={`w-3.5 h-3.5 ${activeEngine === 'custom_voiceover' ? 'text-slate-950' : 'text-amber-400'}`} />
                  <span>{uploadingSegmentId === trackId ? 'در حال آپلود...' : 'آپلود ویس'}</span>
                  <input
                    type="file"
                    accept="audio/mpeg,audio/wav,audio/x-wav,audio/mp4,audio/x-m4a,.mp3,.wav,.m4a"
                    className="hidden"
                    onChange={(e) => handleVoiceoverUpload(trackId, e.target.files?.[0])}
                  />
                </label>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
