// Base URL picked from the CRA env var set at build time.
// In Docker we pass REACT_APP_API_URL (we recommended '/api').
export const API_BASE = process.env.REACT_APP_API_URL || "/api";

// API endpoints in one place (easy to refactor later)
export const API_ENDPOINTS = {
  health: `${API_BASE}/health`,
  upload: `${API_BASE}/documents/upload`,
  listDocs: `${API_BASE}/documents`,
  summarize: `${API_BASE}/summarize`,
};
