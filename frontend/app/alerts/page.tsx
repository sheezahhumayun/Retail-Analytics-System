'use client';

import { useEffect, useMemo, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ScopeContextBanner } from '@/components/dashboard/scope-context-banner';
import { AlertFilters } from '@/components/alerts/alert-filters';
import { AlertCard } from '@/components/alerts/alert-card';
import { AlertThresholdsModal } from '@/components/alert-thresholds-modal';
import { getAlerts, updateAlert } from '@/lib/api/alerts';
import { useAuth } from '@/lib/auth/AuthContext';
import { zonesForScope } from '@/lib/scope/scope-filters';
import { useScope } from '@/lib/scope/ScopeContext';
import { SEVERITY_COLORS } from '@/lib/constants';
import type { Alert, AlertSeverity, AlertStatus } from '@/lib/types';
import { AlertCircle, Settings2 } from 'lucide-react';

const ADMIN_ROLE = 'System Administrator' as const;

export default function AlertsPage() {
  const { user } = useAuth();
  const { store, cameraId, zoneId, storeCameraIds } = useScope();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showThresholdsModal, setShowThresholdsModal] = useState(false);
  const [severity, setSeverity] = useState<AlertSeverity | 'all'>('all');
  const [status, setStatus] = useState<AlertStatus | 'all'>('all');
  const [camera, setCamera] = useState('all');
  const [zone, setZone] = useState('all');

  const cameraOptions = useMemo(
    () =>
      store?.cameras.map((c) => ({ id: c.id, label: c.name })) ?? [],
    [store],
  );

  const zoneOptions = useMemo(
    () =>
      zonesForScope(store, store?.cameras.find((c) => c.id === cameraId) ?? null).map(
        (z) => ({ id: z.id, label: z.name }),
      ),
    [store, cameraId],
  );

  useEffect(() => {
    if (cameraId) {
      setCamera(cameraId);
    } else {
      setCamera('all');
    }
  }, [cameraId]);

  useEffect(() => {
    if (zoneId) {
      setZone(zoneId);
    } else {
      setZone('all');
    }
  }, [zoneId]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await getAlerts();
        if (!cancelled) {
          setAlerts(data);
        }
      } catch {
        if (!cancelled) {
          setAlerts([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const scopeFilteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      if (cameraId && alert.cameraId && alert.cameraId !== cameraId) {
        return false;
      }
      if (
        !cameraId &&
        storeCameraIds.length > 0 &&
        alert.cameraId &&
        !storeCameraIds.includes(alert.cameraId)
      ) {
        return false;
      }
      if (zoneId && alert.zoneId && alert.zoneId !== zoneId) {
        return false;
      }
      return true;
    });
  }, [alerts, cameraId, zoneId, storeCameraIds]);

  const filteredAlerts = scopeFilteredAlerts.filter((alert) => {
    if (severity !== 'all' && alert.severity !== severity) return false;
    if (status !== 'all' && alert.status !== status) return false;
    if (camera !== 'all' && alert.cameraId !== camera) return false;
    if (zone !== 'all' && alert.zoneId !== zone) return false;
    return true;
  });

  const handleAcknowledge = async (id: string) => {
    const updated = await updateAlert(id, { status: 'acknowledged' });
    if (updated) {
      setAlerts((prev) =>
        prev.map((alert) => (alert.id === id ? updated : alert)),
      );
    }
  };

  const handleResolve = async (id: string) => {
    const updated = await updateAlert(id, { status: 'resolved' });
    if (updated) {
      setAlerts((prev) =>
        prev.map((alert) => (alert.id === id ? updated : alert)),
      );
    }
  };

  const openCount = scopeFilteredAlerts.filter((a) => a.status === 'open').length;
  const criticalCount = scopeFilteredAlerts.filter((a) => a.severity === 'critical').length;

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Alerts</h1>
            <p className="text-muted-foreground">
              Monitor and manage store events in real-time
            </p>
          </div>
          {user?.role === ADMIN_ROLE ? (
            <button
              type="button"
              onClick={() => setShowThresholdsModal(true)}
              className="inline-flex items-center gap-2 self-start rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted"
            >
              <Settings2 className="h-4 w-4" />
              Alert Thresholds
            </button>
          ) : null}
        </div>

        <ScopeContextBanner />

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-card/50 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${SEVERITY_COLORS.critical.dot}`} />
              <span className="text-sm text-muted-foreground">Critical Alerts</span>
              <span className="ml-auto font-bold text-foreground">
                {loading ? '—' : criticalCount}
              </span>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card/50 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${SEVERITY_COLORS.warning.dot}`} />
              <span className="text-sm text-muted-foreground">Open Alerts</span>
              <span className="ml-auto font-bold text-foreground">
                {loading ? '—' : openCount}
              </span>
            </div>
          </div>
        </div>

        <AlertFilters
          severity={severity}
          onSeverityChange={setSeverity}
          status={status}
          onStatusChange={setStatus}
          camera={camera}
          onCameraChange={setCamera}
          zone={zone}
          onZoneChange={setZone}
          cameraOptions={cameraOptions}
          zoneOptions={zoneOptions}
        />

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block relative w-10 h-10 mb-3">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin" />
              </div>
              <p className="text-sm text-muted-foreground">Loading alerts…</p>
            </div>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border border-border border-dashed bg-card/30 py-12 px-4">
            <AlertCircle className="mb-3 h-8 w-8 text-muted-foreground" />
            <h3 className="mb-1 text-base font-medium text-foreground">No alerts</h3>
            <p className="text-sm text-muted-foreground">
              No alerts match your current scope and filter selection.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {filteredAlerts.length} {filteredAlerts.length === 1 ? 'Alert' : 'Alerts'}
            </div>
            <div className="space-y-2">
              {filteredAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                  onResolve={handleResolve}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      <AlertThresholdsModal
        isOpen={showThresholdsModal}
        onClose={() => setShowThresholdsModal(false)}
      />
    </DashboardShell>
  );
}
