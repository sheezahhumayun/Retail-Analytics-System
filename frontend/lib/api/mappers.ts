import type {
  AdminCamera,
  Alert,
  AnalyticsModule,
  Camera,
  CameraStatus,
  ComparisonInfo,
  CountingLine,
  DataRow,
  LineShape,
  LiveCameraStatus,
  Point,
  ReportData,
  ReportKPI,
  ReportType,
  Resolution,
  Shape,
  StatSummary,
  Store,
  User,
  UserRole,
  Zone,
  ZoneRow,
  ZoneShape,
  ZoneType,
} from "@/lib/types";
import { FLOOR_ZONES } from "@/lib/heatmap-data";
import { ZONE_TYPE_COLORS } from "@/lib/zones-lines-data";
import { getIntervalLabel as intervalLabelForRange } from "@/lib/analytics-data";
import type { DateRangeKey } from "@/lib/types";
import type { HeatBlob } from "@/lib/types";

// ─── Backend response shapes ─────────────────────────────────────────────────

export interface BackendUserInfo {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
  org_id: string;
}

export interface BackendMeResponse extends BackendUserInfo {
  store_id: string | null;
  store_ids: string[];
}

export interface BackendStoreSummary {
  id: string;
  name: string;
  address?: string | null;
}

export interface BackendOrganization {
  id: string;
  name: string;
  stores: BackendStoreSummary[];
}

export interface BackendStore extends BackendStoreSummary {
  org_id: string;
}

export interface BackendCamera {
  id: string;
  store_id: string;
  name: string;
  location?: string | null;
  rtsp_url?: string | null;
  source_type?: "live" | "recorded";
  last_processed_at?: string | null;
  camera_type: string;
  resolution?: string | null;
  fps?: number | null;
  status: string;
  analytics_modules?: string[];
}

export interface BackendCameraStatus {
  id: string;
  name: string;
  store_id: string;
  source_type?: "live" | "recorded";
  status: string;
  last_seen?: string | null;
  current_occupancy?: number | null;
  processed?: boolean | null;
  last_processed_at?: string | null;
}

export interface BackendTrafficBucket {
  metric_date: string;
  hour: number;
  entries: number;
  exits: number;
}

export interface BackendTrafficResponse {
  store_id: string;
  from: string;
  to: string;
  buckets: BackendTrafficBucket[];
  total_entries: number;
  total_exits: number;
  comparison?: BackendComparisonInfo | null;
  prior_buckets?: BackendTrafficBucket[];
  prior_total_entries?: number | null;
  prior_total_exits?: number | null;
}

export interface BackendComparisonInfo {
  status: "ok" | "module_disabled" | "insufficient_history";
  from: string;
  to: string;
  message?: string | null;
}

export interface BackendOccupancyPoint {
  timestamp: string;
  current_occupancy: number;
}

export interface BackendOccupancyResponse {
  scope: string;
  scope_id: string;
  current: number;
  trend: BackendOccupancyPoint[];
  from?: string | null;
  to?: string | null;
  comparison?: BackendComparisonInfo | null;
  prior_trend?: BackendOccupancyPoint[];
  prior_current?: number | null;
}

export interface BackendZoneBucket {
  metric_date: string;
  hour: number;
  visitors: number;
  avg_dwell: number;
  max_dwell: number;
  min_dwell: number | null;
  dwell_count: number;
}

export interface BackendZoneAnalyticsResponse {
  zone_id: string;
  from: string;
  to: string;
  buckets: BackendZoneBucket[];
  comparison?: BackendComparisonInfo | null;
  prior_buckets?: BackendZoneBucket[];
}

export interface BackendDwellSession {
  id: number;
  zone_id: string;
  track_id: string;
  enter_ts: string;
  exit_ts: string;
  dwell_seconds: number;
}

