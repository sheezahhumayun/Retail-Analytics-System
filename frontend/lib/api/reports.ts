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
}

export interface ReportResult extends ReportData {
  format: ReportFormat;
  store_id: string;
}

let optionsHydrated = false;

export async function ensureReportOptions(): Promise<void> {
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

/** Fetch the backend-rendered PDF (same bytes as Export PDF) without downloading. */
export async function fetchReportPdfBlob(
  type: ReportType,
  { from, to, store_id }: Omit<GetReportParams, "format">,
): Promise<Blob> {
  await ensureReportOptions();
  const backendType = reportTypeToBackend(type);
  const blob = await apiRequestBlob(`/api/reports/${backendType}/export`, {
    query: { store_id, from, to, format: "pdf" },
  });
  // Ensure iframe/embed treats the blob as PDF even if MIME sniffing is flaky.
  if (blob.type === "application/pdf") return blob;
  return new Blob([blob], { type: "application/pdf" });
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
