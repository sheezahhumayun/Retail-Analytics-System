# Docker Compose files

Full setup instructions are in the main **[README.md](../README.md)** (Getting Started section). Use this folder for Compose definitions only.

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Postgres + backend + inference + frontend |
| `docker-compose.rtsp-linux.override.example.yml` | **Untested** Linux `network_mode: host` override for LAN RTSP |

```powershell
# From repo root
docker compose -f docker/docker-compose.yml up --build -d
```
