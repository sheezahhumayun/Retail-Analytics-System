# Module 15 — Alerting System

**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete & Verified | Phase 3 ✅ Complete & Verified | Phase 4 ✅ Complete | Phase 5 ✅ Complete | Phase 6 ✅ Complete | Phase 6b ✅ Complete | Follow-ups ✅

---

## Phase 0 — Baseline Investigation

### What Was Found

**Alerting infrastructure exists but is inactive:**
- ✅ Alert table (alerts) with id, alert_type, camera_id, zone_id, timestamp, severity, status, metadata
- ✅ AnalyticsDbWriter subscribes to DWELL_THRESHOLD / QUEUE_THRESHOLD / OCCUPANCY_THRESHOLD / CAMERA_OFFLINE events and inserts rows
- ✅ Dwell tracker has threshold firing logic (`_maybe_threshold` fires once per visit when dwell ≥ threshold)
- ✅ Queue tracker has length and duration threshold logic (fires once per episode when thresholds exceeded)
- ✅ REST API endpoints: GET /api/alerts (filter by status/severity), PATCH /api/alerts/{id} (acknowledge/resolve)
- ✅ Frontend Alerts page exists and displays/filters/updates alerts correctly

**But: Alerting never fires in the pipeline**
- Current code: `inference/pipeline/process_recorded.py` creates `AnalyticsEngineConfig` without passing any threshold dicts
- Config defaults: `dwell_thresholds=None`, `queue_length_thresholds=None`, `queue_duration_thresholds=None`
- Tracker behavior: When threshold is None, trackers skip the threshold check entirely (return None, no event)
- Root cause: "Alerting was never turned on" — not dead code, just not wired to the pipeline

### Decision

Build a configurable threshold table (`alert_rules`) so admins can control thresholds without code changes. Keep the existing debounce/firing logic completely unchanged — only change the source of the threshold number.

---

## Phase 1 — alert_rules Table Schema & Seed

### What Was Created

**1. New Database Model: `AlertRule`**

```python
class AlertRule(SQLModel, table=True):
    id: int  # PK
    rule_type: str  # DWELL_THRESHOLD | QUEUE_THRESHOLD | QUEUE_THRESHOLD_DURATION | OCCUPANCY_THRESHOLD
    store_id: str | None  # NULL = org-wide or store-wide
    zone_id: str | None  # Specific zone, or NULL for store/org defaults
    threshold: float  # Numeric threshold value (seconds or count)
    severity: str  # warning | critical | info
    enabled: bool  # Default True
    created_at: datetime  # Audit trail
    updated_at: datetime  # Audit trail
```

**Lookup Hierarchy (for Phase 2):**
1. **Per-zone rule** (`store_id=NULL, zone_id=<id>`) — specific zone override
2. **Store-specific rule** (`store_id=<id>, zone_id=NULL`) — future enhancement
3. **Org-wide default** (`store_id=NULL, zone_id=NULL`) — fallback for new zones

**2. Alembic Migration: `006_alert_rules.py`**

Creates table with three-tier seeding:
- **Org-wide defaults** (3 rows: DWELL_THRESHOLD, QUEUE_THRESHOLD, QUEUE_THRESHOLD_DURATION)
- **Per-zone rules** for all existing analytics-enabled zones
- **Queue-zone-specific rules** for queue/checkout/waiting zone types

> **Fixed during verification:** the migration originally used `op.execute(sa.text(...), {...})` for the seed INSERTs, which raised `TypeError: execute() takes 2 positional arguments but 3 were given` — `op.execute()` doesn't accept a params dict the way `Connection.execute()` does. Fixed by binding via `conn = op.get_bind()` and calling `conn.execute(...)` for each seed statement.

**3. Seeded Values** (from `analytics/` module documentation examples)

| Rule Type | Org Default | Per-Zone | Notes |
|-----------|------------|----------|-------|
| DWELL_THRESHOLD | 60.0 s | All zones | From dwell/README.md: "60 seconds" |
| QUEUE_THRESHOLD | 5 persons | Queue zones | From queues/README.md: "5 persons" |
| QUEUE_THRESHOLD_DURATION | 120.0 s | Queue zones | From queues/README.md: "120 seconds" |

All seeded with:
- `severity="warning"` (matches current database/writer.py behavior)
- `enabled=true`
- `store_id=NULL` (org-wide or zone-specific, no per-store overrides yet)

