"use client";

import { useMemo } from "react";
import type { Store, ScopeCamera } from "@/lib/types";

export interface ScopeSelectorConfig {
  /** When true, exclude queue-type zones (queue/checkout/waiting) from dropdown and "All Zones" aggregation. */
  excludeQueueZones?: boolean;
  /** When true, show ONLY queue-type zones (inverse of excludeQueueZones). */
  onlyQueueZones?: boolean;
  /** When false, Zone dropdown doesn't render (used for pages that don't deal with zones). */
  showZoneSelector?: boolean;
  /** When false, Camera dropdown has no "All Cameras" option (used for Heatmap). */
  showCameraAllOption?: boolean;
}

export interface ScopeSelection {
  store_id: string;
  camera_id: string | "all";
  zone_id: string | "all" | undefined;
}

/**
 * Determines if a zone type is a queue-type zone.
 * Queue zones: "checkout_queue" (aggregated type for queue/checkout/waiting)
 */
function isQueueZoneType(zoneType: string | undefined): boolean {
  if (!zoneType) return false;
  return zoneType.toLowerCase() === "checkout_queue";
}

/**
 * Hook to manage scope selector state (store → camera → zone cascade).
 * Handles filtering, validation, and configuration options.
 *
 * @param store - Current store (with cameras and zones)
 * @param config - Configuration for zone filtering and UI visibility
 * @returns Hook state object with selection, handlers, and available options
 */
export function useScopeSelector(
  store: Store | null,
  config: ScopeSelectorConfig = {},
) {
  const {
    excludeQueueZones = false,
    onlyQueueZones = false,
    showZoneSelector = true,
    showCameraAllOption = true,
  } = config;

  // Derive camera list from store
  const camerasInStore = useMemo(() => store?.cameras ?? [], [store]);

  // Available camera options for dropdown
  const cameraOptions = useMemo(() => {
    const options: Array<{ id: string | "all"; name: string }> = [];
    if (showCameraAllOption) {
      options.push({ id: "all", name: "All Cameras" });
    }
    for (const camera of camerasInStore) {
      options.push({ id: camera.id, name: camera.name });
    }
    return options;
  }, [camerasInStore, showCameraAllOption]);

  // Resolve which camera we're looking at (for zone dropdown population)
  const resolveCamera = (cameraId: string | "all"): ScopeCamera | null => {
    if (cameraId === "all") return null;
    return camerasInStore.find((c) => c.id === cameraId) ?? null;
  };

  // Filter zones based on config options
  const filterZones = (
    camera: ScopeCamera | null,
  ): Array<{ id: string; name: string; type?: string }> => {
    if (!camera) return [];

    let zones = camera.zones;

    if (excludeQueueZones) {
      zones = zones.filter((z) => !isQueueZoneType(z.type));
    } else if (onlyQueueZones) {
      zones = zones.filter((z) => isQueueZoneType(z.type));
    }

    return zones.map((z) => ({ id: z.id, name: z.name, type: z.type }));
  };

  // Available zone options (depends on selected camera)
  const getZoneOptions = (
    cameraId: string | "all",
  ): Array<{ id: string | "all"; name: string }> => {
    const options: Array<{ id: string | "all"; name: string }> = [];

    // If no specific camera selected, zones are disabled
    if (cameraId === "all") {
      return options;
    }

    const camera = resolveCamera(cameraId);
    if (!camera) {
      return options;
    }

    // Add "All Zones" option if at least one zone exists
    const filteredZones = filterZones(camera);
    if (filteredZones.length > 0) {
      options.push({ id: "all", name: "All Zones" });
    }

    for (const zone of filteredZones) {
      options.push({ id: zone.id, name: zone.name });
    }

    return options;
  };

  /**
   * Validate and resolve zone_id based on current camera selection.
   * Returns:
   * - undefined if showZoneSelector is false
   * - "all" if camera is "all" (zones don't make sense without a specific camera)
   * - the provided zone_id if valid for the selected camera
   * - "all" as fallback
   */
  const resolveZoneId = (
    cameraId: string | "all",
    requestedZoneId: string | "all" | null,
  ): string | "all" | undefined => {
    if (!showZoneSelector) {
      return undefined;
    }

    if (cameraId === "all") {
      return "all";
    }

    const zoneOptions = getZoneOptions(cameraId);
    if (zoneOptions.length === 0) {
      return "all";
    }

    // If zone is explicitly "all" or empty, return "all"
    if (!requestedZoneId || requestedZoneId === "all") {
      return "all";
    }

    // Verify requested zone exists in filtered list
    if (zoneOptions.some((z) => z.id === requestedZoneId)) {
      return requestedZoneId;
    }

    // Fallback to "all" if zone not found
    return "all";
  };

  /**
   * Validate store and camera selections, apply constraints.
   *
   * @returns Object with validated selections and available options
   */
  const getValidatedState = (
    cameraId: string | "all",
    zoneId: string | "all" | null,
  ) => {
    const validatedCameraId =
      camerasInStore.length === 0
        ? "all"
        : cameraId === "all"
          ? "all"
          : camerasInStore.some((c) => c.id === cameraId)
            ? cameraId
            : showCameraAllOption
              ? "all"
              : camerasInStore[0]?.id ?? "all";

    const validatedZoneId = resolveZoneId(
      validatedCameraId,
      typeof zoneId === "string" ? zoneId : null,
    );

    return {
      camera_id: validatedCameraId,
      zone_id: validatedZoneId,
      zoneOptions: getZoneOptions(validatedCameraId),
      cameraOptions,
    };
  };

  /**
   * Build the final scope selection to pass to API.
   */
  const buildSelection = (
    cameraId: string | "all",
    zoneId: string | "all" | undefined,
  ): ScopeSelection => {
    if (!store) {
      throw new Error("Store is required to build selection");
    }

    return {
      store_id: store.id,
      camera_id: cameraId,
      zone_id: zoneId,
    };
  };

  return {
    cameraOptions,
    getZoneOptions,
    getValidatedState,
    buildSelection,
    resolveCamera,
    isZoneSelectorVisible: showZoneSelector,
    isCameraAllOptionAvailable: showCameraAllOption,
  };
}
