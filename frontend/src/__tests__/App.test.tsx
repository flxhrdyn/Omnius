import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import App from '../App';
import * as apiService from '../services/apiService';

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
global.IntersectionObserver = MockIntersectionObserver as any;

// Mock the apiService
vi.mock('../services/apiService', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/apiService')>();
  return {
    ...actual,
    pingHealth: vi.fn().mockResolvedValue({ status: 'ok' }),
  };
});

describe('App Component Pre-warming', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call pingHealth on mount to wake up the Azure backend', async () => {
    render(<App />);
    
    // Check if pingHealth was called
    expect(apiService.pingHealth).toHaveBeenCalledTimes(1);
  });
});