export interface BackendDwellResponse {
  zone_id: string;
  from: string;
  to: string;
  sessions: BackendDwellSession[];
  count: number;
  avg_dwell_seconds: number | null;
  comparison?: BackendComparisonInfo | null;
  prior_sessions?: BackendDwellSession[];
  prior_count?: number | null;
  prior_avg_dwell_seconds?: number | null;
}

export interface BackendHeatmapResponse {
  camera_id: string;
  date: string;
  from_time: string;
  to_time: string;
  spec: { width: number; height: number; grid_scale: number };
  density: number[][];
  trajectory: number[][];
  total_hits: number;
}

export interface BackendQueueSample {
  timestamp: string;
  queue_length: number;
  estimated_wait: number;
}

export interface BackendQueueResponse {
  zone_id: string;
  from: string;
  to: string;
  samples: BackendQueueSample[];
  avg_queue_length: number | null;
  max_queue_length: number | null;
  comparison?: BackendComparisonInfo | null;
  prior_samples?: BackendQueueSample[];
  prior_avg_queue_length?: number | null;
  prior_max_queue_length?: number | null;
}

export interface BackendAlert {
  id: number;
  alert_type: string;
  camera_id?: string | null;
  zone_id?: string | null;
  timestamp: string;
  severity: string;
  status: string;
  metadata?: Record<string, unknown>;
}

export interface BackendAlertList {
  count: number;
  alerts: BackendAlert[];
}

export interface BackendReportPayload {
  header: {
    report_type: string;
    store_id: string;
    from: string;
    to: string;
    generated_at: string;
    camera_id?: string | null;
    coverage?: {
      module: string;
      cameras_in_scope: number;
      cameras_eligible: number;
      zones_in_scope: number;
      zones_eligible: number;
    } | null;
  };
  kpis: { key: string; label: string; value: number | string }[];
  series: { name: string; points: Record<string, unknown>[] }[];
  table: { columns: Record<string, unknown> }[];
  footnotes?: string[];
  exclusions?: Array<{
    kind: string;
    id: string;
    name: string;
    module: string;
    reason: string;
  }>;
  comparison?: BackendComparisonInfo | null;
}

export interface BackendZoneShape {
  id: string;
  camera_id: string;
  name: string;
  type: string;
  polygon_points: number[][];
  created_at: string;
}

export interface BackendCountingLine {
  id: string;
  camera_id: string;
  name: string;
  point_a: Point;
  point_b: Point;
  direction: "left_is_inside" | "right_is_inside";
  created_at: string;
}

export interface BackendUser {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
  org_id: string;
  store_id?: string | null;
}

// ─── Role mapping ────────────────────────────────────────────────────────────

export function backendRoleToFrontend(role: "admin" | "user"): UserRole {
  return role === "admin" ? "System Administrator" : "Retail Analyst";
}

export function frontendRoleToBackend(role: UserRole): "admin" | "user" {
  return role === "System Administrator" ? "admin" : "user";
}

// ─── Date helpers ──────────────────────────────────────────────────────────

export function priorDateRange(from: string, to: string): { from: string; to: string } {
  const fromDate = new Date(from);
  const toDate = new Date(to);
  const spanDays = Math.max(
    1,
    Math.round((toDate.getTime() - fromDate.getTime()) / 86_400_000),
  );
  const priorTo = new Date(fromDate);
  priorTo.setDate(priorTo.getDate() - 1);
  const priorFrom = new Date(priorTo);
  priorFrom.setDate(priorFrom.getDate() - spanDays + 1);
  return {
    from: priorFrom.toISOString().slice(0, 10),
    to: priorTo.toISOString().slice(0, 10),
  };
}

function formatHourLabel(hour: number): string {
  if (hour === 0) return "12 AM";
  if (hour < 12) return `${hour} AM`;
  if (hour === 12) return "12 PM";
  return `${hour - 12} PM`;
}

function bucketKey(date: string, hour: number): string {
  return `${date}T${String(hour).padStart(2, "0")}`;
}

