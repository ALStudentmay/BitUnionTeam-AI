import axios from 'axios';
import type {
  AnalysisListItem,
  AuditPayload,
  ParseResponse,
  TZAuditResult,
  UserInfo,
} from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TOKEN_KEY = 'auth_token';

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export const apiClient = axios.create({
  baseURL: API_URL,
});

apiClient.interceptors.request.use((config) => {
  const t = getAuthToken();
  if (t) {
    config.headers.Authorization = `Bearer ${t}`;
  }
  return config;
});

export const api = {
  uploadFile: async (file: File): Promise<ParseResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<ParseResponse>('/api/upload', formData);
    return response.data;
  },

  scoreMarkdown: async (markdown: string, filename: string): Promise<TZAuditResult> => {
    const response = await apiClient.post<TZAuditResult>('/api/score', {
      markdown,
      filename,
    });
    return response.data;
  },

  analyzeFile: async (file: File): Promise<TZAuditResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<TZAuditResult>('/api/analyze', formData);
    return response.data;
  },

  register: async (email: string, password: string): Promise<{ access_token: string }> => {
    const r = await apiClient.post<{ access_token: string }>('/api/auth/register', {
      email,
      password,
    });
    return r.data;
  },

  login: async (email: string, password: string): Promise<{ access_token: string }> => {
    const r = await apiClient.post<{ access_token: string }>('/api/auth/login', {
      email,
      password,
    });
    return r.data;
  },

  me: async (): Promise<UserInfo> => {
    const r = await apiClient.get<UserInfo>('/api/auth/me');
    return r.data;
  },

  saveAnalysis: async (payload: AuditPayload): Promise<void> => {
    await apiClient.post('/api/analyses', {
      filename: payload.filename,
      result: payload.result,
    });
  },

  listAnalyses: async (): Promise<AnalysisListItem[]> => {
    const r = await apiClient.get<AnalysisListItem[]>('/api/analyses');
    return r.data;
  },

  getAnalysis: async (id: number): Promise<{ result: TZAuditResult; filename: string }> => {
    const r = await apiClient.get<{
      id: number;
      filename: string;
      created_at: string;
      result: TZAuditResult;
    }>(`/api/analyses/${id}`);
    return { result: r.data.result, filename: r.data.filename };
  },

  deleteAnalysis: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/analyses/${id}`);
  },

  chat: async (message: string, tzContext?: string): Promise<string> => {
    const r = await apiClient.post<{ reply: string }>('/api/chat', {
      message,
      tz_context: tzContext || null,
    });
    return r.data.reply;
  },

  exampleTz: async (topic?: string): Promise<string> => {
    const r = await apiClient.post<{ markdown: string }>('/api/example-tz', { topic: topic || null });
    return r.data.markdown;
  },

  buildReportMarkdown: async (filename: string, result: TZAuditResult): Promise<string> => {
    const r = await apiClient.post<{ markdown: string }>('/api/report/build', {
      filename,
      result,
    });
    return r.data.markdown;
  },
};
