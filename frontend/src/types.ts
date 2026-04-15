export interface TCriterion {
  name: string;
  score: number;
  max_score: number;
  reasoning: string;
}

export interface TZAuditResult {
  total_score: number;
  grade: string;
  criteria: TCriterion[];
  critical_errors: string[];
  strengths: string[];
  improved_markdown: string;
}

export interface ParseResponse {
  filename: string;
  markdown: string;
  char_count: number;
  word_count: number;
}

/** Результат анализа + имя файла для отчёта и истории */
export interface AuditPayload {
  result: TZAuditResult;
  filename: string;
}

export interface UserInfo {
  id: number;
  email: string;
}

export interface AnalysisListItem {
  id: number;
  filename: string;
  created_at: string;
  total_score: number | null;
  grade: string | null;
}