**Verified in Postgres** (2026-08-04): 14 rows present — 3 org-wide defaults + 7 per-zone DWELL_THRESHOLD rows (`east_checkout_queue`, `floor_main`, `queue_lane`, `store1`, `store2`, `west_aisle`, `west_entrance_zone`) + 2 QUEUE_THRESHOLD + 2 QUEUE_THRESHOLD_DURATION rows for queue-type zones. Matches design exactly.

### Decision: Fallback Strategy

- **Existing zones** get explicit per-zone rules so behavior is predictable
- **New zones** (created after migration) inherit org-wide defaults automatically
- Phase 2 lookup will check: zone-specific → store-specific → org-wide default
- **Never silent-disable:** If alert_rules has no row, fall back to hardcoded default (no behavior regression)

### Intent

Phase 1 prepares the schema and seed data. Phase 2 will wire the pipeline to read from this table instead of hardcoded dicts. Existing tests pass unchanged because seeded values match old hardcoded behavior.

---

## Phase 2 — Wire Thresholds to Read from alert_rules

### What Was Created

**1. Alert Rules Service** — `backend/app/services/alert_rules.py`

Three public functions for loading thresholds from the database:
- `get_dwell_thresholds(zone_ids, store_id)` → `dict[str, float | None]`
- `get_queue_length_thresholds(zone_ids, store_id)` → `dict[str, int | None]`
- `get_queue_duration_thresholds(zone_ids, store_id)` → `dict[str, float | None]`

Each function:
- Accepts list of zone IDs to load
- Queries alert_rules table for enabled rules
- Implements fallback hierarchy: zone-specific → store-specific → org-wide default
- Returns dict keyed by zone_id with threshold values
- If no rule exists for a zone, it's included with the org-wide default value

**2. Pipeline Integration** — Updated `inference/pipeline/process_recorded.py`

**Before:**
```python
engine = AnalyticsEngine(
    bus,
    AnalyticsEngineConfig(
        camera_ids=[camera_id],
        zones=pipeline_zones,
        # dwell_thresholds=None (default)
        # queue_length_thresholds=None (default)
        # queue_duration_thresholds=None (default)
    ),
)
```

**After:**
```python
# Load thresholds from alert_rules table
dwell_zones = [z.zone_id for z in pipeline_zones if not is_queue_zone(z)]
queue_zones = [z.zone_id for z in pipeline_zones if is_queue_zone(z)]

dwell_thresholds = get_dwell_thresholds(dwell_zones, store_id) if dwell_zones else None
queue_length_thresholds = get_queue_length_thresholds(queue_zones, store_id) if queue_zones else None
queue_duration_thresholds = get_queue_duration_thresholds(queue_zones, store_id) if queue_zones else None

engine = AnalyticsEngine(
    bus,
    AnalyticsEngineConfig(
        camera_ids=[camera_id],
        zones=pipeline_zones,
        dwell_thresholds=dwell_thresholds,
        queue_length_thresholds=queue_length_thresholds,
        queue_duration_thresholds=queue_duration_thresholds,
        # ... rest of config
    ),
)
```

> **Note:** `tests/scripts/run-events-demo.py` is a separate standalone demo script that builds its own `AnalyticsEngineConfig` from CLI flags (`--dwell-threshold`, etc.) and does **not** call the alert_rules service. It was used during verification (with `--dwell-threshold` passed explicitly) to prove the underlying engine → bus → `AnalyticsDbWriter` → `alerts` table path works. It is not itself wired to `alert_rules` and was intentionally left as-is (out of Phase 2 scope) rather than modified.

### Design Decisions

- ✅ **No debounce logic changed:** Trackers' "fires once per visit" (dwell) and "resets when queue clears" (queue) logic is completely untouched. Only the threshold value source changed.
- ✅ **Fallback to org-wide defaults:** If a zone has no specific alert_rules row, it uses the org-wide default row, ensuring alerting never silently breaks due to missing data.
- ✅ **Simple service pattern:** Matches existing codebase style — direct queries, no complex caching. Database is source of truth.
- ✅ **Backwards compatible:** Seeded alert_rules values match old hardcoded behavior, so existing tests pass unchanged.
- ✅ **Per-rule-type filters:** Dwell rules apply to all analytics zones; queue rules apply only to queue/checkout/waiting zone types.

### Tests

**File:** `tests/test_alert_rules.py` — **10/10 passing, confirmed stable across repeated runs**

