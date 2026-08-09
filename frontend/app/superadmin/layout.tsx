"use client";

import type { ReactNode } from "react";

import { AccessDenied } from "@/components/auth/access-denied";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { useAuth } from "@/lib/auth/AuthContext";

export default function SuperadminLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  if (!user || user.accountType !== "superadmin") {
    return (
      <DashboardShell hideScopeSelector>
        <AccessDenied message="this page requires superadmin access" />
      </DashboardShell>
    );
  }

  return children;
}
