import type { UserRole, UserStatus } from "@/lib/types";
import { USER_STATUS_COLORS } from "@/lib/constants";

export const STORES = ['Downtown Mall', 'Westside Center'];

export const USER_ROLES: UserRole[] = [
  'Retail Analyst',
  'System Administrator',
];

export const ROLE_COLORS: Record<UserRole, string> = {
  'Retail Analyst': 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  'System Administrator': 'bg-rose-500/10 text-rose-700 dark:text-rose-400',
};

const DEFAULT_ROLE_COLOR =
  'bg-muted text-muted-foreground dark:text-muted-foreground';

/** Badge color for a display role; unknown/legacy labels get a neutral fallback. */
export function getRoleColor(role: string): string {
  if (role in ROLE_COLORS) {
    return ROLE_COLORS[role as UserRole];
  }
  return DEFAULT_ROLE_COLOR;
}

export function getStatusColor(status: UserStatus): string {
  return USER_STATUS_COLORS[status];
}

export function getStatusLabel(status: UserStatus): string {
  return status;
}
