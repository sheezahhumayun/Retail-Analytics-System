import type { AlertSeverity, AlertStatus, AlertType } from "@/lib/types";
import {
  ALERT_STATUS_COLORS,
  SEVERITY_COLORS,
} from "@/lib/constants";

export function getAlertLabel(type: AlertType): string {
  const labels: Record<AlertType, string> = {
    high_occupancy: "High Occupancy",
    long_queue: "Long Queue",
    high_dwell_time: "High Dwell Time",
    camera_offline: "Camera Offline",
  };
  return labels[type];
}

export function getSeverityColor(severity: AlertSeverity): string {
  return SEVERITY_COLORS[severity].badge;
}

export function getSeverityDotColor(severity: AlertSeverity): string {
  return SEVERITY_COLORS[severity].dot;
}

export function getStatusColor(status: AlertStatus): string {
  return ALERT_STATUS_COLORS[status];
}

export function formatAlertTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}
