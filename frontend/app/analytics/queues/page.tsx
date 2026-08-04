'use client';

import { useEffect, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { AnalyticsPageLayout, type AnalyticsPageLayoutState } from '@/components/analytics/analytics-page-layout';
import { useQueuesAnalyticsConfig } from '@/lib/scope/use-scoped-analytics-config';
import { getQueueZoneDwellAverageSeconds } from '@/lib/api/analytics';
import { useScope } from '@/lib/scope/ScopeContext';
import { dateRangeForKey } from '@/lib/scope/date-range';
import { StatCard } from '@/components/analytics/stat-card';

function QueuesPageContent() {
  const config = useQueuesAnalyticsConfig();
  const { storeId, cameraId, zoneId } = useScope();
  const [layoutState, setLayoutState] = useState<AnalyticsPageLayoutState>({
    range: 'day',
    comparison: 'none',
    customFrom: '',
    customTo: '',
  });
  const [avgWaitingTime, setAvgWaitingTime] = useState<number | null>(null);
  const [waitingTimeLoading, setWaitingTimeLoading] = useState(false);
  const scopeKey = `${storeId ?? ''}:${cameraId ?? ''}:${zoneId ?? ''}`;

  // Fetch average waiting time from dwell data whenever scope or date range changes
  useEffect(() => {
    let cancelled = false;

    async function loadWaitingTime() {
      if (!storeId) {
        setAvgWaitingTime(null);
        return;
      }

      setWaitingTimeLoading(true);
      try {
        const { from, to } = dateRangeForKey(layoutState.range, layoutState.customFrom, layoutState.customTo);
        const avgSeconds = await getQueueZoneDwellAverageSeconds({
          store_id: storeId,
          camera_id: cameraId ?? undefined,
          zone_id: zoneId ?? undefined,
          from,
          to,
        });

        if (!cancelled) {
          setAvgWaitingTime(avgSeconds);
        }
      } catch (err) {
        if (!cancelled) {
          setAvgWaitingTime(null);
        }
      } finally {
        if (!cancelled) {
          setWaitingTimeLoading(false);
        }
      }
    }

    loadWaitingTime();
    return () => {
      cancelled = true;
    };
  }, [storeId, cameraId, zoneId, layoutState.range, layoutState.customFrom, layoutState.customTo, scopeKey]);

  return (
    <div className="space-y-8">
      <AnalyticsPageLayout config={config} onStateChange={setLayoutState} />
      
      {/* Average Waiting Time Card */}
      {storeId && (
        <div>
          <h3 className="text-sm font-semibold mb-4 px-6">Wait Time Metrics</h3>
          <div className="px-6">
            <StatCard
              label="Average Waiting Time"
              value={
                waitingTimeLoading
                  ? '...'
                  : avgWaitingTime !== null
                    ? avgWaitingTime < 60
                      ? `${Math.round(avgWaitingTime)}s`
                      : `${Math.round(avgWaitingTime / 60)}m`
                    : 'N/A'
              }
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default function QueuesPage() {
  return (
    <DashboardShell scopeBarConfig={{ showCamera: true, showZone: true, onlyQueueZones: true }}>
      <QueuesPageContent />
    </DashboardShell>
  );
}