export function mapComparisonInfo(
  comparison?: BackendComparisonInfo | null,
): ComparisonInfo | null {
  if (!comparison) return null;
  return {
    status: comparison.status,
    from: comparison.from,
    to: comparison.to,
    message: comparison.message,
  };
}

function priorValuesByIndex<T>(
  current: T[],
  prior: T[],
  pick: (item: T) => number,
): Array<number | undefined> {
  return current.map((_, index) => {
    const priorItem = prior[index];
    return priorItem !== undefined ? pick(priorItem) : undefined;
  });
}

export function pctTrend(current: number, prior?: number | null): number | undefined {
  if (prior == null || prior === 0) return undefined;
  return Math.round(((current - prior) / prior) * 100 * 10) / 10;
}

export function mapTrafficBuckets(
  buckets: BackendTrafficBucket[],
  priorBuckets: BackendTrafficBucket[] = [],
): DataRow[] {
  const priorByIndex = priorValuesByIndex(buckets, priorBuckets, (b) => b.entries);
  const multiDay = new Set(buckets.map((b) => b.metric_date)).size > 1;

  return buckets.map((bucket, index) => {
    const id = bucketKey(bucket.metric_date, bucket.hour);
    return {
      id,
      label: multiDay
        ? `${bucket.metric_date} ${formatHourLabel(bucket.hour)}`
        : formatHourLabel(bucket.hour),
      current: bucket.entries,
      prior: priorByIndex[index],
    };
  });
}

export function trafficStatsFromRows(rows: DataRow[]): StatSummary[] {
  if (rows.length === 0) {
    return [
      { label: "Total Visitors", value: "0" },
      { label: "Peak Hour", value: "0" },
      { label: "Average Per Interval", value: "0" },
    ];
  }
  const total = rows.reduce((sum, row) => sum + row.current, 0);
  const peak = rows.reduce((max, row) => (row.current > max.current ? row : max), rows[0]);
  const avg = Math.round(total / rows.length);
  return [
    { label: "Total Visitors", value: total.toLocaleString() },
    { label: "Peak Hour", value: peak.current.toLocaleString(), subtext: peak.label },
    { label: "Average Per Interval", value: avg.toLocaleString() },
  ];
}

export function mapOccupancyTrend(
  trend: BackendOccupancyPoint[],
  priorTrend: BackendOccupancyPoint[] = [],
): DataRow[] {
  // Deduplicate trend by unique timestamp (take only first occurrence)
  // This handles cases where trend contains both current and prior data flattened
  const seenTimestamps = new Set<string>();
  const uniqueTrend: BackendOccupancyPoint[] = [];
  
  for (const point of trend) {
    if (!seenTimestamps.has(point.timestamp)) {
      seenTimestamps.add(point.timestamp);
      uniqueTrend.push(point);
    }
  }
  
  const priorByIndex = priorValuesByIndex(
    uniqueTrend,
    priorTrend,
    (p) => p.current_occupancy,
  );
  const multiDay =
    new Set(uniqueTrend.map((p) => p.timestamp.slice(0, 10))).size > 1;

  const result = uniqueTrend.map((point, index) => {
    const datePart = point.timestamp.slice(0, 10);
    const timePart = point.timestamp.slice(11, 16) || "00:00";
    return {
      id: point.timestamp,
      label: multiDay ? `${datePart} ${timePart}` : timePart,
      current: point.current_occupancy,
      prior: priorByIndex[index],
    };
  });
  
  return result;
}

export function occupancyStatsFromRows(rows: DataRow[]): StatSummary[] {
  if (rows.length === 0) {
    return [
      { label: "Average Occupancy", value: "0" },
      { label: "Peak Occupancy", value: "0" },
      { label: "Total Capacity", value: "100%" },
    ];
  }
  const total = rows.reduce((sum, row) => sum + row.current, 0);
  const peak = rows.reduce((max, row) => (row.current > max.current ? row : max), rows[0]);
  const avg = Math.round(total / rows.length);
  return [
    { label: "Average Occupancy", value: `${avg}` },
    { label: "Peak Occupancy", value: `${peak.current}`, subtext: peak.label },
    { label: "Total Capacity", value: "100%" },
  ];
}

