"use client";

import { useScope } from "@/lib/scope/ScopeContext";
import { cn } from "@/lib/utils";

export function OrganizationLabel({ className }: { className?: string }) {
  const { organization, isLoading } = useScope();

  if (isLoading || !organization) {
    return (
      <span
        className={cn("h-8 w-24 animate-pulse rounded-md bg-muted sm:w-28", className)}
        aria-hidden="true"
      />
    );
  }

  return (
    <div
      className={cn(
        "flex min-w-0 max-w-[9rem] flex-col leading-tight sm:max-w-xs",
        className,
      )}
      aria-label={`Organization: ${organization.name}`}
    >
      <span className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
        Organization
      </span>
      <span className="truncate text-sm font-medium text-foreground">
        {organization.name}
      </span>
    </div>
  );
}
