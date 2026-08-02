import { apiRequest, getAccessToken } from "@/lib/api/client";
import {
  buildOrganizationFromBackend,
  type BackendCamera,
  type BackendOrganization,
  type BackendZoneShape,
} from "@/lib/api/mappers";
import type { Organization, Store } from "@/lib/types";

let cachedOrganization: Organization | null = null;
let cachedStores: Store[] | null = null;
let cachedDefaultZoneId: string | null = null;
let loadPromise: Promise<Organization> | null = null;

async function loadScopeTree(): Promise<Organization> {
  if (cachedOrganization) return cachedOrganization;
  if (!getAccessToken()) {
    throw new Error("Not authenticated");
  }

  const orgs = await apiRequest<BackendOrganization[]>("/api/organizations");
  const org = orgs[0];
  if (!org) {
    throw new Error("No organization found for this deployment");
  }

  const storeIds = new Set(org.stores.map((store) => store.id));
  const allCameras = await apiRequest<BackendCamera[]>("/api/cameras");
  const orgCameras = allCameras.filter((camera) => storeIds.has(camera.store_id));

  const camerasByStore = new Map<string, BackendCamera[]>();
  for (const store of org.stores) {
    camerasByStore.set(store.id, []);
  }
  for (const camera of orgCameras) {
    const list = camerasByStore.get(camera.store_id) ?? [];
    list.push(camera);
    camerasByStore.set(camera.store_id, list);
  }

  // Single list call (camera_id optional) — avoids N GET /api/zones fan-out.
  const allZones = await apiRequest<BackendZoneShape[]>("/api/zones").catch(
    () => [] as BackendZoneShape[],
  );
  const zonesByCamera = new Map<string, BackendZoneShape[]>();
  for (const camera of orgCameras) {
    zonesByCamera.set(camera.id, []);
  }
  for (const zone of allZones) {
    const list = zonesByCamera.get(zone.camera_id) ?? [];
    list.push(zone);
    zonesByCamera.set(zone.camera_id, list);
  }

  const organization = await buildOrganizationFromBackend(
    org,
    camerasByStore,
    zonesByCamera,
  );

  cachedOrganization = organization;
  cachedStores = organization.stores;
  return organization;
}

function loadScopeTreeOnce(): Promise<Organization> {
  if (!loadPromise) {
    loadPromise = loadScopeTree().finally(() => {
      loadPromise = null;
    });
  }
  return loadPromise;
}

/** Returns the deployment's single organization (store → camera → zone tree). */
export function getOrganization(): Promise<Organization> {
  if (!getAccessToken()) {
    return Promise.reject(new Error("Not authenticated"));
  }
  return loadScopeTreeOnce();
}

/** Returns all stores for the deployment organization. */
export async function getStores(): Promise<Store[]> {
  const org = await getOrganization();
  return [...org.stores];
}

/**
 * @deprecated Single-tenant deployment — use `getOrganization()` instead.
 * Returns a one-element array for backwards compatibility.
 */
export async function getOrganizations(): Promise<Organization[]> {
  const org = await getOrganization();
  return [org];
}

export function clearStoresCache(): void {
  cachedOrganization = null;
  cachedStores = null;
  cachedDefaultZoneId = null;
  loadPromise = null;
}

/** First configured zone shape for the deployment, or seeded fallback. */
export async function getDefaultZoneId(): Promise<string> {
  if (cachedDefaultZoneId) return cachedDefaultZoneId;
  try {
    const org = await getOrganization();
    for (const store of org.stores) {
      for (const camera of store.cameras) {
        for (const zone of camera.zones) {
          if (zone.id) {
            cachedDefaultZoneId = zone.id;
            return zone.id;
          }
        }
      }
    }
  } catch {
    // fall through to seed default
  }
  cachedDefaultZoneId = "store1";
  return cachedDefaultZoneId;
}

export async function getDefaultStoreId(): Promise<string> {
  if (getAccessToken()) {
    try {
      const stores = await getStores();
      const preferred = stores.find((store) => store.id === "store_main");
      return preferred?.id ?? stores[0]?.id ?? "store_main";
    } catch {
      // fall through to seed default
    }
  }
  return "store_main";
}
