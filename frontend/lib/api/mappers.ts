import type {
  AdminCamera,
  Alert,
  Camera,
  CameraStatus,
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
  };
  kpis: { key: string; label: string; value: number }[];
  series: { name: string; points: Record<string, unknown>[] }[];
  table: { columns: Record<string, unknown> }[];
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

export function mapTrafficBuckets(
  buckets: BackendTrafficBucket[],
  priorBuckets: BackendTrafficBucket[] = [],
): DataRow[] {
  const priorMap = new Map(
    priorBuckets.map((b) => [bucketKey(b.metric_date, b.hour), b.entries]),
  );
  const multiDay = new Set(buckets.map((b) => b.metric_date)).size > 1;

  return buckets.map((bucket) => {
    const id = bucketKey(bucket.metric_date, bucket.hour);
    return {
      id,
      label: multiDay
        ? `${bucket.metric_date} ${formatHourLabel(bucket.hour)}`
        : formatHourLabel(bucket.hour),
      current: bucket.entries,
      prior: priorMap.get(id),
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
  const priorMap = new Map(priorTrend.map((p, index) => [index, p.current_occupancy]));
  const multiDay =
    new Set(trend.map((p) => p.timestamp.slice(0, 10))).size > 1;

  return trend.map((point, index) => {
    const datePart = point.timestamp.slice(0, 10);
    const timePart = point.timestamp.slice(11, 16) || "00:00";
    return {
      id: point.timestamp,
      label: multiDay ? `${datePart} ${timePart}` : timePart,
      current: point.current_occupancy,
      prior: priorMap.get(index),
    };
  });
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
  const priorMap = new Map(
    priorBuckets.map((b) => [bucketKey(b.metric_date, b.hour), b.visitors]),
  );
  const multiDay = new Set(buckets.map((b) => b.metric_date)).size > 1;

  return buckets.map((bucket) => {
    const id = bucketKey(bucket.metric_date, bucket.hour);
    return {
      id,
      label: multiDay
        ? `${bucket.metric_date} ${formatHourLabel(bucket.hour)}`
        : formatHourLabel(bucket.hour),
      current: bucket.visitors,
      prior: priorMap.get(id),
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

export function mapDwellSessions(sessions: BackendDwellSession[]): DataRow[] {
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
  const priorMap = new Map(
    priorSamples.map((sample, index) => [index, sample.queue_length]),
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
      prior: priorMap.get(index),
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
    zone: zoneNames.get(alert.zone_id ?? "") ?? alert.zone_id ?? "—",
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
  };
}

function mapLiveStatus(status: string): LiveCameraStatus {
  if (status === "online") return "online";
  if (status === "error") return "error";
  return "offline";
}

export function mapLiveCamera(
  camera: BackendCamera,
  status?: BackendCameraStatus | null,
): Camera {
  return {
    id: camera.id,
    name: camera.name,
    location: camera.location ?? "",
    status: mapLiveStatus(status?.status ?? camera.status),
    frameUrl: camera.source_type === "recorded" ? null : (camera.rtsp_url ?? null),
    occupancy: status?.current_occupancy ?? 0,
    entriesToday: 0,
    exitsToday: 0,
    boundingBoxes: [],
    zones: [],
    countingLines: [],
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
    analyticsModules: ["entry-exit", "occupancy", "zones", "dwell", "heatmap", "queue"],
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

  return {
    id: zoneId,
    zone: zoneName,
    visits: visitors,
    dwellSec: avgDwell,
    occupancy: Math.min(100, peakVisitors),
    trend: "flat",
    trendPct: 0,
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
