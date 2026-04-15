import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { UploadPage } from './pages/UploadPage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HistoryPage } from './pages/HistoryPage';
import type { AuditPayload } from './types';
import { api, getAuthToken, setAuthToken } from './api';

type Page = 'upload' | 'dashboard' | 'history' | 'login' | 'register';

function App() {
  const [audit, setAudit] = useState<AuditPayload | null>(null);
  const [page, setPage] = useState<Page>('upload');
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [exampleOpen, setExampleOpen] = useState(false);
  const [exampleMd, setExampleMd] = useState<string | null>(null);
  const [exampleLoading, setExampleLoading] = useState(false);

  useEffect(() => {
    const t = getAuthToken();
    if (!t) return;
    api
      .me()
      .then((u) => setUserEmail(u.email))
      .catch(() => {
        setAuthToken(null);
        setUserEmail(null);
      });
  }, []);

  const logout = () => {
    setAuthToken(null);
    setUserEmail(null);
    setPage('upload');
  };

  const handleScoreComplete = (payload: AuditPayload) => {
    setAudit(payload);
    setPage('dashboard');
  };

  const handleOpenFromHistory = (payload: AuditPayload) => {
    setAudit(payload);
    setPage('dashboard');
  };

  const handleReset = () => {
    setAudit(null);
    setPage('upload');
  };

  const openExample = async () => {
    setExampleOpen(true);
    setExampleMd(null);
    setExampleLoading(true);
    try {
      const md = await api.exampleTz();
      setExampleMd(md);
    } catch {
      setExampleMd('Не удалось сгенерировать пример. Проверьте LLM и квоту API.');
    } finally {
      setExampleLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-200 flex flex-col">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => {
              setPage('upload');
              setAudit(null);
            }}
            className="flex items-center gap-2 text-left"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-md">
              A
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-800">
              Antigravity<span className="text-blue-600">Scorer</span>
            </span>
          </button>
          <nav className="flex items-center gap-2 sm:gap-4 text-sm">
            <button
              type="button"
              onClick={openExample}
              className="text-slate-600 hover:text-blue-700 font-medium sm:hidden text-xs"
            >
              Пример
            </button>
            <button
              type="button"
              onClick={openExample}
              className="text-slate-600 hover:text-blue-700 font-medium hidden sm:inline"
            >
              Пример ТЗ
            </button>
            <button
              type="button"
              onClick={() => setPage('history')}
              className="text-slate-600 hover:text-blue-700 font-medium"
            >
              История
            </button>
            {userEmail ? (
              <>
                <span className="text-slate-400 truncate max-w-[120px] hidden md:inline">{userEmail}</span>
                <button type="button" onClick={logout} className="text-red-600 hover:underline font-medium">
                  Выход
                </button>
              </>
            ) : (
              <>
                <button type="button" onClick={() => setPage('login')} className="text-blue-600 font-medium">
                  Вход
                </button>
                <button
                  type="button"
                  onClick={() => setPage('register')}
                  className="text-slate-600 hover:text-blue-700"
                >
                  Регистрация
                </button>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="py-8 text-slate-800 flex-1">
        {page === 'login' && (
          <LoginPage
            onSuccess={() => {
              setPage('upload');
              api.me().then((u) => setUserEmail(u.email));
            }}
            onGoRegister={() => setPage('register')}
          />
        )}
        {page === 'register' && (
          <RegisterPage
            onSuccess={() => {
              setPage('upload');
              api.me().then((u) => setUserEmail(u.email));
            }}
            onGoLogin={() => setPage('login')}
          />
        )}
        {page === 'history' && (
          <HistoryPage
            onOpenAnalysis={handleOpenFromHistory}
            onNeedLogin={() => setPage('login')}
          />
        )}
        {page === 'upload' && !audit && <UploadPage onScoreComplete={handleScoreComplete} />}
        {page === 'dashboard' && audit && (
          <DashboardPage result={audit.result} filename={audit.filename} onReset={handleReset} />
        )}
      </main>

      {exampleOpen && (
        <div
          className="fixed inset-0 z-[100] bg-black/50 flex items-center justify-center p-4"
          onClick={() => setExampleOpen(false)}
          role="presentation"
        >
          <div
            className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col shadow-2xl"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
          >
            <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-900">Пример структуры ТЗ (ИИ)</h2>
              <button type="button" className="text-slate-500 hover:text-slate-800" onClick={() => setExampleOpen(false)}>
                ✕
              </button>
            </div>
            <div className="p-6 overflow-y-auto prose prose-slate max-w-none text-sm">
              {exampleLoading && <p className="text-slate-500">Генерация…</p>}
              {exampleMd && <ReactMarkdown>{exampleMd}</ReactMarkdown>}
            </div>
          </div>
        </div>
      )}

      <footer className="bg-slate-900 text-slate-400 py-8 text-center mt-auto">
        <p className="text-sm border-t border-slate-800 pt-8 mt-8 inline-block px-12">
          MVP: LLM-аудит ТЗ, история (SQLite), чат-ассистент, пример ТЗ, итоговый отчёт.
        </p>
      </footer>
    </div>
  );
}

export default App;
