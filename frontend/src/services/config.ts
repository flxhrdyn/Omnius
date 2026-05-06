export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_KEY = import.meta.env.VITE_API_KEY || '';

export const authHeaders = () => ({
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
});
