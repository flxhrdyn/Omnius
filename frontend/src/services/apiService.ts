import { API_BASE_URL, authHeaders } from './config';

/**
 * Menjalankan analisis framing pada daftar artikel (URL atau Teks Manual).
 */
export async function analyzeNews(
  items: string[],
  type: 'link' | 'manual',
  model: string,
  onStatusUpdate?: (status: { message: string; percent: number }) => void
): Promise<any> {
  const payload = {
    items: items.map((item) => ({
      type: type === 'link' ? 'url' : 'manual',
      [type === 'link' ? 'url' : 'text']: item,
    })),
    model,
  };

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Analysis failed');
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let analysisResult: any = null;

  if (!reader) throw new Error("Gagal membaca stream analisis.");

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith('data: ')) {
        const jsonStr = trimmedLine.replace('data: ', '').trim();
        if (!jsonStr) continue;

        try {
          const event = JSON.parse(jsonStr);
          if (event.status === 'progress' && onStatusUpdate) {
            onStatusUpdate({ message: event.message, percent: event.percent || 0 });
          } else if (event.status === 'final_result') {
            analysisResult = event.data;
          } else if (event.status === 'error') {
            throw new Error(event.message);
          }
        } catch (e) {
          console.error("Parse Error:", e);
        }
      }
    }
  }

  if (!analysisResult) throw new Error("Analisis selesai tanpa hasil.");
  return analysisResult;
}

/**
 * Menjalankan riset agentic untuk mencari berita berdasarkan topik.
 */
export async function researchNews(
  topic: string,
  onProgress?: (msg: string) => void
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/research`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ topic }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Research failed');
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let finalData: any = null;

  if (!reader) throw new Error("Gagal membaca stream riset.");

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith('data: ')) {
        const jsonStr = trimmedLine.replace('data: ', '').trim();
        if (!jsonStr) continue;

        try {
          const event = JSON.parse(jsonStr);
          if (event.status === 'progress' && onProgress) {
            onProgress(event.message);
          } else if (event.status === 'final_result') {
            finalData = event.data;
          } else if (event.status === 'error') {
            throw new Error(event.message);
          }
        } catch (e) {
          console.error("Parse Error:", e);
        }
      }
    }
  }

  if (!finalData) throw new Error("Riset selesai tanpa hasil.");
  return finalData;
}

/**
 * Mengirimkan ping ke endpoint health untuk membangunkan container Azure (Pre-warming).
 */
export async function pingHealth(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/api/health`, {
      headers: authHeaders(),
    });
  } catch (error) {
    console.warn('Ping failed', error);
  }
}
