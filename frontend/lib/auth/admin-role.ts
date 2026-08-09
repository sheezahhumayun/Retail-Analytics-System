/** Frontend display role that gates admin-only UI (matches backend `admin` via mappers). */
export const ADMIN_DISPLAY_ROLE = "System Administrator" as const;

export function isAdminDisplayRole(role: string | undefined | null): boolean {
  return role === ADMIN_DISPLAY_ROLE;
}
