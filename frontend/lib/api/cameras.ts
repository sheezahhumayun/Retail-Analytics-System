import {
  ANALYTICS_MODULES_LABELS,
  getStatusColor,
  getStatusLabel,
} from "@/lib/admin-cameras-data";
import type { AdminCamera, Camera, CameraStatus, Resolution } from "@/lib/types";
import type { BackendCamera, BackendCameraStatus } from "@/lib/api/mappers";
import {
  analyticsModulesToBackend,
  buildStoreNameMap,
  mapAdminCamera,
  mapLiveCamera,
  resolutionToBackend,
} from "@/lib/api/mappers";
import { apiRequest } from "@/lib/api/client";

export {
  ANALYTICS_MODULES_LABELS,
  getStatusColor,
  getStatusLabel,
};

/** Hydrated from GET /api/stores — populated on first cameras/users API call. */
export const STORES: string[] = [];

export type CreateCameraData = Omit<AdminCamera, "id">;
export type UpdateCameraData = Partial<AdminCamera>;

export type TestCameraSuccess = {
  status: "success";
  camera_id: string;
  resolution: Resolution;
  fps: number;
  latency_ms: number;
  camera_status?: CameraStatus;
};

export type TestCameraError = {
  status: "error";
  camera_id: string;
  error: string;
  camera_status?: CameraStatus;
};

export type TestCameraResult = TestCameraSuccess | TestCameraError;

export type ProcessCameraStatus = {
  camera_id: string;
  status: "idle" | "running" | "completed" | "failed";
  message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
};

let storeNameMap: Map<string, string> | null = null;

async function loadStoreNames(): Promise<Map<string, string>> {
  if (storeNameMap) return storeNameMap;
  const stores = await apiRequest<{ id: string; name: string }[]>("/api/stores");
  storeNameMap = buildStoreNameMap(
    stores.map((store) => ({ ...store, org_id: "" })),
  );
  STORES.length = 0;
  STORES.push(...stores.map((store) => store.name));
  return storeNameMap;
}

/** Populate `STORES` from the API — call before opening camera create/edit UI. */
export async function ensureStoresLoaded(): Promise<void> {
  await loadStoreNames();
}

async function resolveStoreId(storeName: string): Promise<string> {
  const stores = await apiRequest<{ id: string; name: string }[]>("/api/stores");
  return stores.find((store) => store.name === storeName)?.id ?? stores[0]?.id ?? "store_main";
}

export async function getCameras(): Promise<AdminCamera[]> {
  // Admin management view needs to see disabled cameras too (so they can be
  // re-enabled) — everywhere else (`getLiveCameras`, zone/report/analytics
  // camera pickers) intentionally uses the backend's default, which excludes
  // disabled/soft-deleted cameras.
  const [cameras, names] = await Promise.all([
    apiRequest<BackendCamera[]>("/api/cameras", { query: { include_disabled: true } }),
    loadStoreNames(),
  ]);
  return cameras.map((camera) =>
    mapAdminCamera(camera, names.get(camera.store_id) ?? camera.store_id),
  );
}

export async function getLiveCameras(): Promise<Camera[]> {
  const cameras = await apiRequest<BackendCamera[]>("/api/cameras");
  const live = cameras
    .filter((camera) => camera.status !== "disabled")
    .filter((camera) => (camera.source_type ?? "live") === "live");

  const statuses = await Promise.all(
    live.map((camera) =>
      apiRequest<BackendCameraStatus>(`/api/cameras/${camera.id}/status`).catch(
        () => null,
      ),
    ),
  );

  return live.map((camera, index) => mapLiveCamera(camera, statuses[index]));
}

export async function getCameraStatus(id: string): Promise<CameraStatus | null> {
  const status = await apiRequest<BackendCameraStatus>(
    `/api/cameras/${id}/status`,
  ).catch(() => null);
  if (!status) return null;
  return (status.status as CameraStatus) ?? "offline";
}

