# Scope Selector Integration Guide

This document shows how each analytics page can integrate the new shared scope selector in the next phase.

## Architecture

The new scope selector is a **presentation layer** built on top of the existing data structure:
- It does NOT touch the global `ScopeContext` (that manages store/camera/zone globally)
- It does NOT modify page layouts or comparison/date-range UI
- It provides a **reusable cascade** that any page can configure and use independently

## Common Integration Patterns

### Pattern 1: Page with Local Scope + Global Context

**Scenario:** A page that has its own page-specific scope selection, but also respects global store context.

```tsx
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useLocalScopeSelection } from "@/lib/scope/use-local-scope-selection";
import { useScope } from "@/lib/scope/ScopeContext";

export function QueuesAnalyticsPage() {
  const { store } = useScope();  // Get store from global context
  
  // Manage camera/zone locally for this page only
  const { camera, zone, setCamera, setZone, selection } = useLocalScopeSelection(store, {
    onlyQueueZones: true,        // Config: only show queue zones
    showCameraAllOption: false,  // Config: force a specific camera
  });

  // Use selection for API calls
  const handleFetchData = async () => {
    if (!selection) return;
    const result = await getQueues({
      zone_id: selection.zone_id ?? "all",  // <- Uses scope selection
      from,
      to,
    });
    // ...
  };

  return (
    <div>
      {/* Scope selector — minimal, page-specific */}
      <ScopeSelector
        store={store}
        selectedCamera={camera}
        selectedZone={zone}
        onCameraChange={setCamera}
        onZoneChange={setZone}
        config={{ onlyQueueZones: true, showCameraAllOption: false }}
      />
      
      {/* Rest of page... */}
    </div>
  );
}
```

### Pattern 2: Page Without Zone Selection

**Scenario:** A page like Occupancy that doesn't have zones — only store/camera.

```tsx
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useLocalScopeSelection } from "@/lib/scope/use-local-scope-selection";
import { useScope } from "@/lib/scope/ScopeContext";

export function OccupancyPage() {
  const { store } = useScope();
  
  const { camera, setCamera, selection } = useLocalScopeSelection(store, {
    showZoneSelector: false,  // Hide zone dropdown entirely
  });

  const handleFetchData = async () => {
    if (!selection) return;
    const result = await getOccupancy({
      camera_id: selection.camera_id === "all" ? undefined : selection.camera_id,
      from,
      to,
    });
  };

  return (
    <div>
      <ScopeSelector
        store={store}
        selectedCamera={camera}
        selectedZone={undefined}  // Not used
        onCameraChange={setCamera}
        onZoneChange={() => {}}   // Not used
        config={{ showZoneSelector: false }}
      />
    </div>
  );
}
```

### Pattern 3: Heatmap (Forced Single Camera)

**Scenario:** Heatmap only works on a single camera, never "All Cameras".

```tsx
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useLocalScopeSelection } from "@/lib/scope/use-local-scope-selection";
import { useScope } from "@/lib/scope/ScopeContext";

export function HeatmapPage() {
  const { store } = useScope();
  
  const { camera, setCamera, selection } = useLocalScopeSelection(store, {
    showCameraAllOption: false,  // No "All Cameras" — force specific camera
    showZoneSelector: false,     // Also no zones
  });

  const handleRenderHeatmap = async () => {
    if (!selection || selection.camera_id === "all") {
      throw new Error("Heatmap requires a specific camera");
    }
    // Render heatmap for selection.camera_id
  };

  return (
    <div>
      <ScopeSelector
        store={store}
        selectedCamera={camera}
        selectedZone={undefined}
        onCameraChange={setCamera}
        onZoneChange={() => {}}
        config={{ showCameraAllOption: false, showZoneSelector: false }}
      />
      {/* Heatmap viewer */}
    </div>
  );
}
```

### Pattern 4: Zone Performance (Zones Only, All Cameras)

**Scenario:** Zone Performance spans all cameras in a store, showing zones across all cameras.

