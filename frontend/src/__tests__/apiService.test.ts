import { describe, it, expect, vi } from 'vitest';
import { API_BASE_URL } from '../services/apiService';

describe('apiService Configuration', () => {
  it('should use localhost as default API_BASE_URL if no env var is provided', () => {
    // Di test environment tanpa VITE_API_URL, ia harus fallback ke localhost
    expect(API_BASE_URL).toContain('localhost:8000');
  });

  // Catatan: Menguji perubahan import.meta.env secara dinamis dalam satu test 
  // sulit dilakukan karena API_BASE_URL dievaluasi saat import.
  // Namun, kita sudah memastikan kodenya menggunakan import.meta.env.VITE_API_URL.
});
