import { apiRequest } from "@/lib/api/client";
import type { AlertSeverity } from "@/lib/types";

export interface AlertRule {
  id: number;
  rule_type: string;
  store_id: string | null;
  zone_id: string | null;
  threshold: number;
  severity: AlertSeverity;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertRuleUpdate {
  threshold: number;
  severity: AlertSeverity;
  enabled: boolean;
}

export async function getAlertRules(): Promise<AlertRule[]> {
  return apiRequest<AlertRule[]>("/api/admin/alert-rules");
}

export async function updateAlertRule(
  id: number,
  body: AlertRuleUpdate,
): Promise<AlertRule> {
  return apiRequest<AlertRule>(`/api/admin/alert-rules/${id}`, {
    method: "PUT",
    body,
  });
}

const RULE_TYPE_LABELS: Record<string, string> = {
  OCCUPANCY_THRESHOLD: "High Occupancy",
  DWELL_THRESHOLD: "Long Dwell",
  QUEUE_THRESHOLD: "Long Queue Length",
  QUEUE_THRESHOLD_DURATION: "Long Queue Duration",
};

export function formatAlertRuleLabel(
  rule: AlertRule,
  zoneNames?: Map<string, string>,
): string {
  const base = RULE_TYPE_LABELS[rule.rule_type] ?? rule.rule_type;
  if (rule.zone_id) {
    const zoneLabel = zoneNames?.get(rule.zone_id) ?? rule.zone_id;
    return `${base} — ${zoneLabel}`;
  }
  if (rule.store_id) {
    return `${base} — ${rule.store_id}`;
  }
  return `${base} (org default)`;
}

export const ALERT_RULE_SEVERITIES: AlertSeverity[] = [
  "critical",
  "warning",
  "info",
];
