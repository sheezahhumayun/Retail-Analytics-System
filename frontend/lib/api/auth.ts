import {
  apiRequest,
  ApiClientError,
  clearAuthSession,
  readAuthSession,
  writeAuthSession,
  type AuthSession,
  type SessionUser,
} from "@/lib/api/client";
import {
  backendRoleToFrontend,
  type BackendMeResponse,
  type BackendSuperadminMeResponse,
  type BackendUserInfo,
} from "@/lib/api/mappers";
import { clearStoresCache } from "@/lib/api/stores";

export type { SessionUser };

/** Seed-account emails shown on the login page picker (documented in PROJECT_STATUS.md). */
export const LOGIN_HINTS = [
  { email: "admin@demo-retail.local", label: "Admin (System Administrator)" },
  { email: "user@demo-retail.local", label: "User (Retail Analyst)" },
] as const;

const DISABLED_ACCOUNT_MESSAGE =
  "This account has been disabled. Contact an administrator.";
const INVALID_CREDENTIALS_MESSAGE = "Invalid email or password.";

export function getLoginErrorMessage(error: unknown): string {
  if (error instanceof ApiClientError && error.code === "account_disabled") {
    return DISABLED_ACCOUNT_MESSAGE;
  }
  return INVALID_CREDENTIALS_MESSAGE;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: BackendUserInfo;
}

function toSessionUser(user: BackendUserInfo): SessionUser {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    role: backendRoleToFrontend(user.role),
    accountType: user.account_type ?? "org_user",
  };
}

export async function login(email: string, password: string): Promise<SessionUser> {
  const response = await apiRequest<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: { email, password },
    auth: false,
  });

  const session: AuthSession = {
    access_token: response.access_token,
    user: toSessionUser(response.user),
    org_id: response.user.org_id,
  };
  writeAuthSession(session);
  return session.user;
}

export function logout(): Promise<void> {
  clearAuthSession();
  clearStoresCache();
  return Promise.resolve();
}

export function getCurrentUser(): SessionUser | null {
  const session = readAuthSession();
  if (!session?.user) return null;
  return {
    ...session.user,
    accountType: session.user.accountType ?? "org_user",
  };
}

export async function refreshCurrentUser(): Promise<SessionUser | null> {
  const session = readAuthSession();
  if (!session?.access_token) return null;

  const accountType = session.user.accountType ?? "org_user";

  try {
    if (accountType === "superadmin") {
      const me = await apiRequest<BackendSuperadminMeResponse>(
        "/api/auth/superadmin/me",
      );
      const updated: AuthSession = {
        access_token: session.access_token,
        org_id: null,
        user: {
          id: me.id,
          name: me.name,
          email: me.email,
          role: backendRoleToFrontend(me.role),
          accountType: "superadmin",
        },
      };
      writeAuthSession(updated);
      return updated.user;
    }

    const me = await apiRequest<BackendMeResponse>("/api/auth/me");
    const updated: AuthSession = {
      access_token: session.access_token,
      org_id: me.org_id,
      user: {
        id: me.id,
        name: me.name,
        email: me.email,
        role: backendRoleToFrontend(me.role),
        accountType: me.account_type ?? "org_user",
      },
    };
    writeAuthSession(updated);
    return updated.user;
  } catch {
    clearAuthSession();
    return null;
  }
}

export function getSessionOrgId(): string | null {
  return readAuthSession()?.org_id ?? null;
}