export function mapZoneBuckets(
  buckets: BackendZoneBucket[],
  priorBuckets: BackendZoneBucket[] = [],
): DataRow[] {
  const priorByIndex = priorValuesByIndex(buckets, priorBuckets, (b) => b.visitors);
  const multiDay = new Set(buckets.map((b) => b.metric_date)).size > 1;

  return buckets.map((bucket, index) => {
    const id = bucketKey(bucket.metric_date, bucket.hour);
    return {
      id,
      label: multiDay
        ? `${bucket.metric_date} ${formatHourLabel(bucket.hour)}`
        : formatHourLabel(bucket.hour),
      current: bucket.visitors,
      prior: priorByIndex[index],
    };
  });
}

export function zoneStatsFromRows(rows: DataRow[]): StatSummary[] {
  if (rows.length === 0) {
    return [
      { label: "Total Visitors", value: "0" },
      { label: "Busiest Zone", value: "0" },
      { label: "Average Per Zone", value: "0" },
    ];
  }
  const total = rows.reduce((sum, row) => sum + row.current, 0);
  const busiest = rows.reduce((max, row) => (row.current > max.current ? row : max), rows[0]);
  const avg = Math.round(total / rows.length);
  return [
    { label: "Total Visitors", value: total.toLocaleString() },
    { label: "Busiest Hour", value: busiest.current.toLocaleString(), subtext: busiest.label },
    { label: "Average Per Interval", value: avg.toLocaleString() },
  ];
}

function dwellBucketLabel(seconds: number): string {
  if (seconds < 30) return "0-30s";
  if (seconds < 60) return "30-60s";
  if (seconds < 180) return "1-3 min";
  if (seconds < 600) return "3-10 min";
  return "10+ min";
}

export function mapDwellSessions(
  sessions: BackendDwellSession[],
  priorSessions: BackendDwellSession[] = [],
): DataRow[] {
  const currentRows = mapDwellSessionsForPeriod(sessions);
  if (priorSessions.length === 0) {
    return currentRows;
  }
  const priorRows = mapDwellSessionsForPeriod(priorSessions);
  const priorMap = new Map(priorRows.map((row) => [row.label, row.current]));
  return currentRows.map((row) => ({
    ...row,
    prior: priorMap.get(row.label),
  }));
}

function mapDwellSessionsForPeriod(sessions: BackendDwellSession[]): DataRow[] {
  const buckets = new Map<string, number>();
  for (const session of sessions) {
    const label = dwellBucketLabel(session.dwell_seconds);
    buckets.set(label, (buckets.get(label) ?? 0) + 1);
  }
  const order = ["0-30s", "30-60s", "1-3 min", "3-10 min", "10+ min"];
  return order.map((label) => ({
    id: `dwell-${label}`,
    label,
    current: buckets.get(label) ?? 0,
  }));
}

export function dwellStatsFromSessions(
  sessions: BackendDwellSession[],
  avgDwell: number | null,
): StatSummary[] {
  const total = sessions.length;
  const extended = sessions.filter((s) => s.dwell_seconds >= 600).length;
  return [
    { label: "Total Visits", value: total.toLocaleString() },
    {
      label: "Average Duration",
      value: avgDwell != null ? `${Math.round(avgDwell)}s` : "—",
    },
    { label: "Extended Stays (10+)", value: extended.toLocaleString() },
  ];
}

/** Approx stats from histogram rows produced by mapDwellSessions (no extra HTTP). */
export function dwellStatsFromRows(rows: DataRow[]): StatSummary[] {
  const total = rows.reduce((sum, row) => sum + row.current, 0);
  const extended = rows.find((row) => row.label === "10+ min")?.current ?? 0;
  return [
    { label: "Total Visits", value: total.toLocaleString() },
    { label: "Average Duration", value: "—" },
    { label: "Extended Stays (10+)", value: extended.toLocaleString() },
  ];
}

