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
