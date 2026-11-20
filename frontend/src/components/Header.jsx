import React from 'react';
import { Sparkles, BookOpen, Layers, ChevronDown, Plus } from 'lucide-react';

export default function Header({
  projects,
  currentEpisodeId,
  onSelectEpisode,
  onOpenNewModal,
  onOpenSkillsModal,
  onOpenUniverseModal,
  currentTab,
  onSelectTab
}) {
  return (
    <header className="sticky top-0 z-40 bg-[#0c111e]/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-amber-500/20 text-white font-black text-xl">
            🃏
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-tight">استودیو کمدی و آموزش پوکر</h1>
              <span className="text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                معماری بومی Antigravity
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">پایپ‌لاین تولید مستقیم عامل هوشمند Antigravity</p>
          </div>
        </div>

        {/* Center Nav Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => onSelectTab('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              currentTab === 'dashboard'
                ? 'bg-amber-500 text-slate-950 shadow-md font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            استودیو امروز
          </button>

          <button
            onClick={() => onSelectTab('stages')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              currentTab === 'stages'
                ? 'bg-amber-500 text-slate-950 shadow-md font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            مراحل تولید (۸ مرحله)
          </button>
        </nav>

        {/* Episode Selector & Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Episode Dropdown */}
          <div className="relative">
            <select
              value={currentEpisodeId || ''}
              onChange={(e) => onSelectEpisode(e.target.value)}
              className="appearance-none bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs font-medium rounded-xl pr-3 pl-8 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 max-w-[180px] sm:max-w-[210px] truncate cursor-pointer"
            >
              {projects.map((p) => (
                <option key={p.episode_id} value={p.episode_id}>
                  {p.title}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Channel Universe Modal Button */}
          <button
            onClick={onOpenUniverseModal}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500/20 to-purple-500/20 hover:from-amber-500/30 hover:to-purple-500/30 border border-amber-500/30 text-xs font-bold text-amber-300 transition-all hover:scale-105"
            title="میز همیشگی (@PokerRoom) و بانک کاراکترهای ثابت کانال"
          >
            <span>🎭</span>
            <span className="hidden sm:inline">دنیای کانال</span>
          </button>

          {/* New Episode Button */}
          <button
            onClick={onOpenNewModal}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white transition-colors"
            title="ایجاد اپیزود جدید"
          >
            <Plus className="w-4 h-4" />
          </button>

          {/* Skills Instruction Templates */}
          <button
            onClick={onOpenSkillsModal}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-200 transition-colors"
            title="مشاهده الگوهای دستورالعمل مهارت‌ها"
          >
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">مهارت‌ها</span>
          </button>
        </div>
      </div>
    </header>
  );
}
