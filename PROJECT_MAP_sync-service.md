# PROJECT MAP — sync-service
_Last updated: 2026-05-13_

## Service overview
| Item | Value |
|---|---|
| Location | services/sync-service/ |
| Runtime | Python 3.x / FastAPI 0.115.6 |
| Database | None |
| Cache | None (Redis "sync:designs" queue written by design-service; not yet consumed) |
| API prefix | None (only /health) |
| Dev port (vps role) | 8002 (host) → 8000 (container) |
| Dev port (office role) | 8003 (host) → 8002 (container) |
| Health | GET /health → {"status": "ok", "service": "sync-service", "role": "<ROLE>"} |
| Docs | /docs, /redoc |
| Status | Stub — no sync routes implemented |

## File index
| File | Responsibility |
|---|---|
| services/sync-service/src/main.py | FastAPI app; reads ROLE env var; CORS; commented-out router import; /health endpoint only |

## Endpoints
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /health | Health check; includes role in response | No | — |

No other endpoints are implemented. The sync router import is commented out:
```python
# from src.routes import sync
# app.include_router(sync.router, prefix="/sync", tags=["sync"])
```

## Services / Business logic
None implemented. The service is a skeleton FastAPI app only.

## Config / Env vars
| Var | Default | Purpose |
|---|---|---|
| ROLE | vps | Differentiates vps vs office instance; included in /health response and app description |

## External services
| Service | Used for | Files | Status |
|---|---|---|---|
| Redis "sync:designs" queue | Intended consumer of design upload events from design-service | (none yet) | NOT implemented |

## Requirements
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0
redis==5.2.1
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
```

## Known issues and TODOs
| Location | Note |
|---|---|
| src/main.py | Router import is commented out — service does nothing beyond health check |
| src/main.py | CORS allow_origins=["*"] — intentionally permissive for internal network; review before production |
| docker-compose.dev.yml | sync-service-office maps host 8003 → container 8002; but app listens on 8000 — port mapping mismatch for office role |

## What is NOT implemented
| Feature | Status |
|---|---|
| Sync route (/sync/*) | Router import is commented out; no route files exist |
| Redis consumer for "sync:designs" | Queue populated by design-service; no consumer code |
| File synchronisation between VPS and office | Core purpose of service; entirely absent |
| Authentication | No auth dependency |
| Any business logic | Entire service is a stub |
