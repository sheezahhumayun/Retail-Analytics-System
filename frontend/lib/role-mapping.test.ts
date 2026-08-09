import { describe, expect, it } from "vitest";

import { getRoleColor, USER_ROLES } from "@/lib/admin-users-data";
import {
  backendRoleToFrontend,
  frontendRoleToBackend,
} from "@/lib/api/mappers";
import type { UserRole } from "@/lib/types";

describe("user role labels", () => {
  it("offers exactly two picker options aligned with backend admin/user", () => {
    expect(USER_ROLES).toEqual(["Retail Analyst", "System Administrator"]);
  });

  it("round-trips backend admin and user through display labels", () => {
    expect(backendRoleToFrontend("admin")).toBe("System Administrator");
    expect(backendRoleToFrontend("user")).toBe("Retail Analyst");
    expect(frontendRoleToBackend("System Administrator")).toBe("admin");
    expect(frontendRoleToBackend("Retail Analyst")).toBe("user");
  });

  it("maps every UserRole union member to a backend role", () => {
    const roles: UserRole[] = ["Retail Analyst", "System Administrator"];
    for (const role of roles) {
      expect(["admin", "user"]).toContain(frontendRoleToBackend(role));
    }
  });

  it("falls back to a neutral badge color for unrecognized display roles", () => {
    expect(getRoleColor("Store Manager")).toBe(
      "bg-muted text-muted-foreground dark:text-muted-foreground",
    );
    expect(getRoleColor("Retail Analyst")).toBe(
      "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
    );
  });
});