export function mapQueueSamples(
  samples: BackendQueueSample[],
  priorSamples: BackendQueueSample[] = [],
): DataRow[] {
  const priorByIndex = priorValuesByIndex(
    samples,
    priorSamples,
    (sample) => sample.queue_length,
  );
  const multiDay =
    new Set(samples.map((s) => s.timestamp.slice(0, 10))).size > 1;

  return samples.map((sample, index) => {
    const datePart = sample.timestamp.slice(0, 10);
    const timePart = sample.timestamp.slice(11, 16) || `#${index + 1}`;
    return {
      id: sample.timestamp || `queue-${index}`,
      label: multiDay && datePart ? `${datePart} ${timePart}` : timePart,
      current: sample.queue_length,
      prior: priorByIndex[index],
    };
  });
}

export function queueStatsFromRows(rows: DataRow[]): StatSummary[] {
  if (rows.length === 0) {
    return [
      { label: "Total Queue Minutes", value: "0" },
      { label: "Peak Queue Length", value: "0" },
      { label: "Average Queue Length", value: "0" },
    ];
  }
  const total = rows.reduce((sum, row) => sum + row.current, 0);
  const peak = rows.reduce((max, row) => (row.current > max.current ? row : max), rows[0]);
  const avg = Math.round(total / rows.length);
  return [
    { label: "Total Queue Minutes", value: total.toLocaleString() },
    { label: "Peak Queue Length", value: peak.current.toLocaleString(), subtext: peak.label },
    { label: "Average Queue Length", value: avg.toLocaleString() },
  ];
}

const HEAT_COLORS = ["#00aaff", "#ffcc00", "#ff8800", "#ff5500", "#ff2200", "#ff1100"];

export function densityToHeatBlobs(density: number[][]): HeatBlob[] {
  if (!density.length || !density[0]?.length) return [];
  let max = 0;
  for (const row of density) {
    for (const value of row) {
      if (value > max) max = value;
    }
  }
  if (max <= 0) return [];

  const rows = density.length;
  const cols = density[0].length;
  const threshold = max * 0.35;
  const blobs: HeatBlob[] = [];

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const value = density[r][c];
      if (value < threshold) continue;
      const intensity = Math.min(1, value / max);
      const colorIndex = Math.min(
        HEAT_COLORS.length - 1,
        Math.floor(intensity * HEAT_COLORS.length),
      );
      blobs.push({
        id: `h-${r}-${c}`,
        cx: ((c + 0.5) / cols) * 100,
        cy: ((r + 0.5) / rows) * 100,
        rx: (100 / cols) * 1.6,
        ry: (100 / rows) * 1.6,
        intensity,
        color: HEAT_COLORS[colorIndex],
      });
    }
  }
  return blobs;
}

export function mapAlert(
  alert: BackendAlert,
  cameraNames: Map<string, string>,
  zoneNames: Map<string, string>,
): Alert {
  return {
    id: String(alert.id),
    type: alert.alert_type as Alert["type"],
    severity: alert.severity as Alert["severity"],
    camera: cameraNames.get(alert.camera_id ?? "") ?? alert.camera_id ?? "Unknown camera",
    cameraId: alert.camera_id ?? undefined,
    zone: zoneNames.get(alert.zone_id ?? "") ?? alert.zone_id ?? "—",
    zoneId: alert.zone_id ?? undefined,
    timestamp: new Date(alert.timestamp),
    status: alert.status as Alert["status"],
    message:
      (alert.metadata?.message as string | undefined) ??
      `${alert.alert_type.replace(/_/g, " ")} alert`,
  };
}

export function reportTypeToBackend(type: ReportType): string {
  return type === "dwell-time" ? "dwell" : type;
}

