import React, { useCallback, useEffect, useState } from 'react';
import { Loader2, Trash2, FileText } from 'lucide-react';
import { api, getAuthToken } from '../api';
import type { AnalysisListItem, AuditPayload } from '../types';

interface HistoryPageProps {
  onOpenAnalysis: (payload: AuditPayload) => void;
  onNeedLogin: () => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onOpenAnalysis, onNeedLogin }) => {
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    if (!getAuthToken()) {
      setLoading(false);
      setError('Войдите в аккаунт, чтобы видеть историю.');
      return;
    }
    try {
      const list = await api.listAnalyses();
      setItems(list);
    } catch {
      onNeedLogin();
      setError('Сессия истекла — войдите снова.');
    } finally {
      setLoading(false);
    }
  }, [onNeedLogin]);

  useEffect(() => {
    load();
  }, [load]);

  const open = async (id: number) => {
    try {
      const { result, filename } = await api.getAnalysis(id);
      onOpenAnalysis({ result, filename });
    } catch {
      setError('Не удалось загрузить запись');
    }
  };

  const remove = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Удалить запись?')) return;
    try {
      await api.deleteAnalysis(id);
      setItems((prev) => prev.filter((x) => x.id !== id));
    } catch {
      setError('Не удалось удалить');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">История анализов</h1>
      <p className="text-slate-600 mb-8 text-sm">Сохранённые результаты после входа в аккаунт.</p>
      {error && (
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <p className="text-red-600">{error}</p>
          <button
            type="button"
            onClick={onNeedLogin}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg"
          >
            Войти
          </button>
        </div>
      )}
      {items.length === 0 ? (
        <p className="text-slate-500">Пока нет сохранённых анализов. Загрузите ТЗ после входа — результат сохранится автоматически.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((row) => (
            <li
              key={row.id}
              className="bg-white border border-slate-200 rounded-xl p-4 flex items-center justify-between gap-4 hover:border-blue-300 cursor-pointer transition-colors"
              onClick={() => open(row.id)}
            >
              <div className="flex items-start gap-3 min-w-0">
                <FileText className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 truncate">{row.filename}</p>
                  <p className="text-xs text-slate-500">
                    {new Date(row.created_at).toLocaleString('ru-RU')} · балл {row.total_score ?? '—'} ·{' '}
                    {row.grade ?? '—'}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => remove(row.id, e)}
                className="p-2 text-slate-400 hover:text-red-600 rounded-lg"
                title="Удалить"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
