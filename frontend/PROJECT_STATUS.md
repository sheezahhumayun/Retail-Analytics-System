# Frontend — Project Status (API Integration)

**Last updated:** 2026-08-02 (Module 13.5 pass 2)  
**Detail doc:** `FRONTEND_PROJECT_STATUS.md` (UI/feature inventory, 2026-07-25)  
**Backend:** `http://127.0.0.1:8000` · set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` to override

---

## Integration summary

All `lib/api/*.ts` modules call the live FastAPI backend. Shared infrastructure:

| File | Role |
|------|------|
| `lib/api/client.ts` | `fetch` wrapper, JWT from `localStorage` (`auth_session`), `ApiClientError` |
| `lib/api/mappers.ts` | Backend JSON → existing UI types (roles, traffic buckets, zone shapes, reports, …) |

**Auth:** `POST /api/auth/login` stores `{ access_token, user, org_id }`. `AuthContext` refreshes via `GET /api/auth/me` on mount.

**Login (seed):** `admin@demo-retail.local` / `demo` · `user@demo-retail.local` / `demo`

---

## `lib/api/*.ts` — all live

See root `PROJECT_STATUS.md` Module 13.5 pass 2 for the full verification checklist.

**UI-only constants** (not business data): `lib/analytics-data.ts` (`getIntervalLabel`), `lib/reports-data.ts` (`REPORT_TYPES`), `lib/heatmap-data.ts` (`FLOOR_ZONES` SVG layout), `lib/zones-lines-data.ts` (zone type labels/colors), `lib/alerts-data.ts` / `lib/admin-*-data.ts` (formatting helpers).

**Removed in pass 2:** `auth-data.ts`, `mock-users.ts`, `overview-data.ts`, `camera-data.ts`, and all mock datasets inside remaining `*-data.ts` files.

---

## Verify

```powershell
cd frontend
npx tsc --noEmit
npm run dev
```

With backend running, log in and confirm scope selector shows **Demo Retail Co → Main Street Store** and analytics pages load from the API.
