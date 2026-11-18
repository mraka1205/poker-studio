import React, { useState } from 'react';
import { 
  Share2, 
  BarChart3, 
  Copy, 
  Check, 
  CheckCircle2, 
  Instagram, 
  Youtube, 
  TrendingUp, 
  Eye, 
  Clock 
} from 'lucide-react';

export default function PublishView({
  publishData = {},
  analyticsData = {},
  stageNumber = 8,
  stageStatus,
  onApproveStage
}) {
  const [copiedCaption, setCopiedCaption] = useState(false);
  const [copiedTags, setCopiedTags] = useState(false);

  const copyToClipboard = (text, setFlag) => {
    navigator.clipboard.writeText(text);
    setFlag(true);
    setTimeout(() => setFlag(false), 2000);
  };

  const isPublish = stageNumber === 8;

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-full">
              مرحله {stageNumber}: {isPublish ? 'انتشار و توزیع محتوا (Publish)' : 'تحلیل عددها و بازخورد (Analytics)'}
            </span>
          </div>
          <h2 className="text-xl font-black text-white">
            {isPublish ? 'کپشن، هشتگ‌ها و ایده تامبنیل یوتیوب و اینستاگرام' : 'پایش نرخ نگه‌داشت (Audience Retention) و بازخورد مخاطبان'}
          </h2>
        </div>

        {stageStatus === 'approved' ? (
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            این مرحله تایید شد ✓
          </div>
        ) : (
          <button
            onClick={onApproveStage}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-black shadow-lg shadow-amber-500/20 transition-all"
          >
            <Check className="w-4 h-4" />
            تایید مرحله (Approve)
          </button>
        )}
      </div>

      {isPublish ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Caption Box */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Instagram className="w-4 h-4 text-rose-400" />
                کپشن آماده انتشار
              </h3>

              <button
                onClick={() => copyToClipboard(publishData.caption_fa || '', setCopiedCaption)}
                className="flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300"
              >
                {copiedCaption ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedCaption ? 'کپی شد!' : 'کپی کپشن'}
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
              {publishData.caption_fa || 'کپشن هنوز نوشته نشده است.'}
            </div>

            {/* Hashtags */}
            <div className="space-y-1.5 pt-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>هشتگ‌های پربازدید:</span>
                <button
                  onClick={() => copyToClipboard((publishData.hashtags || []).join(' '), setCopiedTags)}
                  className="text-amber-400 hover:text-amber-300 font-semibold"
                >
                  {copiedTags ? 'کپی شد!' : 'کپی هشتگ‌ها'}
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {(publishData.hashtags || []).map((tag, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-amber-400/90 font-medium">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Thumbnail Concept Box */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Youtube className="w-4 h-4 text-red-500" />
              ایده تامبنیل شوکه‌کننده (High CTR Concept)
            </h3>

            <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/30 text-xs text-red-200 leading-relaxed">
              {publishData.thumbnail_concept || 'تصویر میمیک اغراق‌شده از چهره شکست‌خورده کاراکتر'}
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300">پلتفرم‌های مقصد:</h4>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <Youtube className="w-4 h-4 text-red-400" />
                  YouTube Shorts (9:16)
                </span>
                <span className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <Instagram className="w-4 h-4 text-pink-400" />
                  Instagram Reels (9:16)
                </span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-xs text-slate-400">تخمین بازدید (Target Views)</div>
            <div className="text-2xl font-black text-amber-400 font-mono">
              {analyticsData.target_views ? Number(analyticsData.target_views).toLocaleString('fa-IR') : '۵۰,۰۰۰'}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-xs text-slate-400">هدف ماندگاری در ۳۰ ثانیه</div>
            <div className="text-2xl font-black text-emerald-400 font-mono">
              {analyticsData.retention_at_30s || '۷۰٪'}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-xs text-slate-400">نرخ کلیک به نمایش (CTR)</div>
            <div className="text-2xl font-black text-indigo-400 font-mono">
              {analyticsData.click_through_rate || '۸.۵٪'}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-xs text-slate-400">نرخ تعامل (Engagement)</div>
            <div className="text-2xl font-black text-rose-400 font-mono">
              {analyticsData.engagement_rate || '۱۲٪'}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
