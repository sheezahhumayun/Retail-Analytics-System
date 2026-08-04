import { apiRequest, ApiClientError } from "@/lib/api/client";
import {
  densityToHeatBlobs,
  dwellStatsFromSessions,
  FLOOR_ZONES,
  mapComparisonInfo,
  mapDwellSessions,
  mapOccupancyTrend,
  mapQueueSamples,
  mapTrafficBuckets,
  mapZoneBuckets,
  occupancyStatsFromRows,
  pctTrend,
  queueStatsFromRows,
  trafficStatsFromRows,
  zoneRowFromAnalytics,
  zoneRowNotTracked,
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
  AnalyticsDataResult,
  AnalyticsFetchOptions,
  ComparisonInfo,
  ComparisonKey,
  DataRow,
  DateRangeKey,
  FloorZone,
  HeatBlob,
  HeatmapCamera,
  StatSummary,
  ZoneRow,
} from "@/lib/types";

export type OverviewKpiData = {
  visitorsToday: {
    value: number;
    label: string;
    trend?: number;
    trendUnavailable?: string;
    icon: string;
    subtext?: string;
  };
  occupancy: {
    value: number;
    unit: string;
    label: string;
    trend?: number;
    trendUnavailable?: string;
    icon: string;
    subtext?: string;
  };
  peakOccupancy: {
    value: number;
    unit: string;
    label: string;
    subtext: string;
    icon: string;
  };
  dwellTime: {
    value: number;
    unit: string;
    label: string;
    trend?: number;
    trendUnavailable?: string;
    icon: string;
    subtext?: string;
  };
  queueLength: {
    value: number;
    label: string;
    trend?: number;
    trendUnavailable?: string;
    icon: string;
    subtext?: string;
  };
  activeCameras: { value: number; total: number; label: string; icon: string };
};
export type VisitorsByHourRow = { hour: string; visitors: number };
export type EntriesExitsRow = { hour: string; entries: number; exits: number };
export type OccupancyTrendRow = { day: string; occupancy: number };

export interface OverviewScopeParams {
  store_id?: string;
  camera_id?: string;
  zone_id?: string;
}

export interface DateRangeParams {
  from: string;
  to: string;
}

export interface TrafficParams extends DateRangeParams {
  store_id: string;
  camera_id?: string;
  zone_id?: string;
}

export interface OccupancyParams {
  camera_id?: string;
  store_id?: string;
}

export interface ZonesParams extends DateRangeParams {
  store_id: string;
  camera_id?: string;
  zone_id?: string;
}

export interface DwellParams extends DateRangeParams {
  store_id: string;
  camera_id?: string;
  zone_id?: string;
}

export interface HeatmapParams {
  camera_id: string;
  date: string;
  from_time: string;
  to_time: string;
}

