import React, { useState } from 'react';
import { X, Sparkles, FolderPlus, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';
import { createNewEpisode } from '../api';

export default function NewEpisodeModal({ isOpen, onClose, onCreated }) {
  const [title, setTitle] = useState('');
  const [rawIdea, setRawIdea] = useState('');
  const [episodeId, setEpisodeId] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('لطفاً عنوان اپیزود را وارد نمایید.');
      return;
    }

    setLoading(true);
    try {
      const res = await createNewEpisode({
        title: title.trim(),
        raw_hand_or_concept: rawIdea.trim(),
        episode_id: episodeId.trim() || undefined
      });
      
      // Reset form
      setTitle('');
      setRawIdea('');
      setEpisodeId('');
      setShowAdvanced(false);
      
      onCreated(res.episode_id);
      onClose();
    } catch (err) {
      alert('خطا در ایجاد اپیزود: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <FolderPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">ایجاد اپیزود جدید در استودیو</h3>
              <p className="text-[11px] text-slate-400">یک پوشه اختصاصی با state.json و پوشه‌های مالتی‌مدیا ساخته می‌شود</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          
          {/* 1. Episode Title (عنوان اپیزود) */}
          <div className="space-y-1.5">
            <label className="text-slate-200 font-bold block">
              عنوان اپیزود (Episode Title) <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              placeholder="مثال: تراژدی پاکت شاه در برابر تک‌خال اصغر فیش"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-slate-100 text-sm focus:border-amber-500 focus:outline-none"
              required
              autoFocus
            />
          </div>

          {/* 2. Raw Poker Hand / Idea (ایده خام و شرح دست پوکر) */}
          <div className="space-y-1.5">
            <label className="text-slate-200 font-bold flex items-center gap-1.5">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              ایده خام و شرح دست پوکر (Raw Poker Hand / Idea)
            </label>
            <textarea
              rows={5}
              placeholder="شرح دست، اشتباه خنده‌دار بازیکنان، پوزیشن‌ها یا استراتژی مورد نظر را بنویسید...&#10;مثال: هیرو در پوزیشن کات‌آف با پاکت شاه (KK) سه-بت می‌زنه. اصغر فیش با A-3 آف‌سوت از بلایند کال می‌کنه. روی فلاپ آس میاد و کامبیز از خشم نمیتونه فولد بده و با آل‌آین استکش پودر میشه..."
              value={rawIdea}
              onChange={(e) => setRawIdea(e.target.value)}
              className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-700 text-slate-100 text-xs leading-relaxed focus:border-amber-500 focus:outline-none resize-y"
            />
            <p className="text-[11px] text-slate-400">
              این متن مستقیماً در کتابچه ایده ذخیره شده و در پرامپت هوش مصنوعی Google AI Studio گنجانده خواهد شد.
            </p>
          </div>

          {/* Collapsible Advanced Settings (Optional Folder ID) */}
          <div className="pt-1">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-[11px] text-slate-400 hover:text-slate-300 flex items-center gap-1 font-semibold"
            >
              {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              تنظیمات پیشرفته شناسه پوشه (اختیاری)
            </button>

            {showAdvanced && (
              <div className="mt-2 p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
                <label className="text-slate-400 text-[11px] block">
                  شناسه سفارشی پوشه (اگر خالی بگذارید به طور خودکار ساخته می‌شود):
                </label>
                <input
                  type="text"
                  placeholder="مثال: ep02-pocket-kings-tilt"
                  value={episodeId}
                  onChange={(e) => setEpisodeId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 font-mono text-xs ltr-content focus:border-amber-500 focus:outline-none"
                />
              </div>
            )}
          </div>

          {/* Submit Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition-colors"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold shadow-lg shadow-amber-500/20 transition-all hover:scale-102"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? 'در حال ساخت پوشه...' : 'ایجاد اپیزود و شروع تولید'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
