import type { FloorZone } from "@/lib/types";

/** SVG overlay layout for heatmap floor plan — UI positioning only, not analytics data. */
export const FLOOR_ZONES: FloorZone[] = [
  { id: "entrance", label: "Entrance", x: 36, y: 76, w: 28, h: 18 },
  { id: "checkout", label: "Checkout", x: 6, y: 8, w: 26, h: 24 },
  { id: "electronics", label: "Electronics", x: 66, y: 24, w: 28, h: 22 },
  { id: "apparel", label: "Apparel", x: 48, y: 50, w: 28, h: 22 },
  { id: "back-wall", label: "Back Wall", x: 18, y: 4, w: 40, h: 16 },
];
