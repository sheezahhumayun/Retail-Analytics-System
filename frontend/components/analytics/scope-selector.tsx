"use client";

import { useMemo } from "react";
import type { Store } from "@/lib/types";
import {
  type ScopeSelectorConfig,
  type ScopeSelection,
  useScopeSelector,
} from "@/lib/scope/use-scope-selector";

interface ScopeSelectorProps {
  /** Current store to select from. */
  store: Store | null;
  /** Currently selected camera ("all" or a camera id). */
  selectedCamera: string | "all";
  /** Currently selected zone ("all", a zone id, or undefined if zones hidden). */
  selectedZone: string | "all" | undefined;
  /** Called when camera selection changes. */
  onCameraChange: (cameraId: string | "all") => void;
  /** Called when zone selection changes. */
  onZoneChange: (zoneId: string | "all" | undefined) => void;
  /** Configuration for zone filtering and visibility. */
  config?: ScopeSelectorConfig;
  /** CSS class to apply to the root container. */
  className?: string;
}

/**
 * Shared, reusable scope selector component.
 * Three-level cascade: Store (display only) → Camera dropdown → Zone dropdown.
 * Zone dropdown is disabled when Camera = "All Cameras".
 *
 * Features:
 * - Queue zone filtering (excludeQueueZones, onlyQueueZones)
 * - Optional zone selector (showZoneSelector)
 * - Optional "All Cameras" option (showCameraAllOption)
 * - Automatic state validation and fallback
 *
 * Usage example:
 * ```tsx
 * const [camera, setCamera] = useState<string | "all">("all");
 * const [zone, setZone] = useState<string | "all" | undefined>("all");
 *
 * <ScopeSelector
 *   store={store}
 *   selectedCamera={camera}
 *   selectedZone={zone}
 *   onCameraChange={setCamera}
 *   onZoneChange={setZone}
 *   config={{
 *     excludeQueueZones: true,
 *     showZoneSelector: true,
 *     showCameraAllOption: true,
 *   }}
 * />
 *
 * const selection = buildSelection(camera, zone); // { store_id, camera_id, zone_id }
 * ```
 */
export function ScopeSelector({
  store,
  selectedCamera,
  selectedZone,
  onCameraChange,
  onZoneChange,
  config,
  className = "",
}: ScopeSelectorProps) {
  const selector = useScopeSelector(store, config);

  // Validate current selections and get options
  const { camera_id, zone_id, zoneOptions, cameraOptions } = useMemo(
    () => selector.getValidatedState(selectedCamera, selectedZone ?? null),
    [selector, selectedCamera, selectedZone],
  );

  // Sync validated state back to parent if they differ
  if (camera_id !== selectedCamera) {
    onCameraChange(camera_id);
  }
  if (zone_id !== selectedZone) {
    onZoneChange(zone_id);
  }

  const isZoneDisabled = camera_id === "all";

  return (
    <div className={`flex flex-col gap-3 ${className}`.trim()}>
      {/* Store display (read-only, no selector) */}
      {store && (
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">Store:</label>
          <div className="rounded-md border border-border bg-card px-3 py-2">
            <span className="text-sm text-foreground">{store.name}</span>
          </div>
        </div>
      )}

      {/* Camera dropdown */}
      <div className="flex items-center gap-2">
        <label htmlFor="scope-camera" className="text-sm font-medium text-foreground">
          Camera:
        </label>
        <select
          id="scope-camera"
          value={camera_id}
          onChange={(e) => onCameraChange(e.target.value as string | "all")}
          className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {cameraOptions.map((option) => (
            <option key={option.id} value={option.id}>
              {option.name}
            </option>
          ))}
        </select>
      </div>

      {/* Zone dropdown (conditionally shown and disabled) */}
      {selector.isZoneSelectorVisible && (
        <div className="flex items-center gap-2">
          <label htmlFor="scope-zone" className="text-sm font-medium text-foreground">
            Zone:
          </label>
          <select
            id="scope-zone"
            value={zone_id ?? ""}
            onChange={(e) => {
              const val = e.target.value;
              onZoneChange(val ? (val as string | "all") : undefined);
            }}
            disabled={isZoneDisabled}
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {zoneOptions.length === 0 ? (
              <option value="">No zones available</option>
            ) : (
              zoneOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))
            )}
          </select>
        </div>
      )}
    </div>
  );
}
