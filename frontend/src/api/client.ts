import axios from 'axios';

const baseURL = (window as any).HICCUP_CONFIG?.API_BASE_URL || 'http://localhost:7410';

export const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('hiccup_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default api;
