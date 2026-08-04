"use client";

import { useState, useCallback, useMemo } from "react";
import type { Store } from "@/lib/types";
import {
  type ScopeSelectorConfig,
  type ScopeSelection,
  useScopeSelector,
} from "@/lib/scope/use-scope-selector";

/**
 * Local scope state management hook for pages that manage their own store/camera/zone selection.
 * This is independent from the global ScopeContext — use this when a page needs
 * page-specific scope (e.g., page-level dropdowns that don't affect global scope).
 *
 * @param store - Current store (with cameras and zones)
 * @param config - Configuration for zone filtering and UI visibility
 * @returns Object with local selection state, handlers, and utilities
 *
 * @example
 * const { camera, zone, setCamera, setZone, selection } = useLocalScopeSelection(store, {
 *   excludeQueueZones: true,
 * });
 */
export function useLocalScopeSelection(
  store: Store | null,
  config: ScopeSelectorConfig = {},
) {
  const [camera, setCamera] = useState<string | "all">("all");
  const [zone, setZone] = useState<string | "all" | undefined>("all");

  const selector = useScopeSelector(store, config);

  // Validate current selections
  const { camera_id, zone_id } = useMemo(
    () => selector.getValidatedState(camera, zone ?? null),
    [selector, camera, zone],
  );

  // Sync validated state
  const handleCameraChange = useCallback((newCamera: string | "all") => {
    setCamera(newCamera);
    // When camera changes, reset zone to "all"
    setZone("all");
  }, []);

  const handleZoneChange = useCallback((newZone: string | "all" | undefined) => {
    setZone(newZone);
  }, []);

  // Build the selection object for API calls
  const selection = useMemo<ScopeSelection | null>(() => {
    if (!store) return null;
    return {
      store_id: store.id,
      camera_id: camera_id,
      zone_id: zone_id,
    };
  }, [store, camera_id, zone_id]);

  return {
    camera: camera_id,
    zone: zone_id,
    setCamera: handleCameraChange,
    setZone: handleZoneChange,
    selection,
    cameraOptions: selector.cameraOptions,
    getZoneOptions: selector.getZoneOptions,
  };
}
