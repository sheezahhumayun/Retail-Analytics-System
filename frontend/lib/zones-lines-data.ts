import type { ZoneType } from "@/lib/types";

// ─── Zone-type metadata (UI constants) ───────────────────────────────────────

export const ZONE_TYPES: { value: ZoneType; label: string }[] = [
  { value: "entrance", label: "Entrance" },
  { value: "checkout", label: "Checkout / Queue" },
  { value: "general", label: "General" },
];

export const ZONE_TYPE_COLORS: Record<ZoneType, string> = {
  entrance: "#22d3ee",
  checkout: "#f59e0b",
  general: "#a78bfa",
};

export const SHAPE_COLORS = [
  "#22d3ee",
  "#f59e0b",
  "#a78bfa",
  "#34d399",
  "#f87171",
  "#60a5fa",
  "#fb923c",
  "#e879f9",
];
