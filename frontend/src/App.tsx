import React, { useState } from 'react';
import { UploadPage } from './pages/UploadPage';
import { DashboardPage } from './pages/DashboardPage';
import { TZAuditResult } from './types';

function App() {
  const [auditResult, setAuditResult] = useState<TZAuditResult | null>(null);

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-200">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-md">
              A
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-800">Antigravity<span className="text-blue-600">Scorer</span></span>
          </div>
          <a href="https://github.com/ваш-профиль" target="_blank" rel="noreferrer" className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors">
            Документация
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8 text-slate-800">
        {!auditResult ? (
          <UploadPage onScoreComplete={setAuditResult} />
        ) : (
          <DashboardPage result={auditResult} onReset={() => setAuditResult(null)} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-8 text-center mt-auto">
        <p className="text-sm border-t border-slate-800 pt-8 mt-8 inline-block px-12">
          MVP Разработано за 24 часа. Используется подход In-Context Learning (Few-Shot) и Structured Outputs.
        </p>
      </footer>
    </div>
  );
}

export default App;
