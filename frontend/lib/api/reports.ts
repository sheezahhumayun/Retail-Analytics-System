import { apiRequest, apiRequestBlob, downloadBlob } from "@/lib/api/client";
import {
  mapReportPayload,
  reportTypeToBackend,
  type BackendReportPayload,
} from "@/lib/api/mappers";
import { getStores } from "@/lib/api/stores";
import { REPORT_TYPES as STATIC_REPORT_TYPES } from "@/lib/reports-data";
import type { ReportData, ReportType } from "@/lib/types";

export type ReportStoreOption = { id: string; name: string };
export type ReportCameraOption = { id: string; name: string };

/** Hydrated from GET /api/stores on first report call. */
export const STORES: ReportStoreOption[] = [
  { id: "store_main", name: "Main Street Store" },
];

/** Hydrated from GET /api/cameras on first report call. */
export const CAMERAS: ReportCameraOption[] = [
  { id: "entrance", name: "Entrance Camera" },
  { id: "town", name: "Town Floor Camera" },
  { id: "shop", name: "Shop Floor Camera" },
];

export const REPORT_TYPES = STATIC_REPORT_TYPES;

export type ReportFormat = "json" | "csv" | "pdf";

export interface GetReportParams {
  format: ReportFormat;
  from: string;
  to: string;
  store_id: string;
}

export interface ReportResult extends ReportData {
  format: ReportFormat;
  store_id: string;
}

let optionsHydrated = false;

async function ensureReportOptions(): Promise<void> {
  if (optionsHydrated) return;
  const [stores, cameras] = await Promise.all([
    getStores(),
    apiRequest<{ id: string; name: string }[]>("/api/cameras"),
  ]);
  STORES.length = 0;
  STORES.push(...stores.map((store) => ({ id: store.id, name: store.name })));
  CAMERAS.length = 0;
  CAMERAS.push(...cameras.map((camera) => ({ id: camera.id, name: camera.name })));
  optionsHydrated = true;
}

async function resolveStoreName(store_id: string): Promise<string> {
  await ensureReportOptions();
  return STORES.find((store) => store.id === store_id)?.name ?? store_id;
}

export async function getReport(
  type: ReportType,
  { format, from, to, store_id }: GetReportParams,
): Promise<ReportResult> {
  await ensureReportOptions();
  const backendType = reportTypeToBackend(type);
  const storeName = await resolveStoreName(store_id);

  if (format === "csv" || format === "pdf") {
    const blob = await apiRequestBlob(`/api/reports/${backendType}/export`, {
      query: { store_id, from, to, format },
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
      query: { store_id, from, to },
    },
  );

  return {
    ...mapReportPayload(payload, storeName),
    format,
    store_id,
  };
}
