import { apiRequest, getAccessToken } from "@/lib/api/client";
import type {
  BackendProcessingLineSnapshot,
  BackendProcessingZoneSnapshot,
} from "@/lib/api/mappers";

export type ProcessingRunSummary = {
  id: string;
  camera_id: string;
  status: "running" | "completed" | "failed";
  started_at: string;
  finished_at?: string | null;
  message?: string | null;
  source_path: string;
};

export type ProcessingRunDetail = ProcessingRunSummary & {
  zones_snapshot: BackendProcessingZoneSnapshot[];
  lines_snapshot: BackendProcessingLineSnapshot[];
};

export async function getProcessingRuns(cameraId: string): Promise<ProcessingRunSummary[]> {
  return apiRequest<ProcessingRunSummary[]>(
    `/api/cameras/${encodeURIComponent(cameraId)}/processing-runs`,
  );
}

export async function getProcessingRun(
  cameraId: string,
  runId: string,
): Promise<ProcessingRunDetail> {
  return apiRequest<ProcessingRunDetail>(
    `/api/cameras/${encodeURIComponent(cameraId)}/processing-runs/${encodeURIComponent(runId)}`,
  );
}

export function getProcessingRunVideoUrl(cameraId: string, runId: string): string | null {
  const token = getAccessToken();
  if (!token) return null;
  const params = new URLSearchParams({ token });
  return `/api/cameras/${encodeURIComponent(cameraId)}/processing-runs/${encodeURIComponent(runId)}/video?${params.toString()}`;
}
