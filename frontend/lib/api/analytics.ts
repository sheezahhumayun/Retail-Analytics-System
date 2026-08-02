import { apiRequest } from "@/lib/api/client";
import {
  densityToHeatBlobs,
  dwellStatsFromSessions,
  FLOOR_ZONES,
  mapDwellSessions,
  mapOccupancyTrend,
  mapQueueSamples,
  mapTrafficBuckets,
  mapZoneBuckets,
  occupancyStatsFromRows,
  priorDateRange,
  queueStatsFromRows,
  trafficStatsFromRows,
  zoneRowFromAnalytics,
  zoneStatsFromRows,
  type BackendCamera,
  type BackendDwellResponse,
  type BackendHeatmapResponse,
  type BackendOccupancyResponse,
  type BackendQueueResponse,
  type BackendTrafficResponse,
  type BackendZoneAnalyticsResponse,
} from "@/lib/api/mappers";
import { getDefaultStoreId, getDefaultZoneId, getOrganization } from "@/lib/api/stores";
import { getIntervalLabel } from "@/lib/analytics-data";
import { dateRangeForKey } from "@/lib/scope/date-range";
import type {
  DataRow,
  DateRangeKey,
  FloorZone,
  HeatBlob,
  HeatmapCamera,
  StatSummary,
  ZoneRow,
} from "@/lib/types";
import type { kpiData as OverviewKpiDataType } from "@/lib/overview-data";

export type OverviewKpiData = typeof OverviewKpiDataType;
export type VisitorsByHourRow = { hour: string; visitors: number };
export type EntriesExitsRow = { hour: string; entries: number; exits: number };
export type OccupancyTrendRow = { day: string; occupancy: number };

export interface OverviewScopeParams {
  store_id?: string;
}

export interface DateRangeParams {
  from: string;
  to: string;
}

export interface TrafficParams extends DateRangeParams {
  store_id: string;
}

export interface OccupancyParams {
  camera_id?: string;
  store_id?: string;
}

export interface ZonesParams extends DateRangeParams {
  zone_id: string;
}

export interface DwellParams extends DateRangeParams {
  zone_id: string;
}

export interface HeatmapParams {
  camera_id: string;
  date: string;
  from_time: string;
  to_time: string;
}

export interface QueuesParams extends DateRangeParams {
  zone_id: string;
}

export interface HeatmapResult {
  camera_id: string;
  date: string;
  from_time: string;
  to_time: string;
  blobs: HeatBlob[];
  floor_zones: FloorZone[];
}

export interface ZonesResult {
  zone_id: string;
  from: string;
  to: string;
  rows: DataRow[];
  performance: ZoneRow | undefined;
}

async function findZoneName(zone_id: string): Promise<string> {
  try {
    const org = await getOrganization();
    for (const store of org.stores) {
      for (const camera of store.cameras) {
        for (const zone of camera.zones) {
          if (zone.id === zone_id) {
            return zone.name;
          }
        }
      }
    }
  } catch {
    // fall through to id
  }
  return zone_id;
}

async function fetchTrafficResponse(
  store_id: string,
  from: string,
  to: string,
): Promise<BackendTrafficResponse> {
  return apiRequest<BackendTrafficResponse>("/api/analytics/traffic", {
    query: { store_id, from, to },
  });
}

export async function getTraffic({
  store_id,
  from,
  to,
}: TrafficParams): Promise<DataRow[]> {
  const prior = priorDateRange(from, to);
  const [current, previous] = await Promise.all([
    fetchTrafficResponse(store_id, from, to),
    fetchTrafficResponse(store_id, prior.from, prior.to).catch(() => null),
  ]);
  return mapTrafficBuckets(current.buckets, previous?.buckets ?? []);
}

export async function getOccupancy({
  camera_id,
  store_id,
}: OccupancyParams = {}): Promise<DataRow[]> {
  const query: Record<string, string> = {};
  if (camera_id) query.camera_id = camera_id;
  else if (store_id) query.store_id = store_id;
  else {
    query.store_id = await getDefaultStoreId();
  }

  const response = await apiRequest<BackendOccupancyResponse>(
    "/api/analytics/occupancy",
    { query },
  );
  return mapOccupancyTrend(response.trend);
}

export async function getZones({
  zone_id,
  from,
  to,
}: ZonesParams): Promise<ZonesResult> {
  const prior = priorDateRange(from, to);
  const [current, previous] = await Promise.all([
    apiRequest<BackendZoneAnalyticsResponse>("/api/analytics/zones", {
      query: { zone_id, from, to },
    }),
    apiRequest<BackendZoneAnalyticsResponse>("/api/analytics/zones", {
      query: { zone_id, from: prior.from, to: prior.to },
    }).catch(() => null),
  ]);

  const rows = mapZoneBuckets(current.buckets, previous?.buckets ?? []);
  const zoneName = await findZoneName(zone_id);

  return {
    zone_id,
    from,
    to,
    rows,
    performance: zoneRowFromAnalytics(zone_id, zoneName, current.buckets),
  };
}

