import {
  apiRequest,
  clearAuthSession,
  readAuthSession,
  writeAuthSession,
  type AuthSession,
  type SessionUser,
} from "@/lib/api/client";
import {
  backendRoleToFrontend,
  type BackendMeResponse,
  type BackendUserInfo,
} from "@/lib/api/mappers";
import { clearStoresCache } from "@/lib/api/stores";
import type { UserRole } from "@/lib/types";

export type { SessionUser };

const DEV_ROLE_EMAIL: Partial<Record<UserRole, string>> = {
  "System Administrator": "admin@demo-retail.local",
  "Store Manager": "user@demo-retail.local",
  "Operations Manager": "user@demo-retail.local",
  "Retail Analyst": "user@demo-retail.local",
};

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

/** Dev helper — logs in with a seeded demo account for the given UI role. */
export async function loginByRole(
  role: UserRole,
  password: string,
): Promise<SessionUser> {
  const email = DEV_ROLE_EMAIL[role] ?? "user@demo-retail.local";
  return login(email, password);
}

export function logout(): Promise<void> {
  clearAuthSession();
  clearStoresCache();
  return Promise.resolve();
}

export function getCurrentUser(): SessionUser | null {
  const session = readAuthSession();
  return session?.user ?? null;
}

export async function refreshCurrentUser(): Promise<SessionUser | null> {
  const session = readAuthSession();
  if (!session?.access_token) return null;

  try {
    const me = await apiRequest<BackendMeResponse>("/api/auth/me");
    const updated: AuthSession = {
      access_token: session.access_token,
      org_id: me.org_id,
      user: {
        id: me.id,
        name: me.name,
        email: me.email,
        role: backendRoleToFrontend(me.role),
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
