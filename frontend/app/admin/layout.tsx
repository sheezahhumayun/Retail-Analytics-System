"use client";

import type { ReactNode } from "react";

import { AccessDenied } from "@/components/auth/access-denied";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { isAdminDisplayRole } from "@/lib/auth/admin-role";
import { useAuth } from "@/lib/auth/AuthContext";

export default function AdminLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  if (!user || !isAdminDisplayRole(user.role)) {
    return (
      <DashboardShell>
        <AccessDenied />
      </DashboardShell>
    );
  }

  return children;
}
