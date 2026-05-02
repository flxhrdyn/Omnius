/**
 * API Service
 * Menggantikan geminiService.ts dengan pemanggilan ke FastAPI backend Python.
 */

import { AnalysisResult } from '../types';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

/** Header yang dikirim ke setiap endpoint yang terproteksi. */
const authHeaders = (): Record<string, string> => ({
  'Content-Type': 'application/json',
  ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
});

export interface ArticleInput {
  url?: string;
  title?: string;
  text?: string;
}

export async function analyzeNews(
  inputs: string[],
  mode: 'link' | 'manual' = 'link',
  model: string = 'llama-3.3-70b-versatile',
  onStatus?: (status: { message: string, percent: number }) => void
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
    headers: authHeaders(),
    body: JSON.stringify({ articles, model }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let resultData: AnalysisResult | null = null;

  if (!reader) throw new Error("Gagal membaca stream dari server.");

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.replace('data: ', '').trim();
        if (!jsonStr) continue;
        
        try {
          const event = JSON.parse(jsonStr);
          if (event.status === 'progress' && onStatus) {
            onStatus({ message: event.message, percent: event.percent });
          } else if (event.status === 'final_result') {
            resultData = event.data;
          } else if (event.status === 'error') {
            throw new Error(event.message);
          }
        } catch (e) {
          console.error("Error parsing SSE event:", e);
        }
      }
    }
  }

  if (!resultData) throw new Error("Analisis selesai tanpa hasil final.");
  return resultData;
}

export async function getAvailableModels(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/models`);
  if (!response.ok) {
    return ['llama-3.3-70b-versatile'];
  }
  const data = await response.json();
  return data.models as string[];
}

export async function researchNews(topic: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/research`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ topic }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Research failed');
  }

  return response.json();
}
