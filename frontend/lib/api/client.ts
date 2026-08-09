import type { User } from "@/lib/types";

/** Same-origin proxy via next.config rewrites → backend :8000 (avoids CORS). */
const API_BASE_URL =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE_URL) ||
  "";

export const AUTH_STORAGE_KEY = "auth_session";

export type AccountType = "org_user" | "superadmin";

export type SessionUser = Pick<User, "id" | "name" | "email" | "role"> & {
  accountType: AccountType;
};

export interface AuthSession {
  access_token: string;
  user: SessionUser;
  org_id?: string | null;
}

export class ApiClientError extends Error {
  code: string;
  status: number;
  details: unknown;

  constructor(
    message: string,
    code: string,
    status: number,
    details: unknown = null,
  ) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export function readAuthSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function writeAuthSession(session: AuthSession): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getAccessToken(): string | null {
  return readAuthSession()?.access_token ?? null;
}

function buildUrl(
  path: string,
  query?: Record<string, string | number | boolean | undefined | null>,
): string {
  const base = API_BASE_URL || (typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:8000");
  const url = new URL(path.startsWith("http") ? path : `${base}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function parseError(response: Response): Promise<ApiClientError> {
  try {
    const body = (await response.json()) as {
      error?: { code?: string; message?: string; details?: unknown };
    };
    const code = body.error?.code ?? "request_failed";
    const message = body.error?.message ?? response.statusText;
    return new ApiClientError(message, code, response.status, body.error?.details);
  } catch {
    return new ApiClientError(
      response.statusText || "Request failed",
      "request_failed",
      response.status,
    );
  }
}

export interface RequestOptions {
  method?: string;
  query?: Record<string, string | number | boolean | undefined | null>;
  body?: unknown;
  auth?: boolean;
  headers?: Record<string, string>;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", query, body, auth = true, headers = {} } = options;
  const requestHeaders: Record<string, string> = { ...headers };

  if (body !== undefined && !(body instanceof FormData)) {
    requestHeaders["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getAccessToken();
    if (token) {
      requestHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(buildUrl(path, query), {
    method,
    headers: requestHeaders,
    body:
      body === undefined
        ? undefined
        : body instanceof FormData
          ? body
          : JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await parseError(response);
    if (error.status === 401 && auth) {
      clearAuthSession();
    }
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as T;
}

export async function apiRequestBlob(
  path: string,
  options: RequestOptions = {},
): Promise<Blob> {
  const { method = "GET", query, auth = true, headers = {} } = options;
  const requestHeaders: Record<string, string> = { ...headers };

  if (auth) {
    const token = getAccessToken();
    if (token) {
      requestHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(buildUrl(path, query), { method, headers: requestHeaders });
  if (!response.ok) {
    const error = await parseError(response);
    if (error.status === 401 && auth) {
      clearAuthSession();
    }
    throw error;
  }
  return response.blob();
}

export function downloadBlob(blob: Blob, filename: string): void {
  if (typeof window === "undefined") return;
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
