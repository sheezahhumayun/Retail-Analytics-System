"use client";

import type { ReactNode } from "react"
import { usePathname } from "next/navigation"

import { ThemeProvider } from "@/components/theme-provider"
import { TopNav } from "@/components/dashboard/top-nav"
import { ScopeSelector, type ScopeBarConfig } from "@/components/dashboard/scope-selector"

/** Routes that use their own filters — global scope does not apply. */
function isScopeSelectorDisabled(pathname: string): boolean {
  return pathname.startsWith("/admin") || pathname === "/reports"
}

export type DashboardShellProps = {
  children: ReactNode
  /** Override route-based scope visibility (e.g. force hide on a custom page). */
  hideScopeSelector?: boolean
  /** Customize which scope selectors are shown in the global scope bar. */
  scopeBarConfig?: ScopeBarConfig
}

export function DashboardShell({
  children,
  hideScopeSelector,
  scopeBarConfig,
}: DashboardShellProps) {
  const pathname = usePathname()
  const showScopeSelector =
    hideScopeSelector !== undefined
      ? !hideScopeSelector
      : !isScopeSelectorDisabled(pathname)

  return (
    <ThemeProvider>
      <div className="flex min-h-dvh flex-col bg-background">
        <TopNav />

        {showScopeSelector && (
          <div className="sticky top-14 z-40 border-b border-border bg-muted/40">
            <div className="px-4 py-2.5 sm:px-6">
              <ScopeSelector config={scopeBarConfig} />
            </div>
          </div>
        )}

        <main className="flex-1 px-4 py-6 sm:px-6">{children}</main>
      </div>
    </ThemeProvider>
  )
}
