import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "@/lib/auth/storage";
import type { AuthTokens } from "@/lib/types";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const PUBLIC_PATHS = ["/users/login", "/users/signup", "/users/refresh"];

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

function isPublicRequest(url?: string) {
  if (!url) return false;
  return PUBLIC_PATHS.some((path) => url.includes(path));
}

export const http = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

const refreshHttp = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

http.interceptors.request.use((config) => {
  if (!isPublicRequest(config.url)) {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

let refreshQueue: Promise<string> | null = null;

function cycleRefreshToken(): Promise<string> {
  if (!refreshQueue) {
    refreshQueue = (async () => {
      const refresh_token = getRefreshToken();
      if (!refresh_token) {
        throw new Error("No refresh token");
      }
      const { data } = await refreshHttp.post<AuthTokens>("/users/refresh", {
        refresh_token,
      });
      setTokens(data.access_token, data.refresh_token);
      return data.access_token;
    })().finally(() => {
      refreshQueue = null;
    });
  }
  return refreshQueue;
}

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const status = error.response?.status;

    if (
      status !== 401 ||
      !original ||
      original._retry ||
      isPublicRequest(original.url)
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    try {
      const access = await cycleRefreshToken();
      original.headers.Authorization = `Bearer ${access}`;
      return http(original);
    } catch (refreshError) {
      clearTokens();
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
      return Promise.reject(refreshError);
    }
  },
);
