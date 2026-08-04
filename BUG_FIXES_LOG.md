# Bug Fixes — Analytics API Integration

## BUG 1: Missing `store_id` in Overview Page Dwell/Queues Calls (422 Error)

**Root Cause:** 
- `getOverviewKpis()` was calling `/api/analytics/dwell` and `/api/analytics/queues` with only `zone_id`, `from`, `to`, `compare` params
- Backend endpoints require `store_id` as a non-optional parameter
- Missing param → FastAPI validation error → 422 Unprocessable Content

**Fix:**
- Updated `getOverviewKpis()` in `frontend/lib/api/analytics.ts` to include `store_id` in both dwell and queues API calls
- Lines 529, 536: Changed `query: { zone_id, from, to, compare }` → `query: { store_id, zone_id, from, to, compare }`

**Impact:** Overview page no longer emits 422 errors for dwell/queues widgets

## BUG 2a: Missing `store_id` in Zone Performance Zones Calls (422 Error)

**Root Cause:**
- `getZonePerformance()` was calling `/api/analytics/zones` with only `zone_id`, `from`, `to`, `compare` params
- Backend endpoint requires `store_id` as non-optional parameter
- Missing param → 422 Unprocessable Content

**Fix:**
- Updated `getZonePerformance()` in `frontend/lib/api/analytics.ts`:
  - Line 847: Resolve `store_id` with fallback to `getDefaultStoreId()` (same pattern as `getOverviewKpis()`)
  - Line 894: Include `store_id` in API call: `query: { store_id, zone_id, from, to, compare }`

**Impact:** Zone Performance page no longer emits 422 errors for zone analytics calls

## BUG 2b: Queue Zones Included in Zone Performance Results

**Root Cause:**
- `getZonePerformance()` fetches all zones from org data (including queue zones with `type: "checkout_queue"`)
- Queries each zone individually with `zone_id` param
- Backend endpoint routes single-zone queries to `read_zone_analytics_period()` (no queue filtering, by design)
- Queue zones appear in Zone Performance results despite backend having correct `Zone.zone_type` filter

**Fix:**
- Updated `getZonePerformance()` in `frontend/lib/api/analytics.ts`:
  - Lines 863-866: Filter queue zones from `zoneShapes` before querying
  - Check: `if (zone.type === "checkout_queue") continue;`
  - Reuses frontend ZoneShape mapping where `type` is already mapped to `"checkout_queue"`

**Impact:** Zone Performance "all zones" aggregation now correctly excludes queue-type zones

**Note on Architecture:** `getZonePerformance()` uses a custom frontend aggregation approach (builds zone list from org data, queries per-zone) rather than leveraging `read_zones_for_scope()` multi-zone aggregation. This is intentional per the original page design. Queue zone exclusion is now applied at the frontend zone-list-building stage, matching the backend exclusion behavior.
