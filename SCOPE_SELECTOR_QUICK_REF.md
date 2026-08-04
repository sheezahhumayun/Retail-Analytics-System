# Scope Selector — Quick Reference

## Import Paths

```typescript
// Hooks + types
import { useScopeSelector, useLocalScopeSelection } from "@/lib/scope";
import type { ScopeSelectorConfig, ScopeSelection } from "@/lib/scope";

// Component
import { ScopeSelector } from "@/components/analytics/scope-selector";
```

## Basic Usage (Copy-Paste Template)

```tsx
import { useLocalScopeSelection } from "@/lib/scope";
import { ScopeSelector } from "@/components/analytics/scope-selector";
import { useScope } from "@/lib/scope/ScopeContext";

export function AnalyticsPage() {
  const { store } = useScope();
  
  // Step 1: Set up local scope
  const { camera, zone, setCamera, setZone, selection } = useLocalScopeSelection(store, {
    // Customize as needed:
    excludeQueueZones: false,      // Set true to hide queue zones
    onlyQueueZones: false,         // Set true to show ONLY queue zones
    showZoneSelector: true,        // Set false to hide zone dropdown
    showCameraAllOption: true,     // Set false to require specific camera
  });

  // Step 2: Use selection for API calls
  const handleLoadData = async () => {
    if (!selection) return;
    
    const data = await yourApiFunction({
      store_id: selection.store_id,
      camera_id: selection.camera_id === "all" ? undefined : selection.camera_id,
      zone_id: selection.zone_id === "all" ? undefined : selection.zone_id,
      // ... other params
    });
    
    setData(data);
  };

  // Step 3: Render selector
  return (
    <div>
      <ScopeSelector
        store={store}
        selectedCamera={camera}
        selectedZone={zone}
        onCameraChange={setCamera}
        onZoneChange={setZone}
        config={{
          excludeQueueZones: false,
          onlyQueueZones: false,
          showZoneSelector: true,
          showCameraAllOption: true,
        }}
      />
      
      <button onClick={handleLoadData}>Load Data</button>
      {/* Display data... */}
    </div>
  );
}
```

## Config Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `excludeQueueZones` | boolean | false | Hide queue/checkout/waiting zones |
| `onlyQueueZones` | boolean | false | Show ONLY queue/checkout/waiting zones |
| `showZoneSelector` | boolean | true | Show zone dropdown (false for Occupancy) |
| `showCameraAllOption` | boolean | true | Show "All Cameras" (false for Heatmap) |

## Selection Object (What You Get)

```typescript
selection = {
  store_id: "store-1",           // Always a string
  camera_id: "cam-1" | "all",    // Specific camera or "all"
  zone_id: "zone-1" | "all" | undefined  // Zone, "all", or undefined
}
```

## API Query Params (How to Use It)

```typescript
// Zone endpoints
await getZones({
  zone_id: selection.zone_id ?? "all",  // Zone id or "all"
  from, to
});

// Camera endpoints
await getOccupancy({
  camera_id: selection.camera_id === "all" ? undefined : selection.camera_id,
  from, to
});

// Store endpoints
await getTraffic({
  store_id: selection.store_id,  // Always include store
  from, to
});
```

## Page Type → Config Matrix

| Page | Config |
|---|---|
| Zones | `{}` (defaults) |
| Dwell | `{}` (defaults) |
| Queues | `{ onlyQueueZones: true }` |
| Occupancy | `{ showZoneSelector: false }` |
| Heatmap | `{ showCameraAllOption: false, showZoneSelector: false }` |
| Zone Performance | `{}` (defaults) |

## Key Behaviors

- ✅ **Zone dropdown disabled** when Camera = "All Cameras"
- ✅ **Zone auto-resets to "all"** when you change camera
- ✅ **Queue filtering** includes: queue, checkout, waiting
- ✅ **Store always required** — no "all stores" option
- ✅ **Type-safe** — TypeScript catches wrong params

## Files in the Repo

| File | Purpose |
|---|---|
| `frontend/lib/scope/use-scope-selector.ts` | Core hook logic |
| `frontend/lib/scope/use-local-scope-selection.ts` | Local state hook (use this!) |
| `frontend/components/analytics/scope-selector.tsx` | React component |
| `frontend/lib/scope/index.ts` | Re-exports for convenience |
| `SCOPE_SELECTOR_README.md` | Full documentation |
| `SCOPE_SELECTOR_INTEGRATION.md` | Pattern examples per page |

## Troubleshooting

**Zone dropdown not showing?**
- Check `showZoneSelector: false` in config
- Check if camera = "all" (zones disabled in that case)

**"All Cameras" option not showing?**
- Check `showCameraAllOption: false` in config

**Queue zones still appearing?**
- Use `onlyQueueZones: true` instead of `excludeQueueZones: true`

**Selection is null?**
- `store` might be null — check `useScope()` is working

---

**Ready to integrate? Copy the template above and follow the pattern for your page type from `SCOPE_SELECTOR_INTEGRATION.md`**
