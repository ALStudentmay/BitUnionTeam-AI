import axios from 'axios';
import { TZAuditResult, ParseResponse } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
});

export const api = {
  uploadFile: async (file: File): Promise<ParseResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<ParseResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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
    const response = await apiClient.post<TZAuditResult>('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};
