import React, { useState } from 'react';
import { api, setAuthToken } from '../api';

interface LoginPageProps {
  onSuccess: () => void;
  onGoRegister: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess, onGoRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token } = await api.login(email, password);
      setAuthToken(access_token);
      onSuccess();
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string } } };
      setError(ax.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Вход</h1>
      <p className="text-slate-600 mb-8 text-sm">История анализов доступна после входа.</p>
      <form onSubmit={submit} className="space-y-4 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email"
            required
            className="w-full border border-slate-300 rounded-lg px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Пароль</label>
          <input
            type="password"
            required
            className="w-full border border-slate-300 rounded-lg px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '…' : 'Войти'}
        </button>
        <button type="button" onClick={onGoRegister} className="w-full text-sm text-blue-600 hover:underline">
          Регистрация
        </button>
      </form>
    </div>
  );
};
