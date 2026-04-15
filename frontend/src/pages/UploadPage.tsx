import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../api';
import { TZAuditResult } from '../types';

interface UploadPageProps {
  onScoreComplete: (result: TZAuditResult) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onScoreComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressText, setProgressText] = useState<string>('');
  const [isScoringPhase, setIsScoringPhase] = useState(false);

  const loaderTexts = [
    "ИИ-эксперт изучает научную новизну...",
    "Анализируем стратегическую релевантность...",
    "Ищем критические ошибки в KPI...",
    "Оцениваем социально-экономический эффект...",
    "Генерируем идеальную версию ТЗ...",
    "Сводим финальный скоринг..."
  ];

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isScoringPhase) {
      let idx = 0;
      setProgressText(loaderTexts[idx]);
      interval = setInterval(() => {
        idx = (idx + 1) % loaderTexts.length;
        setProgressText(loaderTexts[idx]);
      }, 3500);
    }
    return () => clearInterval(interval);
  }, [isScoringPhase]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      // Шаг 1: Загрузка и парсинг
      setProgressText(`Парсинг файла ${file.name}...`);
      const parseData = await api.uploadFile(file);

      // Шаг 2: Скоринг
      setIsScoringPhase(true);
      const scoreData = await api.scoreMarkdown(parseData.markdown, parseData.filename);

      onScoreComplete(scoreData);
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || 'Произошла неизвестная ошибка при загрузке и анализе.');
      }
    } finally {
      setIsLoading(false);
      setIsScoringPhase(false);
      setProgressText('');
    }
  }, [onScoreComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    disabled: isLoading,
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
          SOTA-2026: Умный Скоринг ТЗ
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Загрузите Техническое Задание (DOCX или PDF). Нейросеть проведет полный аудит 
          по 7 критериям, найдет слабые места и предложит улучшенную версию.
        </p>
      </div>

      <div 
        {...getRootProps()} 
        className={`w-full max-w-3xl p-12 border-3 border-dashed rounded-2xl transition-all duration-200 ease-in-out cursor-pointer flex flex-col items-center justify-center bg-white shadow-sm
          ${isDragActive ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}
          ${isLoading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {isLoading ? (
          <div className="flex flex-col items-center text-blue-600">
            <Loader2 className="w-16 h-16 mb-6 animate-spin" />
            <h3 className="text-xl font-semibold mb-2">Обработка документа</h3>
            <p className="text-slate-500 text-center max-w-md">{progressText}</p>
          </div>
        ) : (
          <>
            <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-6">
              <UploadCloud className="w-10 h-10" />
            </div>
            {isDragActive ? (
              <h3 className="text-2xl font-semibold text-blue-600 mb-2">Отпустите файл здесь...</h3>
            ) : (
              <h3 className="text-2xl font-semibold text-slate-800 mb-2">
                Перетащите файл или нажмите для выбора
              </h3>
            )}
            <p className="text-slate-500 mt-2 font-medium">Поддерживаются форматы: DOCX, PDF, MD</p>
            <div className="mt-8 flex items-center gap-2 text-sm text-slate-400 bg-slate-100 px-4 py-2 rounded-full">
              <FileText className="w-4 h-4" />
              <span>Максимальный размер: 50MB</span>
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="mt-8 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start max-w-3xl w-full text-red-700 animate-in fade-in slide-in-from-bottom-4">
          <AlertCircle className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="font-semibold mb-1">Ошибка обработки</h4>
            <p className="text-sm opacity-90">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};
