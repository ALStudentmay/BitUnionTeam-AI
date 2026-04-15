import React, { useState } from 'react';
import { MessageCircle, Send, Loader2 } from 'lucide-react';
import { api } from '../api';

interface ChatPanelProps {
  tzContext: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ tzContext }) => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([
    {
      role: 'assistant',
      text: 'Задайте вопрос по вашему ТЗ: как усилить KPI, стратегические ссылки, формулировку цели и т.д.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', text }]);
    setLoading(true);
    try {
      const reply = await api.chat(text, tzContext);
      setMessages((m) => [...m, { role: 'assistant', text: reply }]);
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = ax.response?.data?.detail || ax.message || 'Ошибка чата';
      setMessages((m) => [...m, { role: 'assistant', text: `Ошибка: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col border border-slate-200 rounded-2xl bg-slate-50/80 overflow-hidden h-[min(520px,70vh)]">
      <div className="flex items-center gap-2 px-4 py-3 bg-white border-b border-slate-200">
        <MessageCircle className="w-5 h-5 text-blue-600" />
        <span className="font-semibold text-slate-800">AI-ассистент по ТЗ</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[95%] rounded-xl px-3 py-2 text-sm ${
              msg.role === 'user'
                ? 'ml-auto bg-blue-600 text-white'
                : 'mr-auto bg-white border border-slate-200 text-slate-800'
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.text}</p>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" /> Ответ…
          </div>
        )}
      </div>
      <div className="p-3 bg-white border-t border-slate-200 flex gap-2">
        <input
          className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm"
          placeholder="Ваш вопрос…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), send())}
          disabled={loading}
        />
        <button
          type="button"
          onClick={send}
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
