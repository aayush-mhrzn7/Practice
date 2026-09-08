/**
 * api.ts — one fetch helper for the whole UI.
 *
 * Every call attaches Authorization: Bearer <token> when localStorage has one.
 * Logout only clears that key; the JWT stays valid on the server until exp.
 *
 * 403 bodies become ApiError with status 403 so pages can show "no permission".
 * Default API origin is the uvicorn port. Change this if you bind another port.
 */

import type { TokenOut } from "./types";

const API = "http://localhost:8000";
const TOKEN_KEY = "rolekit_token";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

type ApiOptions = {
  method?: string;
  body?: unknown;
};

export type ApiResult<T> = {
  ok: true;
  status: number;
  data: T;
};

export function isApiError(err: unknown): err is ApiError {
  return err instanceof ApiError;
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
  const { method = "GET", body } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (res.status === 204) {
    return { ok: true, status: 204, data: null as T };
  }

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }

  if (!res.ok) {
    const detail = (data as { detail?: unknown } | null)?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail
              .map((item) =>
                typeof item === "object" && item && "msg" in item
                  ? String((item as { msg: unknown }).msg)
                  : JSON.stringify(item),
              )
              .join(", ")
          : "Request failed";
    throw new ApiError(res.status, message);
  }

  return { ok: true, status: res.status, data: data as T };
}

export async function login(email: string, password: string): Promise<TokenOut> {
  const { data } = await api<TokenOut>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
  return data;
}
