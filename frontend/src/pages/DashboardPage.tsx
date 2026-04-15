import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ArrowLeft, AlertTriangle, CheckCircle, FileCheck, Layers, Sparkles, Download } from 'lucide-react';
import { TZAuditResult } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';
import { CriteriaRadar } from '../components/CriteriaRadar';

interface DashboardPageProps {
  result: TZAuditResult;
  onReset: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ result, onReset }) => {
  const [activeTab, setActiveTab] = useState<'criteria' | 'errors' | 'improvements'>('criteria');

  // Определяем цвет градиента для верхней панели в зависимости от оценки
  let gradientBanner = 'from-red-500 to-rose-600';
  if (result.grade === 'A' || result.grade === 'B') gradientBanner = 'from-green-500 to-emerald-600';
  else if (result.grade === 'C') gradientBanner = 'from-yellow-500 to-orange-500';

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([result.improved_markdown], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = "Улучшенное_ТЗ.md";
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-in fade-in duration-500">
      {/* Header */}
      <button 
        onClick={onReset}
        className="flex items-center text-slate-500 hover:text-slate-800 transition-colors mb-6 font-medium"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Загрузить другой файл
      </button>

      {/* Main Score Banner */}
      <div className={`rounded-3xl bg-gradient-to-r ${gradientBanner} p-1 md:p-8 text-white shadow-xl mb-8 flex flex-col md:flex-row items-center justify-between overflow-hidden relative`}>
        <div className="absolute inset-0 bg-white/10 opacity-50 backdrop-blur-2xl"></div>
        <div className="relative z-10 p-6 md:p-0 flex-1">
          <h1 className="text-3xl md:text-5xl font-bold mb-4">Результат аудита</h1>
          <p className="text-white/80 text-lg max-w-xl">
            Нейросеть проанализировала ваше Техническое Задание по 7 системным критериям. 
            Исправьте критические ошибки для повышения шансов на одобрение.
          </p>
          <div className="mt-6 inline-flex items-center bg-white/20 px-4 py-2 rounded-full backdrop-blur-md">
            <span className="font-semibold mr-2">Оценка:</span>
            <span className="text-2xl font-black">{result.grade}</span>
          </div>
        </div>
        <div className="relative z-10 bg-white rounded-3xl p-6 shadow-2xl flex-shrink-0 mx-6 md:mx-0 mb-6 md:mb-0">
          <ScoreGauge score={result.total_score} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Radar Chart */}
        <div className="col-span-1 lg:col-span-1 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <h3 className="text-xl font-bold flex items-center text-slate-800 mb-6">
            <Layers className="w-5 h-5 mr-3 text-blue-500" />
            Баланс критериев
          </h3>
          <CriteriaRadar criteria={result.criteria} />
        </div>

        {/* Info & Strengths tabs */}
        <div className="col-span-1 lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
          <div className="flex border-b border-slate-100 bg-slate-50/50">
            <button 
              onClick={() => setActiveTab('criteria')}
              className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors border-b-2 
                ${activeTab === 'criteria' ? 'border-blue-500 text-blue-700 bg-white' : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'}`}
            >
              <div className="flex items-center justify-center">
                <FileCheck className="w-4 h-4 mr-2" />
                Оценки и логика
              </div>
            </button>
            <button 
              onClick={() => setActiveTab('errors')}
              className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors border-b-2 flex items-center justify-center
                ${activeTab === 'errors' ? 'border-red-500 text-red-700 bg-white' : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'}`}
            >
               <AlertTriangle className="w-4 h-4 mr-2" />
                Критические ошибки
                <span className="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-xs">{result.critical_errors.length}</span>
            </button>
            <button 
              onClick={() => setActiveTab('improvements')}
              className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors border-b-2 flex items-center justify-center
                ${activeTab === 'improvements' ? 'border-green-500 text-green-700 bg-white' : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'}`}
            >
               <Sparkles className="w-4 h-4 mr-2" />
                Сгенерированное ТЗ
            </button>
          </div>

          <div className="p-6 flex-1 overflow-y-auto max-h-[600px] custom-scrollbar">
            {/* Tab: Criteria */}
            {activeTab === 'criteria' && (
              <div className="space-y-4">
                {result.criteria.map((c, idx) => (
                  <div key={idx} className="bg-slate-50 rounded-xl p-5 border border-slate-100">
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-bold text-slate-800 text-lg">{c.name}</h4>
                      <div className={`px-3 py-1 rounded-full text-sm font-bold flex-shrink-0
                        ${(c.score/c.max_score) >= 0.8 ? 'bg-green-100 text-green-700' : 
                          (c.score/c.max_score) >= 0.5 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                        {c.score} / {c.max_score}
                      </div>
                    </div>
                    <p className="text-slate-600 text-sm leading-relaxed">{c.reasoning}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab: Errors */}
            {activeTab === 'errors' && (
               <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center">
                    <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                    Что нужно исправить
                  </h3>
                  {result.critical_errors.length > 0 ? (
                    <ul className="space-y-3">
                      {result.critical_errors.map((err, idx) => (
                        <li key={idx} className="flex items-start bg-red-50 p-4 rounded-xl border border-red-100">
                           <span className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0 mt-0.5">{idx + 1}</span>
                           <span className="text-red-900 leading-tight pt-0.5">{err}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="bg-green-50 p-6 rounded-xl border border-green-100 text-center">
                      <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                      <p className="font-medium text-green-800">Критических ошибок не найдено! Отличная работа.</p>
                    </div>
                  )}
                </div>

                <div className="pt-6 border-t border-slate-100">
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Сильные стороны
                  </h3>
                   <ul className="space-y-3">
                      {result.strengths.map((str, idx) => (
                        <li key={idx} className="flex items-start">
                           <CheckCircle className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                           <span className="text-slate-700 leading-tight pt-0.5">{str}</span>
                        </li>
                      ))}
                    </ul>
                </div>
               </div>
            )}

            {/* Tab: Improvements */}
            {activeTab === 'improvements' && (
              <div className="prose prose-slate max-w-none prose-headings:text-slate-800 prose-a:text-blue-600 hover:prose-a:text-blue-500 relative">
                 <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-xl gap-4">
                    <p className="text-blue-800 font-medium m-0 flex items-center">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Ниже представлена сгенерированная AI улучшенная версия проблемных разделов ТЗ.
                    </p>
                    <button 
                      onClick={handleDownload}
                      className="flex items-center whitespace-nowrap bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Скачать файл (.md)
                    </button>
                 </div>
                 <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-inner">
                  <ReactMarkdown>{result.improved_markdown}</ReactMarkdown>
                 </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