export function mapReportPayload(
  payload: BackendReportPayload,
  storeName: string,
): ReportData {
  const titleMap: Record<string, string> = {
    traffic: "Traffic Report",
    occupancy: "Occupancy Report",
    zones: "Zone Performance Report",
    dwell: "Dwell Time Report",
    queues: "Queue Performance Report",
  };

  const kpis: ReportKPI[] = payload.kpis.map((kpi) => ({
    label: kpi.label,
    value:
      typeof kpi.value === "number" && !Number.isInteger(kpi.value)
        ? kpi.value.toFixed(1)
        : String(kpi.value),
  }));

  const chartData = payload.series.flatMap((series) =>
    series.points.map((point) => ({
      name: series.name,
      ...point,
    })),
  );

  const tableColumns =
    payload.table.length > 0 ? Object.keys(payload.table[0].columns) : [];

  const tableData = payload.table.map((row) => ({ ...row.columns }));

  return {
    title: titleMap[payload.header.report_type] ?? "Analytics Report",
    storeName,
    dateRange: `${payload.header.from} — ${payload.header.to}`,
    kpis,
    chartData,
    tableData,
    tableColumns,
    footnotes: payload.footnotes ?? [],
    exclusions: payload.exclusions ?? [],
    comparison: payload.comparison
      ? {
          status: payload.comparison.status,
          from: payload.comparison.from,
          to: payload.comparison.to,
          message: payload.comparison.message,
        }
      : null,
  };
}

export function zoneRowNotTracked(
  zoneId: string,
  zoneName: string,
  note: string,
): ZoneRow {
  return {
    id: zoneId,
    zone: zoneName,
    visits: 0,
    dwellSec: 0,
    occupancy: 0,
    trend: "flat",
    trendPct: 0,
    trackingStatus: "not_tracked",
    trackingNote: note,
  };
}

function mapLiveStatus(status: string): LiveCameraStatus {
  if (status === "online") return "online";
  if (status === "error") return "error";
  return "offline";
}

const LIVE_ZONE_VARIANTS: Zone["variant"][] = ["accent", "warm", "cool"];

function mapLiveCameraZones(
  cameraId: string,
  zones: BackendZoneShape[],
): Zone[] {
  return zones
    .filter((zone) => zone.camera_id === cameraId)
    .map((zone, index) => {
      const shape = mapZoneShape(zone);
      return {
        id: shape.id,
        label: shape.name,
        points: shape.points.map((point) => `${point.x},${point.y}`).join(" "),
        variant: LIVE_ZONE_VARIANTS[index % LIVE_ZONE_VARIANTS.length],
      };
    });
}

function mapLiveCameraCountingLines(
  cameraId: string,
  lines: BackendCountingLine[],
): CountingLine[] {
  return lines
    .filter((line) => line.camera_id === cameraId)
    .map((line) => {
      const shape = mapCountingLine(line);
      const [start, end] = shape.points;
      return {
        id: shape.id,
        label: shape.name,
        x1: start.x,
        y1: start.y,
        x2: end.x,
        y2: end.y,
      };
    });
}

export function mapLiveCamera(
  camera: BackendCamera,
  status?: BackendCameraStatus | null,
  zones: BackendZoneShape[] = [],
  lines: BackendCountingLine[] = [],
): Camera {
  return {
    id: camera.id,
    name: camera.name,
    location: camera.location ?? "",
    status: mapLiveStatus(status?.status ?? camera.status),
    frameUrl: null,
    occupancy: status?.current_occupancy ?? 0,
    entriesToday: 0,
    exitsToday: 0,
    boundingBoxes: [],
    zones: mapLiveCameraZones(camera.id, zones),
    countingLines: mapLiveCameraCountingLines(camera.id, lines),
  };
}

const RESOLUTION_TO_BACKEND: Record<Resolution, string> = {
  "1080p": "1920x1080",
  "2k": "2560x1440",
  "4k": "3840x2160",
};