export async function getDwell({
  zone_id,
  from,
  to,
}: DwellParams): Promise<DataRow[]> {
  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
    query: { zone_id, from, to },
  });
  return mapDwellSessions(response.sessions);
}

export async function getHeatmap({
  camera_id,
  date,
  from_time,
  to_time,
}: HeatmapParams): Promise<HeatmapResult> {
  const response = await apiRequest<BackendHeatmapResponse>(
    "/api/analytics/heatmap",
    {
      query: {
        camera_id,
        date,
        from_time,
        to_time,
      },
    },
  );

  return {
    camera_id,
    date,
    from_time,
    to_time,
    blobs: densityToHeatBlobs(response.density),
    floor_zones: FLOOR_ZONES,
  };
}

export async function getQueues({
  zone_id,
  from,
  to,
}: QueuesParams): Promise<DataRow[]> {
  const prior = priorDateRange(from, to);
  const [current, previous] = await Promise.all([
    apiRequest<BackendQueueResponse>("/api/analytics/queues", {
      query: { zone_id, from, to },
    }),
    apiRequest<BackendQueueResponse>("/api/analytics/queues", {
      query: { zone_id, from: prior.from, to: prior.to },
    }).catch(() => null),
  ]);
  return mapQueueSamples(current.samples, previous?.samples ?? []);
}

export async function getOverviewKpis(
  params: OverviewScopeParams = {},
): Promise<OverviewKpiData> {
  const store_id = params.store_id ?? (await getDefaultStoreId());
  const today = new Date().toISOString().slice(0, 10);
  const [traffic, occupancy, cameras] = await Promise.all([
    fetchTrafficResponse(store_id, today, today).catch(() => null),
    apiRequest<BackendOccupancyResponse>("/api/analytics/occupancy", {
      query: { store_id },
    }).catch(() => null),
    apiRequest<BackendCamera[]>("/api/cameras", {
      query: { store_id },
    }).catch(() => []),
  ]);

  const visitorsToday = traffic?.total_entries ?? 0;
  const currentOcc = occupancy?.current ?? 0;
  const peakOcc = occupancy?.trend.reduce(
    (max, point) => Math.max(max, point.current_occupancy),
    0,
  ) ?? currentOcc;
  const peakPoint =
    occupancy?.trend && occupancy.trend.length > 0
      ? occupancy.trend.reduce(
          (best, point) =>
            point.current_occupancy > best.current_occupancy ? point : best,
          occupancy.trend[0],
        )
      : null;
  const activeCameras = cameras.filter((camera) => camera.status === "online").length;

  return {
    visitorsToday: {
      value: visitorsToday,
      label: "Visitors Today",
      trend: 0,
      icon: "users",
    },
    occupancy: {
      value: currentOcc,
      unit: "",
      label: "Current Occupancy",
      trend: 0,
      icon: "activity",
    },
    peakOccupancy: {
      value: peakOcc,
      unit: "",
      label: "Peak Occupancy",
      subtext: peakPoint?.timestamp?.slice(11, 16) ?? "—",
      icon: "zap",
    },
    dwellTime: {
      value: 0,
      unit: "min",
      label: "Average Dwell Time",
      trend: 0,
      icon: "clock",
    },
    queueLength: {
      value: 0,
      label: "Current Queue Length",
      trend: 0,
      icon: "list",
    },
    activeCameras: {
      value: activeCameras,
      total: cameras.length,
      label: "Active Cameras",
      icon: "camera",
    },
  };
}

export async function getVisitorsByHour(
  params: OverviewScopeParams = {},
): Promise<VisitorsByHourRow[]> {
  const store_id = params.store_id ?? (await getDefaultStoreId());
  const today = new Date().toISOString().slice(0, 10);
  const traffic = await fetchTrafficResponse(store_id, today, today);
  return traffic.buckets.map((bucket) => ({
    hour:
      bucket.hour === 0
        ? "12 AM"
        : bucket.hour < 12
          ? `${bucket.hour} AM`
          : bucket.hour === 12
            ? "12 PM"
            : `${bucket.hour - 12} PM`,
    visitors: bucket.entries,
  }));
}

export async function getEntriesExits(
  params: OverviewScopeParams = {},
): Promise<EntriesExitsRow[]> {
  const store_id = params.store_id ?? (await getDefaultStoreId());
  const today = new Date().toISOString().slice(0, 10);
  const traffic = await fetchTrafficResponse(store_id, today, today);
  return traffic.buckets.map((bucket) => ({
    hour:
      bucket.hour === 0
        ? "12 AM"
        : bucket.hour < 12
          ? `${bucket.hour} AM`
          : bucket.hour === 12
            ? "12 PM"
            : `${bucket.hour - 12} PM`,
    entries: bucket.entries,
    exits: bucket.exits,
  }));
}