export async function createCamera(data: CreateCameraData): Promise<AdminCamera> {
  const store_id = await resolveStoreId(data.store);
  const body = {
    store_id,
    name: data.name,
    location: data.location,
    rtsp_url: data.rtspUrl,
    source_type: data.sourceType,
    camera_type: data.cameraType,
    resolution: resolutionToBackend(data.resolution),
    fps: data.fps,
    analytics_modules: analyticsModulesToBackend(data.analyticsModules),
  };
  const created = await apiRequest<BackendCamera>("/api/cameras", {
    method: "POST",
    body,
  });
  const names = await loadStoreNames();
  return mapAdminCamera(created, names.get(created.store_id) ?? created.store_id);
}

export async function updateCamera(
  id: string,
  data: UpdateCameraData,
): Promise<AdminCamera | null> {
  const body: Record<string, unknown> = {};
  if (data.store) body.store_id = await resolveStoreId(data.store);
  if (data.name !== undefined) body.name = data.name;
  if (data.location !== undefined) body.location = data.location;
  if (data.rtspUrl !== undefined) body.rtsp_url = data.rtspUrl;
  if (data.sourceType !== undefined) body.source_type = data.sourceType;
  if (data.cameraType !== undefined) body.camera_type = data.cameraType;
  if (data.resolution !== undefined) body.resolution = resolutionToBackend(data.resolution);
  if (data.fps !== undefined) body.fps = data.fps;
  if (data.analyticsModules !== undefined) {
    body.analytics_modules = analyticsModulesToBackend(data.analyticsModules);
  }
  if (data.enabled !== undefined) {
    // Manual admin enable/disable switch — see backend CameraUpdate.status.
    // `online`/`error` are health-probe-derived and intentionally not settable
    // here; re-enabling goes to `offline` and the next health check cycle
    // resolves it to `online`/`error`.
    body.status = data.enabled ? "offline" : "disabled";
  }

  try {
    const updated = await apiRequest<BackendCamera>(`/api/cameras/${id}`, {
      method: "PUT",
      body,
    });
    const names = await loadStoreNames();
    return mapAdminCamera(updated, names.get(updated.store_id) ?? updated.store_id);
  } catch {
    return null;
  }
}

/**
 * Soft-disables the camera (`DELETE /api/cameras/{id}` sets `status=disabled`
 * server-side — historical analytics data is preserved, nothing is hard
 * deleted). Returns the persisted camera (now `status: "disabled"`) so the
 * caller can reflect *actual* server state rather than optimistically
 * removing the row — a plain `filter()` removal previously caused the
 * "reappears after reload" bug, since the row was never really gone.
 */
export async function deleteCamera(id: string): Promise<AdminCamera | null> {
  try {
    const deleted = await apiRequest<BackendCamera>(`/api/cameras/${id}`, { method: "DELETE" });
    const names = await loadStoreNames();
    return mapAdminCamera(deleted, names.get(deleted.store_id) ?? deleted.store_id);
  } catch {
    return null;
  }
}

export async function processCameraVideo(id: string): Promise<ProcessCameraStatus> {
  return apiRequest<ProcessCameraStatus>(`/api/cameras/${id}/process`, {
    method: "POST",
  });
}

export async function getCameraProcessStatus(id: string): Promise<ProcessCameraStatus> {
  return apiRequest<ProcessCameraStatus>(`/api/cameras/${id}/process-status`);
}

export async function testCamera(id: string): Promise<TestCameraResult> {
  const response = await apiRequest<{
    status: "success" | "error";
    latency_ms?: number | null;
    resolution?: string | null;
    fps?: number | null;
    message?: string | null;
    camera_status?: CameraStatus | null;
  }>(`/api/cameras/${id}/test`, { method: "POST" });

  const cameraStatus = response.camera_status as CameraStatus | undefined;

  if (response.status === "error") {
    return {
      status: "error",
      camera_id: id,
      error: response.message ?? "Camera test failed",
      camera_status: cameraStatus,
    };
  }

  return {
    status: "success",
    camera_id: id,
    resolution: (response.resolution as Resolution) ?? "1080p",
    fps: response.fps ?? 0,
    latency_ms: response.latency_ms ?? 0,
    camera_status: cameraStatus,
  };
}
