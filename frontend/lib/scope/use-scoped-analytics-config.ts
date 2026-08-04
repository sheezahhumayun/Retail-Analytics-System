"use client";

import { useMemo } from "react";

import {
  dwellStatsFromRows,
  occupancyStatsFromRows,
  queueStatsFromRows,
  trafficStatsFromRows,
  zoneStatsFromRows,
} from "@/lib/api/mappers";
import { dateRangeForKey } from "@/lib/scope/date-range";
import { resolveZoneId } from "@/lib/scope/scope-filters";
import { useScope } from "@/lib/scope/ScopeContext";
import {
  fetchDwellTimeData,
  fetchIntervalLabel,
  fetchOccupancyData,
  fetchQueuesData,
  fetchTrafficData,
  fetchZonesData,
  getDwell,
  getOccupancy,
  getQueues,
  getTraffic,
  getZones,
} from "@/lib/api/analytics";
import type {
  AnalyticsDataResult,
  AnalyticsFetchOptions,
  AnalyticsPageConfig,
  ComparisonKey,
  DataRow,
  DateRangeKey,
  StatSummary,
} from "@/lib/types";

type ScopedAnalyticsKind = "traffic" | "occupancy" | "zones" | "dwell" | "queues";

type ScopedAnalyticsBase = Omit<
  AnalyticsPageConfig,
  "getData" | "getStats" | "getIntervalLabel"
> & {
  getIntervalLabel?: AnalyticsPageConfig["getIntervalLabel"];
};

function statsForKind(kind: ScopedAnalyticsKind, rows: DataRow[]): StatSummary[] {
  switch (kind) {
    case "traffic":
      return trafficStatsFromRows(rows);
    case "occupancy":
      return occupancyStatsFromRows(rows);
    case "zones":
      return zoneStatsFromRows(rows);
    case "dwell":
      return dwellStatsFromRows(rows);
    case "queues":
      return queueStatsFromRows(rows);
    default: {
      const _exhaustive: never = kind;
      return _exhaustive;
    }
  }
}

function wantsComparison(comparison?: ComparisonKey): boolean {
  return comparison != null && comparison !== "none";
}

function resolveRange(range: DateRangeKey, options?: AnalyticsFetchOptions) {
  return dateRangeForKey(range, options?.customFrom, options?.customTo);
}

function useScopedAnalyticsConfig(
  kind: ScopedAnalyticsKind,
  base: ScopedAnalyticsBase,
): AnalyticsPageConfig {
  const { storeId, cameraId, zoneId, camera, store } = useScope();
  const resolvedZoneId = useMemo(
    () => resolveZoneId(zoneId, camera, store),
    [zoneId, camera, store],
  );

  return useMemo(() => {
    const getData: AnalyticsPageConfig["getData"] = async (range, options) => {
      const { from, to } = resolveRange(range, options);
      const compare = wantsComparison(options?.comparison);

      switch (kind) {
        case "traffic": {
          if (!storeId) return fetchTrafficData(range, options);
          return getTraffic({
            store_id: storeId,
            camera_id: cameraId ?? undefined,
            zone_id: zoneId ?? undefined,
            from,
            to,
            compare,
          });
        }
        case "occupancy": {
          if (!storeId && !cameraId) return fetchOccupancyData(range, options);
          return getOccupancy({
            store_id: storeId ?? undefined,
            camera_id: cameraId ?? undefined,
            from,
            to,
            compare,
          });
        }
        case "zones": {
          if (!storeId) return fetchZonesData(range, options);
          const result = await getZones({
            store_id: storeId,
            camera_id: cameraId ?? undefined,
            zone_id: zoneId ?? undefined,
            from,
            to,
            compare,
          });
          return { rows: result.rows, comparison: result.comparison };
        }
        case "dwell": {
          if (!storeId) return fetchDwellTimeData(range, options);
          return getDwell({
            store_id: storeId,
            camera_id: cameraId ?? undefined,
            zone_id: zoneId ?? undefined,
            from,
            to,
            compare,
          });
        }
        case "queues": {
          if (!storeId) return fetchQueuesData(range, options);
          return getQueues({
            store_id: storeId,
            camera_id: cameraId ?? undefined,
            zone_id: zoneId ?? undefined,
            from,
            to,
            compare,
          });
        }
        default: {
          const _exhaustive: never = kind;
          return _exhaustive;
        }
      }
    };

    const getStats: AnalyticsPageConfig["getStats"] = (rows) =>
      statsForKind(kind, rows);

    return {
      ...base,
      getData,
      getStats,
      getIntervalLabel: base.getIntervalLabel ?? fetchIntervalLabel,
    };
  }, [kind, base, storeId, cameraId, zoneId, resolvedZoneId]);
}

export function useTrafficAnalyticsConfig(): AnalyticsPageConfig {
  return useScopedAnalyticsConfig("traffic", {
    title: "Traffic",
    description: "Visitor counts across the selected time period.",
    metricLabel: "Visitors",
    chartType: "bar",
    currentSeriesLabel: "Current period",
    priorSeriesLabel: "Prior period",
  });
}

export function useOccupancyAnalyticsConfig(): AnalyticsPageConfig {
  return useScopedAnalyticsConfig("occupancy", {
    title: "Occupancy",
    description: "Space occupancy percentage across the selected time period.",
    metricLabel: "Occupancy %",
    chartType: "line",
    currentSeriesLabel: "Current period",
    priorSeriesLabel: "Prior period",
  });
}

export function useZonesAnalyticsConfig(): AnalyticsPageConfig {
  return useScopedAnalyticsConfig("zones", {
    title: "Zones",
    description: "Visitor distribution across facility zones.",
    metricLabel: "Visitors",
    chartType: "bar",
    getIntervalLabel: () => "Zone",
    currentSeriesLabel: "Current period",
    priorSeriesLabel: "Prior period",
  });
}

export function useDwellAnalyticsConfig(): AnalyticsPageConfig {
  return useScopedAnalyticsConfig("dwell", {
    title: "Dwell Time",
    description: "Distribution of visitor dwell times across duration buckets.",
    metricLabel: "Visitors",
    chartType: "bar",
    getIntervalLabel: () => "Duration",
    currentSeriesLabel: "Current period",
    priorSeriesLabel: "Prior period",
  });
}

export function useQueuesAnalyticsConfig(): AnalyticsPageConfig {
  return useScopedAnalyticsConfig("queues", {
    title: "Queues",
    description: "Queue length trends across the selected time period.",
    metricLabel: "Queue Length",
    chartType: "line",
    currentSeriesLabel: "Current period",
    priorSeriesLabel: "Prior period",
  });
}

export function unwrapAnalyticsRows(
  result: AnalyticsDataResult | DataRow[],
): AnalyticsDataResult {
  if (Array.isArray(result)) {
    return { rows: result };
  }
  return result;
}
