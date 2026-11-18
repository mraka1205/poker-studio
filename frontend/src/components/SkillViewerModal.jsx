import React, { useState, useEffect } from 'react';
import { X, BookOpen, FileText, Check, Copy } from 'lucide-react';
import { fetchSkills, fetchSkillDetail } from '../api';

export default function SkillViewerModal({ isOpen, onClose }) {
  const [skills, setSkills] = useState([]);
  const [activeSkill, setActiveSkill] = useState(null);
  const [skillContent, setSkillContent] = useState('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSkills()
        .then(data => {
          setSkills(data.skills || []);
          if (data.skills && data.skills.length > 0) {
            loadSkillContent(data.skills[0].filename);
          }
        })
        .catch(err => console.error('Failed to load skills list', err));
    }
  }, [isOpen]);

  const loadSkillContent = (filename) => {
    setActiveSkill(filename);
    setLoading(true);
    fetchSkillDetail(filename)
      .then(data => {
        setSkillContent(data.content || '');
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load skill detail', err);
        setLoading(false);
      });
  };

  const copyContent = () => {
    navigator.clipboard.writeText(skillContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-4xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">کتابخانه مهارت‌های هوش مصنوعی (.agent/skills)</h3>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyContent}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'کپی شد!' : 'کپی کل متن مهارت'}
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          
          {/* Skills Sidebar */}
          <div className="w-full md:w-64 border-b md:border-b-0 md:border-l border-slate-800 bg-slate-950/40 p-3 space-y-1.5 overflow-y-auto">
            <div className="text-[11px] font-bold text-slate-400 px-2 py-1 uppercase tracking-wider">
              فایل‌های مهارت استودیو
            </div>
            {skills.map((s) => (
              <button
                key={s.filename}
                onClick={() => loadSkillContent(s.filename)}
                className={`w-full text-right px-3 py-2.5 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
                  activeSkill === s.filename
                    ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <FileText className="w-4 h-4 flex-shrink-0 text-amber-400/80" />
                <span className="truncate">{s.filename}</span>
              </button>
            ))}
          </div>

          {/* Markdown Content Viewer */}
          <div className="flex-1 p-5 overflow-y-auto bg-[#070b13]">
            {loading ? (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                در حال بارگذاری راهنمای مهارت...
              </div>
            ) : (
              <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap leading-relaxed select-all">
                {skillContent}
              </pre>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
