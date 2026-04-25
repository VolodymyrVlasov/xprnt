# sync-service

Synchronizes print jobs between the VPS and office print stations.

Runs in two roles controlled by the `ROLE` env var:
- `ROLE=vps` — runs on the VPS, receives jobs from other services
- `ROLE=office` — runs at the print office, polls VPS for pending jobs

## Endpoints

- `GET /health` — health check (includes current role)
- `GET /docs` — Swagger UI

## Development

```bash
pip install -r requirements.txt
ROLE=vps uvicorn src.main:app --reload --port 8002
```

## Tests

```bash
pytest tests/ -v
```