```tsx
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useLocalScopeSelection } from "@/lib/scope/use-local-scope-selection";
import { useScope } from "@/lib/scope/ScopeContext";

export function ZonePerformancePage() {
  const { store } = useScope();
  
  const { zone, setZone, selection } = useLocalScopeSelection(store, {
    // Don't restrict camera; we show all cameras' zones
    showCameraAllOption: true,  // Default: show "All Cameras"
    showZoneSelector: true,     // Show zones
  });

  const handleFetchData = async () => {
    if (!selection) return;
    const result = await getZonePerformance({
      store_id: selection.store_id,
      zone_id: selection.zone_id === "all" ? undefined : selection.zone_id,
    });
  };

  return (
    <div>
      <ScopeSelector
        store={store}
        selectedCamera="all"  // Always "All Cameras"
        selectedZone={zone}
        onCameraChange={() => {}}  // Ignore camera changes
        onZoneChange={setZone}
        config={{ showCameraAllOption: true, showZoneSelector: true }}
      />
    </div>
  );
}
```

## Config Matrix

| Page | excludeQueueZones | onlyQueueZones | showZoneSelector | showCameraAllOption |
|------|---|---|---|---|
| Zones | false | false | true | true |
| Dwell | false | false | true | true |
| Queues | false | true | true | true |
| Occupancy | — | — | false | true |
| Heatmap | — | — | false | false |
| Zone Performance | false | false | true | true |

## Selection Shape for API Calls

After selecting with `ScopeSelector`, you get:

```typescript
selection: ScopeSelection = {
  store_id: "store-downtown",
  camera_id: "cam-entrance" | "all",
  zone_id: "zone-1" | "all" | undefined  // undefined if showZoneSelector=false
}
```

Map this to your API call:
- **Zone endpoint** (expects single zone): `zone_id: selection.zone_id ?? "all"`
- **Camera endpoint** (optional camera): `camera_id: selection.camera_id === "all" ? undefined : selection.camera_id`
- **Store endpoint** (optional camera): always include `store_id`

## Key Behaviors to Remember

1. **Zone disabled when Camera = "All Cameras"** — The UI shows this visually (greyed out).
2. **Zone resets when Camera changes** — If you change camera, zone is forced back to "all".
3. **Queue zone filtering** — Applies to dropdown options AND "All Zones" aggregation.
4. **Type safety** — TypeScript ensures you handle `string | "all" | undefined` correctly.
5. **No page mutation** — The component does not modify the page's layout or existing UI.

## How It Integrates with Existing Code

**Before:** Each page had bespoke `storeId`, `cameraId`, `zoneId` logic.

**After:** Pages use the standardized `ScopeSelector` + `useLocalScopeSelection`, then build API params from the returned `selection` object.

**Example transformation:**
```tsx
// OLD: Page manages its own dropdowns
const [pageCamera, setPageCamera] = useState(null);
// ... custom validation, fallback logic, zone filtering ...

// NEW: Use the hook
const { camera, zone, selection } = useLocalScopeSelection(store, config);
// ... all validation, filtering, fallback built-in ...
```

## Testing Your Integration

1. **Render the component** with different `config` options
2. **Verify dropdowns** show/hide correctly
3. **Change camera** → zone should reset to "all" and zone dropdown should update
4. **Filter zones** → if `excludeQueueZones=true`, queue zones should not appear
5. **Build selection** and pass to your API function
6. **Verify API params** match the contract (store_id always set, camera_id/"all", zone_id/"all"/undefined)

## Files to Reference

- **Hook logic:** `frontend/lib/scope/use-scope-selector.ts`
- **Local state hook:** `frontend/lib/scope/use-local-scope-selection.ts`
- **Component:** `frontend/components/analytics/scope-selector.tsx`
- **Central exports:** `frontend/lib/scope/index.ts`
- **Types:** `frontend/lib/types.ts` (ScopeZone, ScopeCamera, Store, ScopeSelection)

## When You're Ready to Integrate a Page

1. Copy the pattern that matches your page's use case (above)
2. Import `ScopeSelector` and `useLocalScopeSelection`
3. Add the component to your page layout
4. Update your `getData()` function to use `selection` instead of hardcoded scope
5. Test that dropdowns work and API calls receive correct params
6. Commit!
