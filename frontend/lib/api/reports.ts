import { apiRequest, apiRequestBlob, downloadBlob, ApiClientError } from "@/lib/api/client";
import {
  mapReportPayload,
  reportTypeToBackend,
  type BackendCamera,
  type BackendReportPayload,
} from "@/lib/api/mappers";
import { getStores } from "@/lib/api/stores";
import { REPORT_TYPES as STATIC_REPORT_TYPES } from "@/lib/reports-data";
import type { ReportData, ReportType } from "@/lib/types";

export type ReportStoreOption = { id: string; name: string };
export type ReportCameraOption = {
  id: string;
  name: string;
  analytics_modules?: string[];
};

/** Hydrated from GET /api/stores on first report call. */
export const STORES: ReportStoreOption[] = [];

/** Hydrated from GET /api/cameras on first report call. */
export const CAMERAS: ReportCameraOption[] = [];

export const REPORT_TYPES = STATIC_REPORT_TYPES;

export type ReportFormat = "json" | "csv" | "pdf";

export interface GetReportParams {
  format: ReportFormat;
  from: string;
  to: string;
  store_id: string;
  camera_id?: string;
  compare?: boolean;
}

export interface ReportResult extends ReportData {
  format: ReportFormat;
  store_id: string;
}

const REPORT_TYPE_MODULE: Record<ReportType, string> = {
  traffic: "entry_exit",
  occupancy: "occupancy",
  zones: "zones",
  "dwell-time": "dwell",
  queues: "queues",
};

const MODULE_LABELS: Record<string, string> = {
  entry_exit: "Entry/Exit",
  occupancy: "Occupancy",
  zones: "Zone Analytics",
  dwell: "Dwell Analytics",
  heatmap: "Heatmap",
  queues: "Queue Analytics",
};

let optionsHydrated = false;

export async function ensureReportOptions(): Promise<void> {
  if (optionsHydrated) return;
  const [stores, cameras] = await Promise.all([
    getStores(),
    apiRequest<BackendCamera[]>("/api/cameras"),
  ]);
  STORES.length = 0;
  STORES.push(...stores.map((store) => ({ id: store.id, name: store.name })));
  CAMERAS.length = 0;
  CAMERAS.push(
    ...cameras.map((camera) => ({
      id: camera.id,
      name: camera.name,
      analytics_modules: camera.analytics_modules ?? [],
    })),
  );
  optionsHydrated = true;
}

export function reportModuleForType(reportType: ReportType): string {
  return REPORT_TYPE_MODULE[reportType];
}

export function moduleLabel(module: string): string {
  return MODULE_LABELS[module] ?? module;
}

export function cameraSupportsReportType(
  cameraId: string,
  reportType: ReportType,
): boolean {
  const camera = CAMERAS.find((item) => item.id === cameraId);
  const module = REPORT_TYPE_MODULE[reportType];
  return camera?.analytics_modules?.includes(module) ?? false;
}

export function reportModuleDisabledMessage(
  cameraId: string,
  reportType: ReportType,
): string | null {
  if (!cameraId) return null;
  const camera = CAMERAS.find((item) => item.id === cameraId);
  if (!camera) return null;
  const module = REPORT_TYPE_MODULE[reportType];
  if (camera.analytics_modules?.includes(module)) return null;
  return `${MODULE_LABELS[module] ?? module} is not enabled for camera "${camera.name}".`;
}

async function resolveStoreName(store_id: string): Promise<string> {
  await ensureReportOptions();
  return STORES.find((store) => store.id === store_id)?.name ?? store_id;
}

function reportQuery(
  params: Omit<GetReportParams, "format">,
): Record<string, string> {
  const query: Record<string, string> = {
    store_id: params.store_id,
    from: params.from,
    to: params.to,
    compare: params.compare === false ? "false" : "true",
  };
  if (params.camera_id) {
    query.camera_id = params.camera_id;
  }
  return query;
}

/** Fetch the backend-rendered PDF (same bytes as Export PDF) without downloading. */
export async function fetchReportPdfBlob(
  type: ReportType,
  { from, to, store_id, camera_id }: Omit<GetReportParams, "format">,
): Promise<Blob> {
  await ensureReportOptions();
  const backendType = reportTypeToBackend(type);
  const blob = await apiRequestBlob(`/api/reports/${backendType}/export`, {
    query: { ...reportQuery({ from, to, store_id, camera_id }), format: "pdf" },
  });
  if (blob.type === "application/pdf") return blob;
  return new Blob([blob], { type: "application/pdf" });
}

export async function getReport(
  type: ReportType,
  { format, from, to, store_id, camera_id }: GetReportParams,
): Promise<ReportResult> {
  await ensureReportOptions();
  const backendType = reportTypeToBackend(type);
  const storeName = await resolveStoreName(store_id);

  if (format === "csv" || format === "pdf") {
    const blob = await apiRequestBlob(`/api/reports/${backendType}/export`, {
      query: { ...reportQuery({ from, to, store_id, camera_id }), format },
    });
    downloadBlob(blob, `${backendType}.${format}`);
    return {
      title: `${type} export`,
      storeName,
      dateRange: `${from} — ${to}`,
      kpis: [],
      chartData: [],
      tableData: [],
      tableColumns: [],
      format,
      store_id,
    };
  }

  const payload = await apiRequest<BackendReportPayload>(
    `/api/reports/${backendType}`,
    {
      query: reportQuery({ from, to, store_id, camera_id }),
    },
  );

  return {
    ...mapReportPayload(payload, storeName),
    format,
    store_id,
  };
}

export function isReportModuleDisabledError(err: unknown): boolean {
  return err instanceof ApiClientError && err.code === "analytics_module_disabled";
}