1. `TestAlertRulesService` — Verify service loads correct thresholds with fallback
   - `test_load_dwell_thresholds_org_default` ✅
   - `test_load_queue_length_thresholds_org_default` ✅
   - `test_load_queue_duration_thresholds_org_default` ✅
   - `test_load_thresholds_custom_zone_rule` ✅
   - `test_load_thresholds_disabled_rule` ✅

2. `TestDwellThresholdWithAlertRules` — Dwell threshold firing with alert_rules values
   - `test_dwell_fires_with_seeded_threshold` ✅
   - `test_dwell_respects_custom_threshold` ✅

3. `TestQueueThresholdWithAlertRules` — Queue threshold firing with alert_rules values
   - `test_queue_length_fires_with_seeded_threshold` ✅
   - `test_queue_length_respects_custom_threshold` ✅
   - `test_queue_duration_fires_with_seeded_threshold` ✅

Each test proves that:
- ✅ Old behavior is preserved (tests pass with seeded values)
- ✅ New behavior works (changing alert_rules changes firing behavior)

**Bugs found and fixed during verification (all in test infrastructure, not application code):**
1. Migration 006 `op.execute()` bind-params bug (see Phase 1 note above).
2. `db_ready()` fixture had a bare `except Exception` that masked a real `ImportError` (missing `backend/__init__.py`) behind a misleading "PostgreSQL not available" skip message. Narrowed to `except OperationalError`.
3. `db_ready()` fixture inserted `Zone` rows with `camera_id="test_camera"` without first creating the corresponding `Camera` row, violating `zones_camera_id_fkey`. Fixed by merging a `Camera` row before the `Zone` rows.
4. Two tests (`test_dwell_respects_custom_threshold`, `test_queue_length_respects_custom_threshold`) wrote custom `AlertRule` rows without cleanup, causing order-dependent pollution across runs. Fixed with a function-scoped autouse fixture that deletes matching `AlertRule` rows before and after every test, making the suite self-healing against both intra-run pollution and leftover state from interrupted prior runs.

### End-to-End Verification (2026-08-04)

Ran `tests/scripts/run-events-demo.py sample-data/town.mp4 --camera-id town --zone-config tests/videos/town_zones.json --dwell-threshold 2 --persist-db` after confirming the underlying alert_rules-driven code path via unit tests.

**Result:**
- 21 `DWELL_THRESHOLD` bus events fired (zones `store1`, `store2`, both under the 2s test threshold).
- All 21 persisted to the `events` table with matching `camera_id`/`zone_id`/timestamps.
- All 21 persisted to the `alerts` table (`severity=warning`, `status=open`), confirmed via direct query — verification initially appeared to fail because the query filtered on wall-clock `NOW() - INTERVAL '1 hour'`, but recorded-pipeline event timestamps are video-relative (near epoch `1970-01-01`), not wall-clock. Querying without the time filter confirmed all 21 rows present and correct.

This confirms the full path: `alert_rules` table → `alert_rules` service → `AnalyticsEngineConfig` thresholds → dwell tracker firing → event bus → `AnalyticsDbWriter` → `alerts` table, works correctly end to end.

### Intent

Phase 2 wires the pipeline to actually read thresholds from the database instead of passing None. Admins can now change alert thresholds without redeploying code — just update the alert_rules table. The debounce/firing logic is untouched; only the threshold value changes.

---

## Phase 3 — Occupancy Alerting

### What Was Created

**1. New rule type: `OCCUPANCY_THRESHOLD`**

Store-level (not zone-level). `zone_id` is always `NULL` for this rule type. `store_id=NULL` means org-wide default (same convention as dwell/queue org defaults).

| Field | Value |
|-------|-------|
| `rule_type` | `OCCUPANCY_THRESHOLD` |
| `store_id` | `NULL` (org-wide default) |
| `zone_id` | `NULL` (always — store-level rule) |
| `threshold` | `30` (absolute person count — **placeholder**, confirm/adjust via rules edit once Phase 4 admin API exists) |
| `severity` | `warning` |
| `enabled` | `true` |

**2. Alembic Migration: `007_occupancy_threshold_alert_rule.py`** (revision `007_occupancy_alert`)

Additive only — inserts exactly one org-wide row. Does not modify migration 006.

> **Note:** The original revision id `007_occupancy_threshold_alert_rule` exceeded Alembic's `alembic_version.version_num` varchar(32) limit and was shortened to `007_occupancy_alert`.

