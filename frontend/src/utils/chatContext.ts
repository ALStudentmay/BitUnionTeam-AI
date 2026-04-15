import type { TZAuditResult } from '../types';

/** Контекст для чат-ассистента по результатам аудита */
export function buildChatContext(result: TZAuditResult): string {
  const parts = [
    `Итог: ${result.total_score}/100, оценка ${result.grade}`,
    '',
    'Критические замечания:',
    ...(result.critical_errors.length ? result.critical_errors.map((e) => `- ${e}`) : ['- нет']),
    '',
    'Фрагмент улучшенного ТЗ:',
    result.improved_markdown.slice(0, 8000),
  ];
  return parts.join('\n');
}
