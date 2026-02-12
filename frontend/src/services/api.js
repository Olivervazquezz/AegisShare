import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

// Attach JWT to every request automatically.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aegis_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear token and redirect to login.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('aegis_token');
      window.location.href = '/';
    }
    return Promise.reject(err);
  }
);

export default api;
