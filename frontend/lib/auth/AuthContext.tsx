"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import {
  getCurrentUser,
  login as apiLogin,
  logout as apiLogout,
  refreshCurrentUser,
  type SessionUser,
} from "@/lib/api/auth";
import type { UserRole } from "@/lib/types";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  mustChangePassword: boolean;
};

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<SessionUser>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function sessionToAuthUser(session: SessionUser): AuthUser {
  return {
    id: session.id,
    name: session.name,
    email: session.email,
    role: session.role,
    mustChangePassword: false,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      const cached = getCurrentUser();
      if (!cached) {
        if (!cancelled) setIsLoading(false);
        return;
      }

      const refreshed = await refreshCurrentUser();
      if (!cancelled) {
        setUser(refreshed ? sessionToAuthUser(refreshed) : null);
        setIsLoading(false);
      }
    }

    hydrate();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const session = await apiLogin(email, password);
    if (session.accountType === "superadmin") {
      await apiLogout();
      setUser(null);
      return session;
    }
    setUser(sessionToAuthUser(session));
    return session;
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
    router.push("/login");
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
