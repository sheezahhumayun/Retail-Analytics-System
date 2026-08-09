import { isAdminDisplayRole } from "@/lib/auth/admin-role"

export type NavLeaf = {
  label: string
  href: string
}

export type NavItem =
  | { label: string; href: string; children?: undefined }
  | { label: string; href?: undefined; children: NavLeaf[] }

/** Top-nav dropdown label for routes gated by `app/admin/layout.tsx`. */
export const ADMIN_NAV_LABEL = "Admin" as const

export const NAV_ITEMS: NavItem[] = [
  { label: "Overview", href: "/" },
  { label: "Live Cameras", href: "/live-cameras" },
  {
    label: "Analytics",
    children: [
      { label: "Traffic", href: "/analytics/traffic" },
      { label: "Occupancy", href: "/analytics/occupancy" },
      { label: "Zones", href: "/analytics/zones" },
      { label: "Dwell Time", href: "/analytics/dwell-time" },
      { label: "Queues", href: "/analytics/queues" },
    ],
  },
  {
    label: "Visual Analytics",
    children: [
      { label: "Store Heatmap", href: "/visual-analytics/heatmap" },
      { label: "Zone Performance", href: "/visual-analytics/zone-performance" },
      { label: "Customer Flow", href: "/visual-analytics/customer-flow" },
    ],
  },
  { label: "Reports", href: "/reports" },
  { label: "Alerts", href: "/alerts" },
  {
    label: "Admin",
    children: [
      { label: "Cameras", href: "/admin/cameras" },
      { label: "Zones & Lines", href: "/admin/zones-lines" },
      { label: "Users", href: "/admin/users" },
    ],
  },
]

/** Admin children match `/admin/cameras`, `/admin/zones-lines`, `/admin/users`. */
export function navItemsForSessionRole(role: string | undefined | null): NavItem[] {
  if (isAdminDisplayRole(role)) {
    return NAV_ITEMS
  }
  return NAV_ITEMS.filter((item) => item.label !== ADMIN_NAV_LABEL)
}