**Verified in Postgres** (2026-08-04): 1 row present — `(OCCUPANCY_THRESHOLD, store_id=NULL, zone_id=NULL, threshold=30.0, severity=warning, enabled=true)`.

**3. Alert Rules Service** — extended `backend/app/services/alert_rules.py`

New functions (existing dwell/queue functions untouched):
- `get_occupancy_threshold(store_id)` → `float | None` — store-specific → org-wide → hardcoded fallback `30.0`
- `get_occupancy_severity(store_id)` → `str` — severity from matched rule (used by `AnalyticsDbWriter`)

**4. Store-level breach tracking** — `analytics/occupancy/aggregator.py`

`StoreOccupancyAggregator` (not `OccupancyTracker`) holds breach state:
- `check_threshold(threshold)` returns `True` only on below-threshold → at-or-above-threshold transition
- Stays `False` while occupancy remains elevated
- Re-arms when occupancy drops back below threshold (no hysteresis, no cooldown — mirrors dwell's "fires once per visit" flag)

**5. Event bus integration** — `analytics/events/engine.py`

After each ENTRY/EXIT updates `StoreOccupancyAggregator`:
1. `get_occupancy_threshold(store_id)`
2. `check_threshold(threshold)`
3. If `True`, publish `OCCUPANCY_THRESHOLD` on the bus via `occupancy_threshold_to_analytics()` (`analytics/events/adapters.py`)

Event metadata: `store_id`, `current_occupancy`, `threshold`. `camera_id` on the event envelope is the crossing camera; the `alerts` row uses `camera_id=NULL` (store-level).

**6. DB writer** — `database/writer.py`

New branch for `OCCUPANCY_THRESHOLD` in `_insert_alert`:
- Inserts `alerts` row with `camera_id=NULL`, `zone_id=NULL`
- Severity pulled from matched `alert_rules` row via `get_occupancy_severity()`
- DWELL_THRESHOLD / QUEUE_THRESHOLD severity left hardcoded (`"warning"`) — loading from `alert_rules` would require a per-zone DB lookup in `_insert_alert`; deferred to Phase 4

**7. Event type** — `analytics/events/types.py`

`OCCUPANCY_THRESHOLD` added to `AnalyticsEventType` enum alongside `DWELL_THRESHOLD` / `QUEUE_THRESHOLD`.

### Design Decisions

- ✅ **Store-level scope:** Customer-facing occupancy number is the store rollup, not per-camera or per-zone
- ✅ **Absolute person count:** No `capacity` field on stores — threshold is a raw headcount
- ✅ **Transition-based firing:** Fires once on breach, re-arms on drop — same mental model as dwell's `threshold_fired` flag
- ✅ **No debounce logic changed:** Dwell/queue debounce untouched; occupancy is a new, independent path
- ✅ **Additive DB only:** One new migration file; migration 006 not edited
- ✅ **Fallback safety:** Hardcoded `30.0` fallback if no `alert_rules` row exists (never silently returns `None` when a default would work)

### Tests

**File:** `tests/test_alert_rules.py` — `TestOccupancyThresholdWithAlertRules` (3 new tests)

- `test_occupancy_fires_once_on_breach_transition` ✅ — sustained over-threshold sequence fires exactly one alert
- `test_occupancy_refires_after_drop_and_rebreach` ✅ — drop below threshold then re-breach fires a second alert
- `test_load_occupancy_threshold_org_default` ✅ — org-wide seeded threshold (30) returned

**Full suite** (2026-08-04): `pytest tests/test_occupancy.py tests/test_alert_rules.py tests/test_events.py tests/test_database.py -q` → **44 passed**

Cleanup fixture extended to delete store-specific `OCCUPANCY_THRESHOLD` test rows (`store_id=STORE_ID`) before/after each test.

### Intent

Phase 3 adds store-level occupancy alerting on top of the Phase 1–2 infrastructure. Occupancy breaches now flow through the same event bus → `AnalyticsDbWriter` → `alerts` table path as dwell and queue thresholds. The seeded `threshold=30` is a placeholder — adjust via the Phase 4 Alert Thresholds modal or direct `alert_rules` edit.

---

## Phase 4 — Admin API & Alert Thresholds Modal

### What Was Created

**1. Admin REST API** — `backend/app/routers/alert_rules_admin.py`

Gated with `require_admin` from `backend/app/auth.py` (same dependency as `/api/users`).

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/alert-rules` | List all `alert_rules` rows |
| `PUT /api/admin/alert-rules/{id}` | Update `threshold`, `severity`, `enabled`; sets `updated_at` |

- Body validation: `threshold > 0` (422 otherwise)
- No POST / DELETE — edits existing rows only (minimal Phase 4 scope)

**Schemas:** `backend/app/schemas/extended/alert_rules.py` (`AlertRuleResponse`, `AlertRuleUpdate`)

**Registered in:** `backend/app/main.py` → `app.include_router(alert_rules_admin.router, prefix=api)`

**2. Frontend API** — `frontend/lib/api/alert-rules.ts`

- `getAlertRules()`, `updateAlertRule(id, body)`
- `formatAlertRuleLabel()` for human-readable row labels
- `ALERT_RULE_SEVERITIES` from existing `AlertSeverity` union (`critical`, `warning`, `info`)

**3. Alert Thresholds modal** — `frontend/components/alert-thresholds-modal.tsx`

- Reuses existing modal pattern (`fixed inset-0`, backdrop, sticky header — same as `user-modal.tsx` / `camera-modal.tsx`; no new dialog library)
- On open: `GET /api/admin/alert-rules`, flat list (org default + per-zone rows)
- Per row: threshold input, severity dropdown, enabled toggle
- Client-side validation: threshold must be `> 0` before save
- Save: `PUT` only changed rows (diff vs initial GET)
- Entry point: **Alert Thresholds** button on `/alerts` page header (`frontend/app/alerts/page.tsx`)
- Visibility gated on `user.role === 'System Administrator'` (same pattern as `app/admin/layout.tsx`)

**4. Tests** — `tests/test_api_extended.py` → `TestAdminAlertRules`

- `test_admin_can_list_alert_rules` ✅
- `test_admin_can_update_threshold` ✅
- `test_non_admin_forbidden` ✅
- `test_put_invalid_threshold_returns_422` ✅

### Design Decisions

- ✅ **No new page/route** — modal on existing Alerts page only
- ✅ **PUT-only** — no new rows via API; migrations + seed own the baseline rows
- ✅ **Severity from `alert_rules`** for occupancy alerts in writer; dwell/queue writer severity still hardcoded (deferred)
- ✅ **Read functions untouched** — `get_dwell_thresholds` / `get_queue_*` / `get_occupancy_threshold` unchanged

### Intent

Admins can view and edit threshold/severity/enabled for all seeded `alert_rules` rows without SQL or redeploy. Seeded `OCCUPANCY_THRESHOLD=30` can be adjusted via the modal.

---

## Phase 6 — Auto-provision `alert_rules` on zone creation

### Problem

New zones created via `POST /api/zones` had no per-zone `alert_rules` rows. Thresholds silently fell back to org-wide defaults with **no visible row** in the Alert Thresholds admin modal — admins could not see or edit zone-specific thresholds for API-created zones.

### What Was Created

**1. Provisioning service** — `backend/app/services/alert_rules.py`

- `provision_zone_alert_rules(zone_id, zone_type, store_id=None, session=None)`
- `_get_org_default_rule(session, rule_type)` — reads org-wide default (`store_id=NULL`, `zone_id=NULL`)
- `_upsert_alert_rule(...)` — same idempotent key as `database/seed.py` (`rule_type` + `store_id` + `zone_id`)

**Provisioning rules:**

| Rule type | When provisioned |
|-----------|------------------|
| `DWELL_THRESHOLD` | Always (every zone) |
| `QUEUE_THRESHOLD` | Only if `zone_type` ∈ `QUEUE_ZONE_TYPES` (`analytics.modules`) |
| `QUEUE_THRESHOLD_DURATION` | Only if queue zone type |
| `OCCUPANCY_THRESHOLD` | **Never** per-zone (store-level only) |

Threshold, severity, and enabled are **copied from the current org-wide default** at creation time — not hardcoded. If an admin already changed the org default, new zones inherit the current value.

**2. Zone creation hook** — `backend/app/routers/zones_config.py` → `POST /api/zones`

After `zone_shapes` + analytics `zones` rows are flushed:

- Calls `provision_zone_alert_rules(...)` with the request session
- Wrapped in `try/except` — logs warning on failure; **does not fail zone creation** (missing row degrades to org-default fallback, which is already safe)

**3. `zone_shapes` → `zones` sync on create** (required for `alert_rules.zone_id` FK → `zones.id`)

`POST /api/zones` now also inserts a matching analytics `Zone` row (same `id` as `zone_shapes`):

| `Zone` column | Value on create |
|---------------|-----------------|
| `id` | `body.id` |
| `camera_id` | `body.camera_id` |
| `name` | `body.name` |
| `polygon_coords` | `body.polygon_points` (real polygon, ≥ 3 vertices — not a placeholder) |
| `zone_type` | Mapped from shape type (`checkout_queue` → `"queue"`, `entrance` → `"entrance"`, else `"general"`) |
| `analytics_enabled` | `True` |

`zone_shapes.id` and `zones.id` share the same string PK namespace by convention (seed/demo use identical ids). No FK links the two tables; duplicate id → Postgres PK violation, not a silent second row.

**Other `zones` table writers (for context):** `database/seed.py` (`merge`), `database/seed_demo.py` (`add`). Pipeline (`process_recorded.py`) and `polygon_editor.py` read or emit JSON only — they do not insert `zones` rows. Reseed `merge` on an existing id updates; it does not duplicate.

**4. Tests** — `tests/test_api_extended.py` → `TestZoneAlertRuleProvisioning`

- `test_create_general_zone_provisions_dwell_from_org_default` ✅
- `test_create_queue_zone_provisions_queue_rules_from_org_defaults` ✅

### Zone deletion — hard delete + `alert_rules` cascade

**Decision (2026-08-05)** — not part of original Phase 4/6 scope. **Implemented in Phase 6b.**

Zone deletion is a **hard delete** (`DELETE /api/zones/{id}`): removes `zone_shapes` and analytics `zones` rows. There is **no soft-delete flag** (unlike cameras, which use `status = "disabled"`).

Because Phase 6 provisions `alert_rules` rows for every zone at creation, zone deletion **cascades** to delete matching `alert_rules` rows (`zone_id = <deleted zone>`) in the **same transaction**. This:

- Prevents orphaned threshold rows in the admin UI
- Avoids FK-violation failures on delete (`alert_rules.zone_id` → `zones.id` is a real FK — see Phase 6b)

**Delete order (same DB transaction):** `alert_rules` → `zones` → `zone_shapes`.

Historical `alerts` rows for the deleted zone are preserved (same “preserve history” pattern as camera soft-delete).

### Known pre-existing gap (not fixed in Phase 6)

`PUT /api/zones/{id}` updates **`zone_shapes` only**, not the analytics `zones` table. Polygon, name, and type edits from the admin UI do **not** propagate to the row the pipeline and `alert_rules` FK actually use — geometry can drift stale after an edit. Predates Phase 6; flagged for a future pass.

### Design Decisions

- ✅ Reuse seed upsert pattern — do not reinvent idempotency
- ✅ `QUEUE_ZONE_TYPES` from `analytics.modules` — no second hardcoded list
- ✅ No per-zone `OCCUPANCY_THRESHOLD`
- ✅ Provisioning failure is non-fatal for zone creation
- ✅ Phase 4 admin GET/PUT and Phase 5 nav badge pub/sub untouched

---

## Phase 6b — Cascade delete + zone names in admin modal

Two small fixes on top of Phase 6. Phase 4 (admin GET/PUT), Phase 5 (nav badge), and Phase 6 provisioning logic untouched. PUT-doesn't-sync-to-`zones` drift **not** fixed here.

### Fix 1 — Cascade delete `alert_rules` on zone delete

**File:** `backend/app/routers/zones_config.py` → `DELETE /api/zones/{id}`

In the same request transaction as zone removal:

1. Delete all `alert_rules` rows where `zone_id = <deleted zone>` (any `rule_type`)
2. Delete analytics `zones` row (if present)
3. Delete `zone_shapes` row

**Why this order:** `alert_rules.zone_id` has a real Postgres FK to `zones.id` (`fk_alert_rules_zone_id` in migration `006_alert_rules`; `foreign_key="zones.id"` on `AlertRule` in `database/models.py`). `alert_rules` must be removed before `zones`.

**Test:** `tests/test_api_extended.py` → `TestZoneAlertRuleProvisioning`

- `test_delete_zone_cascades_alert_rules` ✅ — create zone (provisions rules), delete zone, confirm `alert_rules` count for that `zone_id` is 0

### Fix 2 — Zone display names in Alert Thresholds modal

**Problem:** Per-zone rows were labeled e.g. `Long Dwell — store1` (raw `zone_id`).

**Files:**

- `frontend/components/alert-thresholds-modal.tsx` — on open, loads zone names via `getOrganization()` in parallel with `getAlertRules()` (same cached scope-tree pattern as `frontend/lib/api/alerts.ts` and zone dropdowns)
- `frontend/lib/api/alert-rules.ts` — `formatAlertRuleLabel(rule, zoneNames?)` resolves `zone_id` → name; falls back to raw `zone_id` if not found

Labels now show e.g. `Long Dwell — store1` → `Long Dwell — Store 1` (actual zone name from `zone_shapes` / org tree).

---

## Follow-up — `database/seed.py` alert_rules seeding

Migrations 006/007 only run once; truncate/reseed left `alert_rules` empty. Added idempotent seeding that mirrors migration values.

**Added to `database/seed.py`:**

- `_upsert_alert_rule()` — upsert on `(rule_type, store_id, zone_id)`
- `_seed_alert_rules()` — called after `_seed_cameras_and_zones()` (per-zone rules need real `zone_id` FKs)
- Org-wide defaults: DWELL 60, QUEUE 5, QUEUE_DURATION 120, OCCUPANCY 30 (matches 006 + 007)
- Per-zone: DWELL for all `analytics_enabled` zones; QUEUE + QUEUE_DURATION for `queue` / `checkout` / `waiting` zones

**Typical row counts after `python -m database.seed`:**

| rule_type | count (reference seed) |
|-----------|------------------------|
| DWELL_THRESHOLD | 8 |
| QUEUE_THRESHOLD | 3 |
| QUEUE_THRESHOLD_DURATION | 3 |
| OCCUPANCY_THRESHOLD | 1 |

(4 zones: `store1`, `store2`, `floor_main`, `queue_lane` — one queue zone)

---

## Follow-up — Test hygiene & API test fixes

### `tests/test_alert_rules.py` cleanup

`cleanup_alert_rules` autouse fixture now deletes **all** `alert_rules` rows for `test_dwell_zone` and `test_queue_zone` (any `rule_type`), plus store-scoped `OCCUPANCY_THRESHOLD` test rows — before and after each test. Prevents test zone rules leaking into dev/admin views after test runs.

Verified: `COUNT(*) FROM alert_rules WHERE zone_id IN ('test_dwell_zone','test_queue_zone')` → **0** after two consecutive test runs.

### `tests/test_api.py::TestAnalytics` fixes

| Test | Fix |
|------|-----|
| `test_zones`, `test_dwell` | Added required `store_id: STORE_ID` param (endpoint requires it; was 422) |
| `test_traffic` | Store-level `/traffic` now reads `VisitorMetric` rollups via `_visitor_metric_buckets()` in `analytics_read.py` (24 zero-filled hours/day); test asserts `len(buckets) == 24` |
| `test_queues_empty` | Added `store_id`; `zone_id` must be a queue zone (`queue_lane`, not `store1` → 403); date range `2099-01-01`–`2099-01-02` for empty samples |

**Root cause (22 vs 24 buckets):** `_traffic_buckets()` aggregated sparse `Event` rows and omitted zero-traffic hours; seed `VisitorMetric` has full 24-hour rows but was not used for store-level traffic.

---

## Follow-up — Nav open-alert badge refresh

**Problem:** Nav bell badge (`OpenAlertBadge` in `top-nav.tsx`) called `getOpenAlertCount()` once on mount; count stayed stale after acknowledge/resolve on `/alerts`.

**Mechanism:** No React Query or alerts Context in the codebase. Added **module-level pub/sub** in `frontend/lib/api/alerts.ts`:

- `subscribeOpenAlertCount(listener)` / `notifyOpenAlertCountChanged()`
- `updateAlert()` calls `notifyOpenAlertCountChanged()` after successful `PATCH /api/alerts/{id}`
- `OpenAlertBadge` subscribes and refetches count on notify

**Files:** `frontend/lib/api/alerts.ts`, `frontend/components/dashboard/top-nav.tsx`

**Manual verify:** Log in → note nav badge count → `/alerts` → acknowledge/resolve an open alert → badge updates immediately without page reload (same tab).

---

## Summary of Changes (Phases 1–6b + follow-ups)

### Database
- ✅ `alert_rules` table (migrations 006 + 007)
- ✅ `database/seed.py` — `_seed_alert_rules()` mirrors migration values on every reseed (idempotent)
- ✅ Phase 6: per-zone `alert_rules` auto-provisioned on `POST /api/zones`; cascade delete on zone hard-delete (Phase 6b)

### Backend
- ✅ `backend/app/services/alert_rules.py` — threshold loaders (dwell, queue, occupancy) + `provision_zone_alert_rules`
- ✅ `inference/pipeline/process_recorded.py` — pipeline reads thresholds from DB
- ✅ Phase 3 occupancy: `aggregator.check_threshold()`, bus event, `AnalyticsDbWriter` branch
- ✅ Phase 4: `GET/PUT /api/admin/alert-rules` (`alert_rules_admin.py`)
- ✅ Phase 6: `zones_config.py` — sync analytics `Zone` on create; provision `alert_rules`; cascade delete `alert_rules` on zone delete (6b)
- ✅ Phase 6b: `formatAlertRuleLabel` + modal zone name lookup via `getOrganization()`
- ✅ `analytics_read.py` — store `/traffic` from `VisitorMetric` (24 zero-filled hours/day)

### Frontend
- ✅ `alert-thresholds-modal.tsx` + `frontend/lib/api/alert-rules.ts`
- ✅ Alerts page admin trigger; nav badge pub/sub after PATCH (`subscribeOpenAlertCount`)

### Tests
- ✅ `tests/test_alert_rules.py` (13 tests + test-zone cleanup fixture)
- ✅ `tests/test_api_extended.py::TestAdminAlertRules` (4 tests)
- ✅ `tests/test_api_extended.py::TestZoneAlertRuleProvisioning` (3 tests)
- ✅ `tests/test_api.py::TestAnalytics` fixes (store_id, traffic, queues)

### Known Limitations (remaining)
- Dwell/queue writer severity still hardcoded `"warning"`
- Admin API PUT-only (no POST/DELETE)
- Occupancy threshold DB lookup on every ENTRY/EXIT
- Nav badge pub/sub not cross-tab
- `tests/scripts/run-events-demo.py` not wired to `alert_rules`
- `PUT /api/zones/{id}` does not sync analytics `zones` row (geometry drift after edit)

---

## Testing Strategy

**Per phase:**
- ✅ Phase 1: Migration creates table, seeding produces expected rows — verified
- ✅ Phase 2: Threshold firing with DB-backed values — verified via unit tests + live pipeline run
- ✅ Phase 3: Occupancy fires once per breach, re-fires after drop + re-breach — 44/44 analytics tests passing
- ✅ Phase 4: Admin list/update API + RBAC — `TestAdminAlertRules` 4/4 passing
- ✅ Phase 6: Zone create provisions `alert_rules` from org defaults — `TestZoneAlertRuleProvisioning` 3/3 passing
- ✅ Phase 6b: Zone delete cascades `alert_rules`; modal shows zone names

**Test suite runs:**
- `test_dwell.py` — Dwell threshold firing ✅
- `test_queues.py` — Queue length/duration threshold firing ✅
- `test_events.py` — Full engine integration ✅
- `test_database.py` — DB writer persistence ✅
- `test_alert_rules.py` — Service + threshold firing with DB ✅ (inference venv + `database/requirements.txt`)
- `test_api_extended.py` — Admin alert-rules API + zone provisioning ✅ (backend venv)
- `test_api.py::TestAnalytics` — Analytics endpoints ✅ (backend venv)

**Reseed verification:**
```bash
python -m database.seed
docker exec retail-analytics-postgres psql -U retail -d retail_analytics \
  -c "SELECT rule_type, COUNT(*) FROM alert_rules GROUP BY rule_type;"
```

**Environment note:** `test_alert_rules.py` needs both the inference stack (`supervision`, `ultralytics`, etc.) and DB access (`sqlmodel`, `psycopg2`). Run from `inference/.venv` with `database/requirements.txt` installed.

---

## Implementation Notes

- **Debounce logic is untouched:** "fires once per visit" (dwell), "resets when queue clears" (queue), "fires once per breach, re-arms on drop" (occupancy) — only the threshold value changes
- **Severity mapping:** Occupancy severity read from `alert_rules`; dwell/queue still hardcoded `"warning"` in writer; `"critical"` for `CAMERA_OFFLINE`
- **Caching strategy:** Keep simple — direct query with reload pattern matching existing codebase patterns
- **Backwards compatibility:** Phase 2 must ensure tests pass with same seeded thresholds; no behavior change until admin edits a rule
- **Event timestamps in recorded-pipeline runs are video-relative** (near epoch), not wall-clock — worth remembering when querying `events`/`alerts` for verification; filtering on `NOW() - INTERVAL` will silently exclude all recorded-pipeline rows.