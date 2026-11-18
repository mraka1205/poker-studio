import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  componentDidCatch(error, info) { console.error('UI crash:', error, info); }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#090D16] text-slate-100 p-6">
        <div className="max-w-lg space-y-3 text-center">
          <h1 className="text-lg font-bold">خطای غیرمنتظره در رابط کاربری</h1>
          <pre className="text-xs text-rose-300 whitespace-pre-wrap ltr-content">
            {String(this.state.error?.message || this.state.error)}
          </pre>
          <button onClick={() => window.location.reload()}
            className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold">بارگذاری مجدد</button>
        </div>
      </div>
    );
  }
}
