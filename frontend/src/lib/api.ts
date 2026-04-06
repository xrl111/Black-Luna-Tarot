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
