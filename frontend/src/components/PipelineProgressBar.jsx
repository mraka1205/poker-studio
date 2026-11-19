import React from 'react';
import { 
  Lightbulb, 
  BookTemplate, 
  FileText, 
  Users, 
  Mic, 
  Film, 
  Scissors, 
  Share2, 
  BarChart3, 
  CheckCircle2, 
  Clock, 
  AlertCircle 
} from 'lucide-react';

const STAGE_ICONS = {
  1: Lightbulb,
  2: BookTemplate,
  3: FileText,
  4: Users,
  5: Mic,
  6: Film,
  7: Scissors,
  8: Share2,
  9: BarChart3
};

export default function PipelineProgressBar({ 
  stages = [], 
  currentStage = 1, 
  activeViewStage = 1, 
  onSelectStage
}) {
  const defaultStages = [
    { stage_number: 1, name_fa: "ایده", name_en: "Idea", status: "approved" },
    { stage_number: 2, name_fa: "Bible", name_en: "Bible", status: "approved" },
    { stage_number: 3, name_fa: "سناریو", name_en: "Script", status: "approved" },
    { stage_number: 4, name_fa: "کاراکترها", name_en: "Characters", status: "waiting_approval" },
    { stage_number: 5, name_fa: "صدا و میکس", name_en: "Audio & Mix", status: "in_progress" },
    { stage_number: 6, name_fa: "صحنه‌ها", name_en: "Scenes", status: "in_progress" },
    { stage_number: 7, name_fa: "تدوین", name_en: "Edit", status: "pending" },
    { stage_number: 8, name_fa: "انتشار", name_en: "Publish", status: "pending" },
    { stage_number: 9, name_fa: "عددها", name_en: "Analytics", status: "pending" },
  ];

  const displayStages = stages.length > 0 ? stages : defaultStages;
  const approvedCount = displayStages.filter(s => s.status === 'approved').length;
  const progressPercent = Math.round((approvedCount / displayStages.length) * 100);

  return (
    <div className="bg-[#0f1524] border-b border-slate-800/80 px-4 py-3 sm:px-6 shadow-inner">
      <div className="max-w-7xl mx-auto">
        
        {/* Top Mini Info */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-300">مسیر تولید ۹ مرحله‌ای اپیزود:</span>
            <span className="text-xs font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
              مرحله فعال: {displayStages.find(s => s.stage_number === currentStage)?.name_fa || `مرحله ${currentStage}`}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">پیشرفت کل:</span>
              <span className="text-xs font-mono font-bold text-emerald-400">{progressPercent}%</span>
            </div>
            <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all duration-500" 
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Horizontal 9-Stage Progress Stepper */}
        <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5 sm:gap-2">
          {displayStages.map((stage) => {
            const Icon = STAGE_ICONS[stage.stage_number] || Lightbulb;
            const isCurrent = stage.stage_number === currentStage;
            const isSelected = stage.stage_number === activeViewStage;
            const isApproved = stage.status === 'approved';
            const isWaiting = stage.status === 'waiting_approval';
            const isInProgress = stage.status === 'in_progress';

            let statusBg = 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700';
            let iconColor = 'text-slate-500';

            if (isApproved) {
              statusBg = isSelected 
                ? 'bg-emerald-950/70 border-emerald-500 text-emerald-200 ring-2 ring-emerald-500/30' 
                : 'bg-emerald-950/40 border-emerald-800/80 text-emerald-300 hover:border-emerald-600';
              iconColor = 'text-emerald-400';
            } else if (isWaiting) {
              statusBg = isSelected 
                ? 'bg-purple-950/70 border-purple-400 text-purple-200 ring-2 ring-purple-500/40' 
                : 'bg-purple-950/40 border-purple-700/80 text-purple-300 hover:border-purple-500';
              iconColor = 'text-purple-400 animate-pulse';
            } else if (isInProgress) {
              statusBg = isSelected 
                ? 'bg-amber-950/70 border-amber-400 text-amber-200 ring-2 ring-amber-500/40' 
                : 'bg-amber-950/40 border-amber-700/80 text-amber-300 hover:border-amber-500';
              iconColor = 'text-amber-400';
            } else if (isSelected) {
              statusBg = 'bg-slate-800 border-slate-600 text-slate-100 ring-1 ring-slate-500';
              iconColor = 'text-slate-300';
            }

            return (
              <button
                key={stage.stage_number}
                onClick={() => onSelectStage(stage.stage_number)}
                className={`relative group p-2 rounded-xl border transition-all text-right flex flex-col justify-between ${statusBg}`}
              >
                {/* Active Indicator Pip */}
                {isCurrent && (
                  <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                  </span>
                )}

                <div className="flex items-center justify-between w-full mb-1">
                  <span className="text-[10px] font-mono font-bold text-slate-500 group-hover:text-slate-400">
                    ۰{stage.stage_number}
                  </span>
                  
                  {isApproved ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : isWaiting ? (
                    <AlertCircle className="w-3.5 h-3.5 text-purple-400" />
                  ) : isInProgress ? (
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
                  )}
                </div>

                <div className="flex items-center gap-1.5 mt-0.5">
                  <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${iconColor}`} />
                  <span className="text-xs font-bold truncate">
                    {stage.name_fa}
                  </span>
                </div>
                
                <span className="text-[9px] text-slate-500 truncate mt-0.5 ltr-content font-mono">
                  {stage.name_en}
                </span>
              </button>
            );
          })}
        </div>

      </div>
    </div>
  );
}
