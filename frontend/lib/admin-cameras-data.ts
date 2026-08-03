import type { AnalyticsModule, CameraStatus } from "@/lib/types";
import { CAMERA_STATUS_COLORS } from "@/lib/constants";

export const ANALYTICS_MODULES_LABELS: Record<AnalyticsModule, string> = {
  "entry-exit": "Entry/Exit",
  occupancy: "Occupancy",
  zones: "Zones",
  dwell: "Dwell",
  heatmap: "Heatmap",
  queue: "Queue",
};

export function getStatusColor(status: CameraStatus): string {
  return CAMERA_STATUS_COLORS[status];
}

export function getStatusLabel(status: CameraStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}