const RESOLUTION_FROM_BACKEND: Record<string, Resolution> = {
  "1920x1080": "1080p",
  "2560x1440": "2k",
  "3840x2160": "4k",
  "640x360": "1080p",
};

export function resolutionToBackend(resolution: Resolution): string {
  return RESOLUTION_TO_BACKEND[resolution] ?? "1920x1080";
}

export function resolutionFromBackend(value?: string | null): Resolution {
  if (!value) return "1080p";
  return RESOLUTION_FROM_BACKEND[value] ?? "1080p";
}

const BACKEND_ANALYTICS_MODULE: Record<string, AnalyticsModule> = {
  entry_exit: "entry-exit",
  occupancy: "occupancy",
  zones: "zones",
  dwell: "dwell",
  heatmap: "heatmap",
  queues: "queue",
};

const FRONTEND_ANALYTICS_MODULE: Record<AnalyticsModule, string> = {
  "entry-exit": "entry_exit",
  occupancy: "occupancy",
  zones: "zones",
  dwell: "dwell",
  heatmap: "heatmap",
  queue: "queues",
};

export function analyticsModulesFromBackend(
  modules?: string[] | null,
): AnalyticsModule[] {
  if (!modules?.length) return [];
  return modules
    .map((module) => BACKEND_ANALYTICS_MODULE[module])
    .filter((module): module is AnalyticsModule => module !== undefined);
}

export function analyticsModulesToBackend(
  modules: AnalyticsModule[],
): string[] {
  return modules.map((module) => FRONTEND_ANALYTICS_MODULE[module]);
}

export function mapAdminCamera(
  camera: BackendCamera,
  storeName: string,
): AdminCamera {
  const sourceType = camera.source_type ?? "live";
  return {
    id: camera.id,
    name: camera.name,
    store: storeName,
    location: camera.location ?? "",
    status: (camera.status as CameraStatus) ?? "offline",
    sourceType,
    lastProcessedAt: camera.last_processed_at ?? null,
    resolution: resolutionFromBackend(camera.resolution),
    fps: camera.fps ?? 30,
    rtspUrl: camera.rtsp_url ?? "",
    cameraType: camera.camera_type === "ptz" ? "ptz" : "fixed",
    analyticsModules: analyticsModulesFromBackend(camera.analytics_modules),
    enabled: camera.status !== "disabled",
  };
}

export function mapBackendUser(
  user: BackendUser,
  storeNameMap: Map<string, string>,
): User {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    role: backendRoleToFrontend(user.role),
    assignedStore: user.store_id
      ? storeNameMap.get(user.store_id) ?? user.store_id
      : "—",
    status: "Active",
  };
}

function parsePolygonVertex(
  point: unknown,
): { x: number; y: number } | null {
  if (Array.isArray(point) && point.length >= 2) {
    const x = Number(point[0]);
    const y = Number(point[1]);
    if (Number.isFinite(x) && Number.isFinite(y)) {
      return { x, y };
    }
    return null;
  }

  if (point && typeof point === "object") {
    const record = point as { x?: unknown; y?: unknown };
    const x = Number(record.x);
    const y = Number(record.y);
    if (Number.isFinite(x) && Number.isFinite(y)) {
      return { x, y };
    }
  }

  return null;
}

function normalizePolygonPoints(
  points: unknown,
  width = 640,
  height = 360,
): Point[] {
  if (!Array.isArray(points)) {
    return [];
  }

  return points
    .map((point) => {
      const vertex = parsePolygonVertex(point);
      if (!vertex) return null;
      return {
        x: Math.max(0, Math.min(100, (vertex.x / width) * 100)),
        y: Math.max(0, Math.min(100, (vertex.y / height) * 100)),
      };
    })
    .filter((point): point is Point => point !== null);
}