export interface QueuesParams extends DateRangeParams {
  store_id: string;
  camera_id?: string;
  zone_id?: string;
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

export interface ZonesResult {
  zone_id: string;
  from: string;
  to: string;
  rows: DataRow[];
  performance: ZoneRow | undefined;
  comparison?: AnalyticsDataResult["comparison"];
}

function wantsComparison(comparison?: ComparisonKey): boolean {
  return comparison != null && comparison !== "none";
}

function rejectComparisonModuleDisabled(
  comparison: ComparisonInfo | null | undefined,
): void {
  if (comparison?.status === "module_disabled") {
    throw new ApiClientError(
      comparison.message ?? "Analytics module is not enabled for this scope",
      "analytics_module_disabled",
      403,
    );
  }
}

function resolveRange(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): { from: string; to: string } {
  return dateRangeForKey(range, options?.customFrom, options?.customTo);
}

async function fetchTrafficResponse(
  store_id: string,
  from: string,
  to: string,
  compare = false,
): Promise<BackendTrafficResponse> {
  const query: Record<string, string> = { store_id, from, to };
  if (compare) query.compare = "true";
  return apiRequest<BackendTrafficResponse>("/api/analytics/traffic", { query });
}

function trafficResult(
  response: BackendTrafficResponse,
  compare: boolean,
): AnalyticsDataResult {
  const comparison = compare ? mapComparisonInfo(response.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorBuckets =
    compare && comparison?.status === "ok"
      ? (response.prior_buckets ?? [])
      : [];
  return {
    rows: mapTrafficBuckets(response.buckets, priorBuckets),
    comparison,
  };
}

export async function getTraffic(
  params: TrafficParams & { compare?: boolean },
): Promise<AnalyticsDataResult> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;
  if (params.compare) query.compare = "true";

  const response = await apiRequest<BackendTrafficResponse>(
    "/api/analytics/traffic",
    { query },
  );
  const comparison = params.compare ? mapComparisonInfo(response.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorBuckets =
    params.compare && comparison?.status === "ok"
      ? (response.prior_buckets ?? [])
      : [];
  return {
    rows: mapTrafficBuckets(response.buckets, priorBuckets),
    comparison,
  };
}

export async function getOccupancy(
  params: OccupancyParams & {
    from?: string;
    to?: string;
    compare?: boolean;
  } = {},
): Promise<AnalyticsDataResult> {
  const query: Record<string, string> = {};
  if (params.camera_id) query.camera_id = params.camera_id;
  else if (params.store_id) query.store_id = params.store_id;
  else {
    query.store_id = await getDefaultStoreId();
  }
  if (params.from && params.to) {
    query.from = params.from;
    query.to = params.to;
  }
  if (params.compare) query.compare = "true";

  const response = await apiRequest<BackendOccupancyResponse>(
    "/api/analytics/occupancy",
    { query },
  );
  const comparison = params.compare ? mapComparisonInfo(response.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorTrend =
    params.compare && comparison?.status === "ok"
      ? (response.prior_trend ?? [])
      : [];
  return {
    rows: mapOccupancyTrend(response.trend, priorTrend),
    comparison,
  };
}

export async function getZones(
  params: ZonesParams & { compare?: boolean },
): Promise<ZonesResult> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;
  if (params.compare) query.compare = "true";

  const current = await apiRequest<BackendZoneAnalyticsResponse>(
    "/api/analytics/zones",
    { query },
  );

  const comparison = params.compare ? mapComparisonInfo(current.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorBuckets =
    params.compare && comparison?.status === "ok"
      ? (current.prior_buckets ?? [])
      : [];
  const rows = mapZoneBuckets(current.buckets, priorBuckets);
  const zoneName = params.zone_id ? await findZoneName(params.zone_id) : "All Zones";

  return {
    zone_id: params.zone_id || "all",
    from: params.from,
    to: params.to,
    rows,
    performance: params.zone_id 
      ? zoneRowFromAnalytics(
          params.zone_id,
          zoneName,
          current.buckets,
          priorBuckets,
        )
      : undefined,
    comparison,
  };
}

export async function getDwell(
  params: DwellParams & { compare?: boolean },
): Promise<AnalyticsDataResult> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;
  if (params.compare) query.compare = "true";

  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
    query,
  });
  const comparison = params.compare ? mapComparisonInfo(response.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorSessions =
    params.compare && comparison?.status === "ok"
      ? (response.prior_sessions ?? [])
      : [];
  return {
    rows: mapDwellSessions(response.sessions, priorSessions),
    comparison,
  };
}

export async function getDwellAverageSeconds(
  params: DwellParams,
): Promise<number | null> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;

  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
    query,
  });
  return response.avg_dwell_seconds ?? null;
}

export async function getQueueZoneDwellAverageSeconds(
  params: DwellParams,
): Promise<number | null> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;

  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell-queues", {
    query,
  });
  return response.avg_dwell_seconds ?? null;
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

export async function getQueues(
  params: QueuesParams & { compare?: boolean },
): Promise<AnalyticsDataResult> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
  };
  if (params.camera_id) query.camera_id = params.camera_id;
  if (params.zone_id) query.zone_id = params.zone_id;
  if (params.compare) query.compare = "true";

  const current = await apiRequest<BackendQueueResponse>("/api/analytics/queues", {
    query,
  });
  const comparison = params.compare ? mapComparisonInfo(current.comparison) : null;
  rejectComparisonModuleDisabled(comparison);
  const priorSamples =
    params.compare && comparison?.status === "ok"
      ? (current.prior_samples ?? [])
      : [];
  return {
    rows: mapQueueSamples(current.samples, priorSamples),
    comparison,
  };
}

