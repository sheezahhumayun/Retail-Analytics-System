# Frontend — Project Status (API Integration)

**Last updated:** 2026-07-31  
**Detail doc:** `FRONTEND_PROJECT_STATUS.md` (UI/feature inventory, 2026-07-25)  
**Backend:** `http://127.0.0.1:8000` · set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` to override

---

## Integration summary

All `lib/api/*.ts` modules now call the live FastAPI backend. Shared infrastructure:

| File | Role |
|------|------|
| `lib/api/client.ts` | `fetch` wrapper, JWT from `localStorage` (`auth_session`), `ApiClientError` |
| `lib/api/mappers.ts` | Backend JSON → existing UI types (roles, traffic buckets, zone shapes, reports, …) |

**Auth:** `POST /api/auth/login` stores `{ access_token, user, org_id }`. `getCurrentUser()` reads cached user; `refreshCurrentUser()` optional `GET /api/auth/me`.

**Login (seed):** `admin@demo-retail.local` / `demo` · `user@demo-retail.local` / `demo`

---

## `lib/api/*.ts` — live vs client-side

### `auth.ts` — **live**

| Function | Endpoint | Notes |
|----------|----------|-------|
| `login` | `POST /api/auth/login` | Real password check; stores JWT |
| `loginByRole` | *(dev)* | Maps UI role → demo email, calls `login` |
| `logout` | client-only | Clears `auth_session` |
| `getCurrentUser` | client cache | Sync read of stored user |
| `refreshCurrentUser` | `GET /api/auth/me` | Optional refresh helper |

### `stores.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getOrganization` | `GET /api/organizations` + `GET /api/stores` + `GET /api/cameras` + `GET /api/zones` (composed tree) |
| `getStores` | composed from org tree |
| `getOrganizations` | `[getOrganization()]` |
| `getDefaultStoreId` | first store from API |

### `analytics.ts` — **live** (mappers + aggregation)

| Function | Endpoint / source |
|----------|-------------------|
| `getTraffic` | `GET /api/analytics/traffic` (+ prior period for comparison) |
| `getOccupancy` | `GET /api/analytics/occupancy` |
| `getZones` | `GET /api/analytics/zones` |
| `getDwell` | `GET /api/analytics/dwell` |
| `getHeatmap` | `GET /api/analytics/heatmap` → `density[][]` → `HeatBlob[]` |
| `getQueues` | `GET /api/analytics/queues` |
| `getOverviewKpis` | composed from traffic + occupancy + cameras |
| `getVisitorsByHour` | derived from traffic buckets |
| `getEntriesExits` | derived from traffic buckets |
| `getOccupancyTrend` | derived from occupancy trend |
| `fetch*Data/Stats` | thin wrappers over `get*` above |
| `fetchIntervalLabel` | **client-only** (`lib/analytics-data.ts`) |
| `getHeatmapCameras` | `GET /api/cameras` (fixed/fisheye) |
| `getZonePerformance` | `GET /api/zones` + `GET /api/analytics/zones` per zone |

### `events.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getEvents` | `GET /api/events` |

### `alerts.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getAlerts` | `GET /api/alerts` |
| `updateAlert` | `PATCH /api/alerts/{id}` |
| `formatAlertTime`, `getSeverityColor`, … | **client-only** re-exports from `lib/alerts-data.ts` |

### `reports.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getReport` (json) | `GET /api/reports/{type}` |
| `getReport` (csv/pdf) | `GET /api/reports/{type}/export` + browser download |
| `STORES`, `CAMERAS` | hydrated from API; seeded with `store_main` / camera ids for first paint |
| `REPORT_TYPES` | **static** constant |

### `cameras.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getCameras` | `GET /api/cameras` |
| `getLiveCameras` | `GET /api/cameras` + `GET /api/cameras/{id}/status` |
| `getCameraStatus` | `GET /api/cameras/{id}/status` |
| `createCamera` | `POST /api/cameras` |
| `updateCamera` | `PUT /api/cameras/{id}` |
| `deleteCamera` | `DELETE /api/cameras/{id}` |
| `testCamera` | `POST /api/cameras/{id}/test` |
| `ANALYTICS_MODULES_LABELS`, `getStatusColor`, … | **client-only** from `lib/admin-cameras-data.ts` |
| `STORES` | hydrated from API; default `["Main Street Store"]` |

### `zones.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getAllShapes` | `GET /api/zones` + `GET /api/lines` per camera |
| `getCamerasList` | `GET /api/cameras` |
| `getZoneShapes` | `GET /api/zones?camera_id=` |
| `createZone` | `POST /api/zones` |
| `updateZone` | `PUT /api/zones/{id}` |
| `deleteZone` | `DELETE /api/zones/{id}` |
| `ZONE_TYPES`, `SHAPE_COLORS`, … | **static** from `lib/zones-lines-data.ts` |

### `lines.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getCountingLines` | `GET /api/lines?camera_id=` |
| `createCountingLine` | `POST /api/lines` |
| `updateCountingLine` | `PUT /api/lines/{id}` |
| `deleteCountingLine` | `DELETE /api/lines/{id}` |

### `users.ts` — **live**

| Function | Endpoint |
|----------|----------|
| `getUsers` | `GET /api/users` |
| `createUser` | `POST /api/users` |
| `updateUser` | `PUT /api/users/{id}` |
| `deleteUser` | `DELETE /api/users/{id}` |
| `resetPassword` | `POST /api/users/{id}/reset-password` |
| `ROLE_COLORS`, `USER_ROLES`, `getStatusColor` | **client-only** from `lib/admin-users-data.ts` |
| `STORES` | hydrated from API; default `["Main Street Store"]` |

---

## Role mapping (backend ↔ UI)

| Backend JWT `role` | Frontend `UserRole` |
|--------------------|---------------------|
| `admin` | System Administrator |
| `user` | Retail Analyst |

Admin route gate checks `role === "System Administrator"`.

---

## Known limitations (post-integration)

- No live video stream / MJPEG endpoint — `frameUrl` is RTSP path string or null
- Live camera overlays remain empty (no inference overlay API)
- Heatmap `floor_zones` still uses static `FLOOR_ZONES` from `lib/heatmap-data.ts` for SVG layout
- `TestCameraModal` UI not yet calling `testCamera()` (component unchanged)
- Admin zones/lines **Save** button still console-only (API CRUD functions are live)
- Report form export buttons still `alert()` — use `getReport(..., { format: 'csv'|'pdf' })` for real downloads

---

## Verify

```powershell
cd frontend
npx tsc --noEmit
npm run dev
```

With backend running, log in and confirm scope selector shows **Demo Retail Co → Main Street Store** and analytics pages load without mock data.