function backendZoneTypeToFrontend(type: string): ZoneType {
  if (type === "entrance") return "entrance";
  if (type === "checkout_queue" || type === "checkout") return "checkout";
  return "general";
}

function frontendZoneTypeToBackend(type: ZoneType): string {
  if (type === "checkout") return "checkout_queue";
  return type;
}

export function mapZoneShape(shape: BackendZoneShape): ZoneShape {
  const zoneType = backendZoneTypeToFrontend(shape.type);
  return {
    kind: "zone",
    id: shape.id,
    name: shape.name,
    type: zoneType,
    points: normalizePolygonPoints(shape.polygon_points),
    color: ZONE_TYPE_COLORS[zoneType],
    cameraId: shape.camera_id,
  };
}

export function mapCountingLine(line: BackendCountingLine): LineShape {
  const normalized = normalizePolygonPoints(
    [
      [line.point_a.x, line.point_a.y],
      [line.point_b.x, line.point_b.y],
    ],
    640,
    360,
  );
  const pointA = normalized[0] ?? { x: 0, y: 0 };
  const pointB = normalized[1] ?? { x: 0, y: 0 };
  return {
    kind: "line",
    id: line.id,
    name: line.name,
    points: [pointA, pointB],
    insideSide: line.direction === "right_is_inside" ? "right" : "left",
    color: "#34d399",
    cameraId: line.camera_id,
  };
}

export function shapesFromBackend(
  zones: BackendZoneShape[],
  lines: BackendCountingLine[],
): Shape[] {
  return [...zones.map(mapZoneShape), ...lines.map(mapCountingLine)];
}

export function zoneRowFromAnalytics(
  zoneId: string,
  zoneName: string,
  buckets: BackendZoneBucket[],
  priorBuckets: BackendZoneBucket[] = [],
): ZoneRow {
  const visitors = buckets.reduce((sum, bucket) => sum + bucket.visitors, 0);
  const dwellWeighted = buckets.reduce(
    (sum, bucket) => sum + bucket.avg_dwell * bucket.dwell_count,
    0,
  );
  const dwellCount = buckets.reduce((sum, bucket) => sum + bucket.dwell_count, 0);
  const avgDwell = dwellCount > 0 ? Math.round(dwellWeighted / dwellCount) : 0;
  const peakVisitors = buckets.reduce(
    (max, bucket) => Math.max(max, bucket.visitors),
    0,
  );
  const priorVisitors = priorBuckets.reduce((sum, bucket) => sum + bucket.visitors, 0);
  const trendPct = pctTrend(visitors, priorVisitors) ?? 0;
  const trend: ZoneRow["trend"] =
    trendPct > 0 ? "up" : trendPct < 0 ? "down" : "flat";

  return {
    id: zoneId,
    zone: zoneName,
    visits: visitors,
    dwellSec: avgDwell,
    occupancy: Math.min(100, peakVisitors),
    trend,
    trendPct: Math.abs(trendPct),
  };
}

export function buildStoreNameMap(stores: BackendStore[]): Map<string, string> {
  return new Map(stores.map((store) => [store.id, store.name]));
}

export async function buildOrganizationFromBackend(
  org: BackendOrganization,
  camerasByStore: Map<string, BackendCamera[]>,
  zonesByCamera: Map<string, BackendZoneShape[]>,
): Promise<import("@/lib/types").Organization> {
  const stores: Store[] = org.stores.map((store) => ({
    id: store.id,
    name: store.name,
    cameras: (camerasByStore.get(store.id) ?? []).map((camera) => ({
      id: camera.id,
      name: camera.name,
      zones: (zonesByCamera.get(camera.id) ?? []).map((zone) => ({
        id: zone.id,
        name: zone.name,
        type: zone.type,
      })),
    })),
  }));

  return {
    id: org.id,
    name: org.name,
    stores,
  };
}

export { FLOOR_ZONES };
export { getIntervalLabel as fetchIntervalLabel } from "@/lib/analytics-data";