function cameraHasModule(camera: BackendCamera, module: string): boolean {
  return camera.analytics_modules?.includes(module) ?? false;
}

function coverageSubtext(eligible: number, total: number, label: string): string | undefined {
  if (total === 0 || eligible >= total) return undefined;
  return `${label} tracked at ${eligible} of ${total} cameras`;
}

async function findCameraIdForZone(zoneId: string): Promise<string | null> {
  try {
    const org = await getOrganization();
    for (const store of org.stores) {
      for (const camera of store.cameras) {
        for (const zone of camera.zones) {
          if (zone.id === zoneId) return camera.id;
        }
      }
    }
  } catch {
    return null;
  }
  return null;
}

export async function getOverviewKpis(
  params: OverviewScopeParams = {},
): Promise<OverviewKpiData> {
  const store_id = params.store_id ?? (await getDefaultStoreId());
  const today = new Date().toISOString().slice(0, 10);
  const zone_id = params.zone_id ?? (await getDefaultZoneId());

  const cameras = await apiRequest<BackendCamera[]>("/api/cameras", {
    query: { store_id },
  }).catch(() => []);

  const scopedCameras = params.camera_id
    ? cameras.filter((camera) => camera.id === params.camera_id)
    : cameras;

  const entryExitCameras = scopedCameras.filter((camera) =>
    cameraHasModule(camera, "entry_exit"),
  );
  const occupancyCameras = scopedCameras.filter((camera) =>
    cameraHasModule(camera, "occupancy"),
  );
  const dwellCameras = scopedCameras.filter((camera) =>
    cameraHasModule(camera, "dwell"),
  );
  const queueCameras = scopedCameras.filter((camera) =>
    cameraHasModule(camera, "queues"),
  );

  const zoneCameraId = await findCameraIdForZone(zone_id);

  let traffic: BackendTrafficResponse | null = null;
  if (entryExitCameras.length > 0) {
    traffic = await fetchTrafficResponse(store_id, today, today, true).catch(() => null);
  }

  let occupancy: BackendOccupancyResponse | null = null;
  if (params.camera_id && occupancyCameras.length > 0) {
    occupancy = await apiRequest<BackendOccupancyResponse>("/api/analytics/occupancy", {
      query: { camera_id: params.camera_id, from: today, to: today, compare: "true" },
    }).catch(() => null);
  } else if (!params.camera_id && occupancyCameras.length > 0) {
    occupancy = await apiRequest<BackendOccupancyResponse>("/api/analytics/occupancy", {
      query: { store_id, from: today, to: today, compare: "true" },
    }).catch(() => null);
  }

  let dwell: BackendDwellResponse | null = null;
  if (zoneCameraId && dwellCameras.some((camera) => camera.id === zoneCameraId)) {
    dwell = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
      query: { store_id, zone_id, from: today, to: today, compare: "true" },
    }).catch(() => null);
  }

  let queues: BackendQueueResponse | null = null;
  if (zoneCameraId && queueCameras.some((camera) => camera.id === zoneCameraId)) {
    queues = await apiRequest<BackendQueueResponse>("/api/analytics/queues", {
      query: { store_id, zone_id, from: today, to: today, compare: "true" },
    }).catch(() => null);
  }

  const visitorsToday = traffic?.total_entries ?? 0;
  const visitorsTrend =
    traffic?.comparison?.status === "ok"
      ? pctTrend(visitorsToday, traffic.prior_total_entries ?? null)
      : undefined;
  const visitorsTrendUnavailable =
    traffic?.comparison && traffic.comparison.status !== "ok"
      ? traffic.comparison.message ?? "Comparison unavailable"
      : undefined;
  const currentOcc = occupancy?.current ?? 0;
  const peakOcc =
    occupancy?.trend.reduce(
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
  const avgDwellMinutes = dwell?.avg_dwell_seconds
    ? Math.round(dwell.avg_dwell_seconds / 60)
    : 0;
  const latestQueueSample = queues?.samples?.[queues.samples.length - 1];
  const queueLength =
    latestQueueSample?.queue_length ?? queues?.avg_queue_length ?? 0;

  const occupancyTrend =
    occupancy?.comparison?.status === "ok"
      ? pctTrend(currentOcc, occupancy.prior_current ?? null)
      : undefined;
  const occupancyTrendUnavailable =
    occupancy?.comparison && occupancy.comparison.status !== "ok"
      ? occupancy.comparison.message ?? "Comparison unavailable"
      : undefined;

  const dwellTrend =
    dwell?.comparison?.status === "ok"
      ? pctTrend(avgDwellMinutes * 60, dwell.prior_avg_dwell_seconds ?? null)
      : undefined;
  const dwellTrendUnavailable =
    dwell?.comparison && dwell.comparison.status !== "ok"
      ? dwell.comparison.message ?? "Comparison unavailable"
      : undefined;

  const queueTrend =
    queues?.comparison?.status === "ok"
      ? pctTrend(queueLength, queues.prior_avg_queue_length ?? null)
      : undefined;
  const queueTrendUnavailable =
    queues?.comparison && queues.comparison.status !== "ok"
      ? queues.comparison.message ?? "Comparison unavailable"
      : undefined;

  return {
    visitorsToday: {
      value: visitorsToday,
      label: "Visitors Today",
      trend: visitorsTrend,
      trendUnavailable: visitorsTrendUnavailable,
      icon: "users",
      subtext: coverageSubtext(entryExitCameras.length, scopedCameras.length, "Traffic"),
    },
    occupancy: {
      value: currentOcc,
      unit: "",
      label: "Current Occupancy",
      trend: occupancyTrend,
      trendUnavailable: occupancyTrendUnavailable,
      icon: "activity",
      subtext: coverageSubtext(occupancyCameras.length, scopedCameras.length, "Occupancy"),
    },
    peakOccupancy: {
      value: peakOcc,
      unit: "",
      label: "Peak Occupancy",
      subtext: peakPoint?.timestamp?.slice(11, 16) ?? "—",
      icon: "zap",
    },
    dwellTime: {
      value: avgDwellMinutes,
      unit: "min",
      label: "Average Dwell Time",
      trend: dwellTrend,
      trendUnavailable: dwellTrendUnavailable,
      icon: "clock",
      subtext:
        zoneCameraId && !dwellCameras.some((camera) => camera.id === zoneCameraId)
          ? "Dwell not enabled for selected zone camera"
          : coverageSubtext(dwellCameras.length, scopedCameras.length, "Dwell"),
    },
    queueLength: {
      value: Math.round(queueLength),
      label: "Current Queue Length",
      trend: queueTrend,
      trendUnavailable: queueTrendUnavailable,
      icon: "list",
      subtext:
        zoneCameraId && !queueCameras.some((camera) => camera.id === zoneCameraId)
          ? "Queues not enabled for selected zone camera"
          : coverageSubtext(queueCameras.length, scopedCameras.length, "Queues"),
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

export async function fetchTrafficData(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<AnalyticsDataResult> {
  const { from, to } = resolveRange(range, options);
  const store_id = await getDefaultStoreId();
  return getTraffic({
    store_id,
    from,
    to,
    compare: wantsComparison(options?.comparison),
  });
}

export async function fetchTrafficStats(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<StatSummary[]> {
  const result = await fetchTrafficData(range, options);
  return trafficStatsFromRows(result.rows);
}

export async function fetchOccupancyData(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<AnalyticsDataResult> {
  const { from, to } = resolveRange(range, options);
  const store_id = await getDefaultStoreId();
  return getOccupancy({
    store_id,
    from,
    to,
    compare: wantsComparison(options?.comparison),
  });
}

export async function fetchOccupancyStats(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<StatSummary[]> {
  const result = await fetchOccupancyData(range, options);
  return occupancyStatsFromRows(result.rows);
}

export async function fetchZonesData(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<AnalyticsDataResult> {
  const { from, to } = resolveRange(range, options);
  const store_id = await getDefaultStoreId();
  const zone_id = await getDefaultZoneId();
  const result = await getZones({
    store_id,
    zone_id,
    from,
    to,
    compare: wantsComparison(options?.comparison),
  });
  return { rows: result.rows, comparison: result.comparison };
}

export async function fetchZonesStats(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<StatSummary[]> {
  const result = await fetchZonesData(range, options);
  return zoneStatsFromRows(result.rows);
}

export async function fetchDwellTimeData(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<AnalyticsDataResult> {
  const { from, to } = resolveRange(range, options);
  const store_id = await (await import("@/lib/api/stores")).getDefaultStoreId();
  const zone_id = await getDefaultZoneId();
  return getDwell({
    store_id,
    zone_id,
    from,
    to,
    compare: wantsComparison(options?.comparison),
  });
}

export async function fetchDwellTimeStats(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<StatSummary[]> {
  const { from, to } = resolveRange(range, options);
  const store_id = await (await import("@/lib/api/stores")).getDefaultStoreId();
  const zone_id = await getDefaultZoneId();
  const response = await apiRequest<BackendDwellResponse>("/api/analytics/dwell", {
    query: { store_id, zone_id, from, to },
  });
  return dwellStatsFromSessions(response.sessions, response.avg_dwell_seconds);
}

export async function fetchQueuesData(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<AnalyticsDataResult> {
  const { from, to } = resolveRange(range, options);
  const store_id = await (await import("@/lib/api/stores")).getDefaultStoreId();
  const zone_id = await getDefaultZoneId();
  return getQueues({
    store_id,
    zone_id,
    from,
    to,
    compare: wantsComparison(options?.comparison),
  });
}

export async function fetchQueuesStats(
  range: DateRangeKey,
  options?: AnalyticsFetchOptions,
): Promise<StatSummary[]> {
  const result = await fetchQueuesData(range, options);
  return queueStatsFromRows(result.rows);
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
  const store_id = params.store_id ?? (await getDefaultStoreId());

  const cameras = await apiRequest<BackendCamera[]>("/api/cameras").catch(() => []);
  const cameraById = new Map(cameras.map((camera) => [camera.id, camera]));

  const zoneShapes: Array<{ id: string; name: string; cameraId: string }> = [];
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
          // Exclude queue-type zones (frontend ZoneShape.type already mapped to "checkout_queue")
          if (zone.type === "checkout_queue") {
            continue;
          }
          zoneShapes.push({ id: zone.id, name: zone.name, cameraId: camera.id });
        }
      }
    }
  } catch {
    return [];
  }

  const uniqueZones = new Map<string, { id: string; name: string; cameraId: string }>();
  for (const shape of zoneShapes) {
    uniqueZones.set(shape.id, shape);
  }

  const rows: ZoneRow[] = [];
  for (const shape of uniqueZones.values()) {
    const camera = cameraById.get(shape.cameraId);
    if (!camera || !cameraHasModule(camera, "zones")) {
      rows.push(
        zoneRowNotTracked(
          shape.id,
          shape.name,
          "Zone analytics not enabled for this camera",
        ),
      );
      continue;
    }

    try {
      const analytics = await apiRequest<BackendZoneAnalyticsResponse>(
        "/api/analytics/zones",
        { query: { store_id, zone_id: shape.id, from, to, compare: "true" } },
      );
      const priorBuckets =
        analytics.comparison?.status === "ok" ? (analytics.prior_buckets ?? []) : [];
      const row = zoneRowFromAnalytics(
        shape.id,
        shape.name,
        analytics.buckets,
        priorBuckets,
      );
      if (camera && !cameraHasModule(camera, "dwell")) {
        row.dwellSec = 0;
        row.trackingNote = "Dwell not enabled for this camera";
      }
      rows.push(row);
    } catch (err) {
      if (err instanceof ApiClientError && err.code === "analytics_module_disabled") {
        rows.push(
          zoneRowNotTracked(shape.id, shape.name, err.message),
        );
      } else {
        rows.push(
          zoneRowNotTracked(shape.id, shape.name, "Unable to load zone analytics"),
        );
      }
    }
  }

  return rows;
}
