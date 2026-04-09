import axios from "axios";

const apiOrigin = (import.meta as any).env?.VITE_API_ORIGIN || (import.meta as any).env?.VITE_API_PROXY || "http://localhost:8000";

function normalizeOrigin(origin: string): string {
  if (!origin) return "";
  return origin.endsWith("/") ? origin.slice(0, -1) : origin;
}

const ORIGIN = normalizeOrigin(apiOrigin);

export function apiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  if (!ORIGIN) return normalizedPath;
  return `${ORIGIN}${normalizedPath}`;
}

export const axiosClient = axios.create({
  baseURL: ORIGIN || undefined,
  timeout: 120000,
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // We export the handling to components via catching, 
    // but we can globally catch 401 Unauthorized to remove token
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      // Optional: window.location.href = "/";
    }
    
    // We let components catch 429 to show their own UI, or we can use toast here
    // Currently relying on the frontend component Catch block to show notification.
    
    return Promise.reject(error);
  }
);
