import { apiRequest } from "@/lib/api/client";
import {
  mapAlert,
  type BackendAlert,
  type BackendAlertList,
} from "@/lib/api/mappers";
import { getOrganization } from "@/lib/api/stores";
import {
  formatAlertTime,
  getAlertLabel,
  getSeverityColor,
  getSeverityDotColor,
  getStatusColor,
} from "@/lib/alerts-data";
import type { Alert, AlertSeverity, AlertStatus } from "@/lib/types";

export {
  formatAlertTime,
  getAlertLabel,
  getSeverityColor,
  getSeverityDotColor,
  getStatusColor,
};

export interface GetAlertsParams {
  status?: AlertStatus;
  severity?: AlertSeverity;
}

export type AlertPatch = Partial<
  Pick<Alert, "status" | "severity" | "message">
>;

type OpenAlertCountListener = () => void;
const openAlertCountListeners = new Set<OpenAlertCountListener>();

/** Subscribe to open-alert count changes (e.g. after PATCH on /api/alerts). */
export function subscribeOpenAlertCount(listener: OpenAlertCountListener): () => void {
  openAlertCountListeners.add(listener);
  return () => {
    openAlertCountListeners.delete(listener);
  };
}

export function notifyOpenAlertCountChanged(): void {
  for (const listener of openAlertCountListeners) {
    listener();
  }
}

/** Name lookups from the cached org tree — no per-camera zone fan-out. */
async function buildNameLookups(): Promise<{
  cameras: Map<string, string>;
  zones: Map<string, string>;
}> {
  const cameraNames = new Map<string, string>();
  const zoneNames = new Map<string, string>();
  try {
    const org = await getOrganization();
    for (const store of org.stores) {
      for (const camera of store.cameras) {
        cameraNames.set(camera.id, camera.name);
        for (const zone of camera.zones) {
          zoneNames.set(zone.id, zone.name);
        }
      }
    }
  } catch {
    // leave maps empty — mapper falls back to ids
  }
  return { cameras: cameraNames, zones: zoneNames };
}

export async function getAlerts({
  status,
  severity,
}: GetAlertsParams = {}): Promise<Alert[]> {
  const [response, lookups] = await Promise.all([
    apiRequest<BackendAlertList>("/api/alerts", {
      query: {
        status,
        severity,
      },
    }),
    buildNameLookups(),
  ]);

  return response.alerts.map((alert) =>
    mapAlert(alert, lookups.cameras, lookups.zones),
  );
}

export async function updateAlert(
  id: string,
  patch: AlertPatch,
): Promise<Alert | null> {
  if (!patch.status) return null;

  const updated = await apiRequest<BackendAlert>(`/api/alerts/${id}`, {
    method: "PATCH",
    body: { status: patch.status },
  });

  notifyOpenAlertCountChanged();

  const lookups = await buildNameLookups();
  return mapAlert(updated, lookups.cameras, lookups.zones);
}

export async function getOpenAlertCount(): Promise<number> {
  const response = await apiRequest<BackendAlertList>("/api/alerts", {
    query: { status: "open" },
  });
  return response.count;
}
