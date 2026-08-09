import { describe, expect, it } from "vitest";

import { ADMIN_DISPLAY_ROLE } from "@/lib/auth/admin-role";
import {
  ADMIN_NAV_LABEL,
  NAV_ITEMS,
  navItemsForSessionRole,
} from "@/lib/nav-config";

describe("navItemsForSessionRole", () => {
  const adminChildHrefs = ["/admin/cameras", "/admin/zones-lines", "/admin/users"];

  it("includes Admin nav for System Administrator session role", () => {
    const items = navItemsForSessionRole(ADMIN_DISPLAY_ROLE);
    const adminItem = items.find((item) => item.label === ADMIN_NAV_LABEL);
    expect(adminItem).toBeDefined();
    expect(adminItem?.children?.map((child) => child.href)).toEqual(adminChildHrefs);
  });

  it("omits Admin nav for non-admin session roles", () => {
    const items = navItemsForSessionRole("Retail Analyst");
    expect(items.some((item) => item.label === ADMIN_NAV_LABEL)).toBe(false);
    expect(items.map((item) => item.label)).toEqual(
      NAV_ITEMS.filter((item) => item.label !== ADMIN_NAV_LABEL).map(
        (item) => item.label,
      ),
    );
  });

  it("keeps non-admin routes when Admin is hidden", () => {
    const items = navItemsForSessionRole("Retail Analyst");
    expect(items.some((item) => item.label === "Reports")).toBe(true);
    expect(items.some((item) => item.label === "Alerts")).toBe(true);
    expect(items.some((item) => item.label === "Live Cameras")).toBe(true);
  });
});
