# Shared Scope Selector - Implementation Summary

## Overview

Built a reusable, configurable scope selector component + hooks that implements the three-level cascade:
**Store (display only) → Camera dropdown → Zone dropdown**

This is independent of any page's existing layout, comparison/date-range UI, or global ScopeContext. Each page can configure it differently and use it locally.

## Files Created

### 1. **Hook: `use-scope-selector.ts`**
📍 Location: `frontend/lib/scope/use-scope-selector.ts`

**Core logic** — all the validation, filtering, and selection management.

**Exports:**
- `ScopeSelectorConfig` — configuration interface with all options
- `ScopeSelection` — the shape pages will use for API query params: `{ store_id, camera_id: string | "all", zone_id: string | "all" | undefined }`
- `useScopeSelector(store, config)` — hook that returns utilities for building UI

**Configuration options:**
- `excludeQueueZones: boolean` — exclude queue/checkout/waiting zones from dropdown + "All Zones" aggregation
- `onlyQueueZones: boolean` — inverse: show ONLY queue-type zones
- `showZoneSelector: boolean` — when false, Zone dropdown doesn't render (for Occupancy, etc.)
- `showCameraAllOption: boolean` — when false, Camera has no "All Cameras" option (for Heatmap)

**Key behaviors:**
- Zone dropdown is **disabled** (not just empty) when Camera = "All Cameras"
- Zone value forced to "all" when camera is "all"
- Queue zone filtering includes: `queue`, `checkout`, `waiting` (case-insensitive)

### 2. **Component: `scope-selector.tsx`**
📍 Location: `frontend/components/analytics/scope-selector.tsx`

**React component** — the actual UI (Store display + Camera + Zone dropdowns).

**Props:**
- `store: Store | null` — current store with cameras/zones
- `selectedCamera: string | "all"` — controlled by parent
- `selectedZone: string | "all" | undefined` — controlled by parent
- `onCameraChange: (id) => void` — called when camera changes
- `onZoneChange: (id) => void` — called when zone changes
- `config?: ScopeSelectorConfig` — optional configuration
- `className?: string` — optional CSS classes

**Styles:** Uses Tailwind + consistent design system tokens (border-input, bg-card, etc.)

### 3. **Hook: `use-local-scope-selection.ts`**
📍 Location: `frontend/lib/scope/use-local-scope-selection.ts`

**Convenience hook** for pages that want to manage their own local scope state (independent from global ScopeContext).

**Returns:**
- `camera: string | "all"` — validated camera selection
- `zone: string | "all" | undefined` — validated zone selection
- `setCamera: (id) => void` — update camera (auto-resets zone)
- `setZone: (id) => void` — update zone
- `selection: ScopeSelection | null` — ready for API calls
- `cameraOptions, getZoneOptions` — helpers

## Type Changes

Updated `ScopeZone` type to include zone type for filtering:

```typescript
// frontend/lib/types.ts
export type ScopeZone = { id: string; name: string; type?: string };
```

Also updated the mapper (`frontend/lib/api/mappers.ts`) to include zone type when building the organization tree.

## Usage Example

### Using the component directly (controlled):
```tsx
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useState } from "react";

export function MyAnalyticsPage() {
  const [camera, setCamera] = useState<string | "all">("all");
  const [zone, setZone] = useState<string | "all" | undefined>("all");
  
  return (
    <ScopeSelector
      store={store}
      selectedCamera={camera}
      selectedZone={zone}
      onCameraChange={setCamera}
      onZoneChange={setZone}
      config={{
        excludeQueueZones: true,     // Don't show queue zones
        showZoneSelector: true,       // Show zone dropdown
        showCameraAllOption: true,    // Show "All Cameras" option
      }}
    />
  );
}
```

### Using the local scope hook (simpler for page-specific scope):
```tsx
import { useLocalScopeSelection } from "@/lib/scope/use-local-scope-selection";
import { ScopeSelector } from "@/components/analytics/scope-selector";

export function MyQueuesPage() {
  const store = /* from context */;
  const { camera, zone, setCamera, setZone, selection } = useLocalScopeSelection(store, {
    onlyQueueZones: true,  // Only queue zones
    showCameraAllOption: false,  // Force specific camera
  });
  
  // selection is now ready to pass to API: { store_id, camera_id, zone_id }
  
  return (
    <ScopeSelector
      store={store}
      selectedCamera={camera}
      selectedZone={zone}
      onCameraChange={setCamera}
      onZoneChange={setZone}
      config={{ onlyQueueZones: true, showCameraAllOption: false }}
    />
  );
}
```

## What's NOT Changed

✅ No existing page code touched
✅ No global ScopeContext modified
✅ No comparison/date-range UI touched
✅ Fully backward compatible

## Next Steps (when wiring into pages)

For each analytics page that needs scope selection:

1. Import the component and hook
2. Add local state: `[camera, setCamera]`, `[zone, setZone]`
3. Add `<ScopeSelector>` to the page layout
4. Configure options per page's needs (`excludeQueueZones`, `showZoneSelector`, etc.)
5. Build API query params from the selection: `{ store_id, camera_id, zone_id }`
6. Pass query params to your existing `fetchData()` function

## Verification

✅ Code compiles (TypeScript types are correct)
✅ All configuration options implemented
✅ Zone filtering logic handles queue types correctly
✅ Component properly disables/hides zone dropdown based on camera selection
✅ Selection shape matches API contract: `{ store_id, camera_id, zone_id }`
✅ Exports are clean and well-documented
