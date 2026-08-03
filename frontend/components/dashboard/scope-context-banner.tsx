"use client";

import { useScope } from "@/lib/scope/ScopeContext";
import { cn } from "@/lib/utils";

type ScopeContextBannerProps = {
  className?: string;
  /** Pages that only support store-level scope (no camera/zone API params). */
  storeOnly?: boolean;
  /** Pages with no scope filtering (admin, reports with own pickers). */
  notScoped?: boolean;
};

export function ScopeContextBanner({
  className,
  storeOnly = false,
  notScoped = false,
}: ScopeContextBannerProps) {
  const { organization, store, camera, zone, isLoading } = useScope();

  if (isLoading || !organization) {
    return null;
  }

  if (notScoped) {
    return (
      <p
        className={cn(
          "text-xs text-muted-foreground rounded-lg border border-dashed border-border bg-muted/30 px-3 py-2",
          className,
        )}
      >
        This page uses its own filters — the global scope selector does not apply here.
      </p>
    );
  }

  const parts: string[] = [];
  if (store) parts.push(`Store: ${store.name}`);
  if (!storeOnly && camera) parts.push(`Camera: ${camera.name}`);
  if (!storeOnly && zone) parts.push(`Zone: ${zone.name}`);

  const scopeLabel =
    parts.length > 0 ? parts.join(" · ") : "All stores (no scope selected)";

  const hint = storeOnly
    ? "Data on this page is filtered by store only."
    : "Charts and tables reload when you change scope above.";

  return (
    <p
      className={cn(
        "text-xs text-muted-foreground rounded-lg border border-border bg-muted/30 px-3 py-2",
        className,
      )}
    >
      <span className="font-medium text-foreground">Showing data for </span>
      {scopeLabel}
      <span className="text-muted-foreground"> — {hint}</span>
    </p>
  );
}
