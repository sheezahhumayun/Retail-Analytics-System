"use client";

import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/auth-guard";
import { AuthProvider, useAuth } from "@/lib/auth/AuthContext";
import { ScopeProvider } from "@/lib/scope/ScopeContext";

function ScopeWhenAuthenticated({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  if (!user) {
    return <>{children}</>;
  }
  return <ScopeProvider>{children}</ScopeProvider>;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AuthGuard>
        <ScopeWhenAuthenticated>{children}</ScopeWhenAuthenticated>
      </AuthGuard>
    </AuthProvider>
  );
}
