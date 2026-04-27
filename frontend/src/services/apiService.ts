/**
 * API Service
 * Menggantikan geminiService.ts dengan pemanggilan ke FastAPI backend Python.
 */

import { AnalysisResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ArticleInput {
  url?: string;
  title?: string;
  text?: string;
}

export async function analyzeNews(
  inputs: string[],
  mode: 'link' | 'manual' = 'link',
  model: string = 'llama-3.3-70b-versatile'
): Promise<AnalysisResult> {
  const articles: ArticleInput[] = inputs.map((input) => {
    if (mode === 'link') {
      return { url: input };
    } else {
      return { text: input };
    }
  });

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ articles, model }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  const data: AnalysisResult = await response.json();
  return data;
}

export async function getAvailableModels(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/models`);
  if (!response.ok) {
    return ['llama-3.3-70b-versatile'];
  }
  const data = await response.json();
  return data.models as string[];
}