export async function getOccupancyTrend(
  params: OverviewScopeParams = {},
): Promise<OccupancyTrendRow[]> {
  const store_id = params.store_id ?? (await getDefaultStoreId());
  const response = await apiRequest<BackendOccupancyResponse>(
    "/api/analytics/occupancy",
    { query: { store_id } },
  );
  return response.trend.map((point) => ({
    day: point.timestamp.slice(0, 10),
    occupancy: point.current_occupancy,
  }));
}

export async function fetchTrafficData(range: DateRangeKey): Promise<DataRow[]> {
  const { from, to } = dateRangeForKey(range);
  const store_id = await getDefaultStoreId();
  return getTraffic({ store_id, from, to });
}

export async function fetchTrafficStats(range: DateRangeKey): Promise<StatSummary[]> {
  const rows = await fetchTrafficData(range);
  return trafficStatsFromRows(rows);
}

export async function fetchOccupancyData(range: DateRangeKey): Promise<DataRow[]> {
  const store_id = await getDefaultStoreId();
  return getOccupancy({ store_id });
}

export async function fetchOccupancyStats(
  range: DateRangeKey,
): Promise<StatSummary[]> {
  const rows = await fetchOccupancyData(range);
  return occupancyStatsFromRows(rows);
}

export async function fetchZonesData(range: DateRangeKey): Promise<DataRow[]> {
  const { from, to } = dateRangeForKey(range);
  const zone_id = await getDefaultZoneId();
  const result = await getZones({ zone_id, from, to });
  return result.rows;
}

export async function fetchZonesStats(range: DateRangeKey): Promise<StatSummary[]> {
  const rows = await fetchZonesData(range);
  return zoneStatsFromRows(rows);
}

export async function fetchDwellTimeData(range: DateRangeKey): Promise<DataRow[]> {
  const { from, to } = dateRangeForKey(range);
  const zone_id = await getDefaultZoneId();
  return getDwell({ zone_id, from, to });
}

export async function fetchDwellTimeStats(
  range: DateRangeKey,
): Promise<StatSummary[]> {
  const { from, to } = dateRangeForKey(range);
  const zone_id = await getDefaultZoneId();
  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
    query: { zone_id, from, to },
  });
  return dwellStatsFromSessions(response.sessions, response.avg_dwell_seconds);
}

export async function fetchQueuesData(range: DateRangeKey): Promise<DataRow[]> {
  const { from, to } = dateRangeForKey(range);
  const zone_id = await getDefaultZoneId();
  return getQueues({ zone_id, from, to });
}

export async function fetchQueuesStats(range: DateRangeKey): Promise<StatSummary[]> {
  const rows = await fetchQueuesData(range);
  return queueStatsFromRows(rows);
}

export function fetchIntervalLabel(range: DateRangeKey): string {
  return getIntervalLabel(range);
}

export async function getHeatmapCameras(): Promise<HeatmapCamera[]> {
  const cameras = await apiRequest<{ id: string; name: string; camera_type: string }[]>(
    "/api/cameras",
  );
  return cameras
    .filter((camera) => camera.camera_type === "fixed" || camera.camera_type === "fisheye")
    .map((camera) => ({ id: camera.id, label: camera.name }));
}

export async function getZonePerformance(
  params: { store_id?: string; zone_id?: string } = {},
): Promise<ZoneRow[]> {
  const { from, to } = dateRangeForKey("week");

  const zoneShapes: Array<{ id: string; name: string }> = [];
  try {
    const org = await getOrganization();
    for (const store of org.stores) {
      if (params.store_id && store.id !== params.store_id) {
        continue;
      }
      for (const camera of store.cameras) {
        for (const zone of camera.zones) {
          if (params.zone_id && zone.id !== params.zone_id) {
            continue;
          }
          zoneShapes.push({ id: zone.id, name: zone.name });
        }
      }
    }
  } catch {
    return [];
  }

  const uniqueZones = new Map<string, { id: string; name: string }>();
  for (const shape of zoneShapes) {
    uniqueZones.set(shape.id, shape);
  }

  // Backend has no store-level zone analytics aggregate yet (PROJECT_STATUS gap).
  // Fetch sequentially instead of Promise.all so we never open N concurrent
  // DB sessions from one page load.
  const rows: ZoneRow[] = [];
  for (const shape of uniqueZones.values()) {
    try {
      const analytics = await apiRequest<BackendZoneAnalyticsResponse>(
        "/api/analytics/zones",
        { query: { zone_id: shape.id, from, to } },
      );
      rows.push(zoneRowFromAnalytics(shape.id, shape.name, analytics.buckets));
    } catch {
      rows.push(zoneRowFromAnalytics(shape.id, shape.name, []));
    }
  }

  return rows;
}
