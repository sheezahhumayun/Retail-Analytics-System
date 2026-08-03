'use client';

import { useEffect, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ScopeContextBanner } from '@/components/dashboard/scope-context-banner';
import { KPICard } from '@/components/overview/kpi-card';
import { VisitorsByHourChart } from '@/components/overview/visitors-by-hour-chart';
import { EntriesExitsChart } from '@/components/overview/entries-exits-chart';
import { OccupancyTrendChart } from '@/components/overview/occupancy-trend-chart';
import { getOverviewKpis } from '@/lib/api/analytics';
import { resolveZoneId } from '@/lib/scope/scope-filters';
import { useScope } from '@/lib/scope/ScopeContext';
import type { OverviewKpiData } from '@/lib/api/analytics';

export default function OverviewPage() {
  const { storeId, cameraId, zoneId, camera, store } = useScope();
  const resolvedZoneId = resolveZoneId(zoneId, camera, store);
  const [kpis, setKpis] = useState<OverviewKpiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      const kpiData = await getOverviewKpis({
        store_id: storeId ?? undefined,
        camera_id: cameraId ?? undefined,
        zone_id: resolvedZoneId,
      });
      if (!cancelled) {
        setKpis(kpiData);
        setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [storeId, cameraId, resolvedZoneId]);

  return (
    <DashboardShell>
      <div className="mx-auto w-full max-w-7xl space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Overview
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            High-level performance across the selected scope.
          </p>
        </div>

        <ScopeContextBanner storeOnly />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KPICard
            label={kpis?.visitorsToday.label ?? 'Visitors Today'}
            value={kpis ? kpis.visitorsToday.value.toLocaleString() : ''}
            trend={kpis?.visitorsToday.trend}
            icon="users"
            isLoading={loading}
          />
          <KPICard
            label={kpis?.occupancy.label ?? 'Current Occupancy'}
            value={kpis?.occupancy.value ?? ''}
            unit={kpis?.occupancy.unit}
            trend={kpis?.occupancy.trend}
            icon="activity"
            isLoading={loading}
          />
          <KPICard
            label={kpis?.peakOccupancy.label ?? 'Peak Occupancy'}
            value={kpis?.peakOccupancy.value ?? ''}
            unit={kpis?.peakOccupancy.unit}
            subtext={kpis?.peakOccupancy.subtext}
            icon="zap"
            isLoading={loading}
          />
          <KPICard
            label={kpis?.dwellTime.label ?? 'Average Dwell Time'}
            value={kpis?.dwellTime.value ?? ''}
            unit={kpis?.dwellTime.unit}
            trend={kpis?.dwellTime.trend}
            icon="clock"
            isLoading={loading}
          />
          <KPICard
            label={kpis?.queueLength.label ?? 'Current Queue Length'}
            value={kpis?.queueLength.value ?? ''}
            trend={kpis?.queueLength.trend}
            icon="list"
            isLoading={loading}
          />
          <KPICard
            label={kpis?.activeCameras.label ?? 'Active Cameras'}
            value={
              kpis
                ? `${kpis.activeCameras.value} / ${kpis.activeCameras.total} online`
                : ''
            }
            icon="camera"
            isLoading={loading}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="lg:col-span-2">
            <VisitorsByHourChart />
          </div>
          <EntriesExitsChart />
          <OccupancyTrendChart />
        </div>
      </div>
    </DashboardShell>
  );
}
