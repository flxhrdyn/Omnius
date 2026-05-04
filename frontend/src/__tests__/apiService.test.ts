import { describe, it, expect, vi } from 'vitest';
import { API_BASE_URL, pingHealth } from '../services/apiService';

describe('apiService', () => {
  it('should use localhost as default API_BASE_URL if no env var is provided', () => {
    expect(API_BASE_URL).toContain('localhost:8000');
  });

  it('pingHealth should call /api/health', async () => {
    // Mock global fetch
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchMock);

    await pingHealth();

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/health'),
      expect.any(Object)
    );

    vi.unstubAllGlobals();
  });
});
