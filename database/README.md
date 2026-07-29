# Retail Analytics — PostgreSQL schema & persistence (Module 11, PRD §31 / §35)

PostgreSQL stores **aggregated metrics** and **analytics events** — not raw frame-level
detections. The Analytics Engine's :class:`AnalyticsDbWriter` subscribes to the event
bus and rolls up hourly/daily tables as events arrive.

## Quick start (local dev)

```powershell
# 1. Start Postgres (host port 5433 — avoids local PostgreSQL on 5432)
copy .env.example .env
docker compose -f docker/docker-compose.yml up -d

# Or standalone:
# docker run -d --name retail-pg -p 5433:5432 `
#   -e POSTGRES_USER=retail -e POSTGRES_PASSWORD=retail `
#   -e POSTGRES_DB=retail_analytics postgres:16

# 2. Install deps (inference venv or backend venv)
pip install -r database/requirements.txt

# 3. Run migrations
alembic -c database/alembic.ini upgrade head

# 4. Seed reference org / store / camera / zone rows
python -m database.seed

# 5. Run pipeline with persistence
python tests/scripts/run-events-demo.py sample-data/town.mp4 `
  --camera-id town --zone-config tests/videos/town_zones.json --persist-db
```

Connection string (override via `.env` or `DATABASE_URL`):

```text
DATABASE_URL=postgresql+psycopg2://retail:retail@localhost:5433/retail_analytics
```

If you previously ran the container on port 5432, recreate it:

```powershell
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml up -d
```

## Schema (PRD §31)

| Table | Purpose |
|-------|---------|
| `organizations`, `stores`, `users` | Multi-tenant hierarchy |
| `cameras`, `zones`, `counting_lines` | Configuration |
| `tracks` | Anonymous track first/last seen |
| `events` | Raw analytics events (pruned after retention) |
| `visitor_metrics` | Hourly entries/exits per store |
| `occupancy_metrics` | Time-series occupancy per camera/store |
| `zone_metrics` | Hourly zone visitors + dwell rollups |
| `dwell_events` | Completed dwell sessions |
| `queue_metrics` | Queue length / wait samples |
| `alerts` | Threshold + camera offline alerts |

### Indexes

Time-range dashboard queries use composite indexes on
`(camera_id, timestamp)`, `(zone_id, timestamp)`, and `(store_id, metric_date, hour)`.

## Retention (PRD §35)

Raw `events` rows are pruned after **90 days** by default (configurable):

```powershell
$env:RAW_EVENT_RETENTION_DAYS = "90"
python -m database.cleanup
```

Aggregated tables are kept indefinitely.

## Dashboard query (Module 13 preview)

```sql
SELECT hour, entries, exits
FROM visitor_metrics
WHERE store_id = 'store_main'
  AND metric_date = CURRENT_DATE - INTERVAL '1 day'
ORDER BY hour;
```

Or via Python:

```python
from database import session_scope, visitors_by_hour_yesterday

with session_scope() as s:
    print(visitors_by_hour_yesterday(s, "store_main"))
```

## Test Checkpoint 11

```powershell
# Full pipeline → Postgres
python tests/scripts/run-events-demo.py sample-data/town.mp4 `
  --camera-id town --zone-config tests/videos/town_zones.json --persist-db

# Restart-safe: run again — rows append, no conflict
python tests/scripts/run-events-demo.py sample-data/town.mp4 `
  --camera-id town --zone-config tests/videos/town_zones.json --persist-db

# Automated tests (requires running Postgres)
pytest tests/test_database.py -v
```
