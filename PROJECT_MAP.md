# PROJECT MAP — xprnt monorepo
_Last updated: 2026-05-14_
_Scope: full — order-service, design-service, calculator-service, sync-service, admin_

## Detailed service maps
| Service | Map file |
|---|---|
| order-service | [PROJECT_MAP_order-service.md](PROJECT_MAP_order-service.md) |
| design-service | [PROJECT_MAP_design-service.md](PROJECT_MAP_design-service.md) |
| calculator-service | [PROJECT_MAP_calculator-service.md](PROJECT_MAP_calculator-service.md) |
| sync-service | [PROJECT_MAP_sync-service.md](PROJECT_MAP_sync-service.md) |
| admin | [PROJECT_MAP_admin.md](PROJECT_MAP_admin.md) |

## Repository structure
```
xprnt/
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       ├── ci.yml               ← runs tests on push/PR to main and develop
│       └── deploy-office.yml    ← auto-deploy to SVR on push to main
├── infra/
│   └── postgres/
│       └── init.sql
├── services/
│   ├── order-service/
│   │   ├── src/
│   │   │   ├── config.py
│   │   │   ├── main.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── seeds.py
│   │   │   ├── models/
│   │   │   ├── repository/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── alembic/
│   │       └── versions/  (5 migrations)
│   ├── design-service/
│   │   ├── app/
│   │   │   ├── config.py
│   │   │   ├── main.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── models/
│   │   │   ├── repository/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   ├── schemas/
│   │   │   └── utils/
│   │   └── alembic/
│   │       └── versions/  (2 migrations)
│   ├── calculator-service/
│   │   └── app/
│   │       ├── config.py
│   │       ├── main.py
│   │       ├── routes/
│   │       ├── schemas/
│   │       └── services/
│   ├── sync-service/
│   │   └── src/
│   │       └── main.py
│   └── admin/
│       ├── src/
│       │   ├── main.jsx
│       │   ├── App.jsx
│       │   ├── authProvider.js
│       │   ├── dataProvider.js
│       │   └── resources/
│       │       ├── users/
│       │       ├── companies/
│       │       ├── categories/
│       │       ├── products/
│       │       ├── prices/
│       │       ├── priceMultipliers/
│       │       ├── orders/
│       │       ├── sizes/
│       │       └── measurementUnits/
│       ├── package.json
│       ├── vite.config.js
│       └── Dockerfile.dev
└── PROJECT_MAP*.md
```

## Services table
| Service | Type | Dev port (host) | Stack | DB | Container name |
|---|---|---|---|---|---|
| order-service | Python API | 8000 | FastAPI 0.115.6 / SQLAlchemy 2 / asyncpg | PostgreSQL order_db | order-service |
| design-service | Python API | 8001 | FastAPI 0.115.6 / SQLAlchemy 2 / asyncpg | PostgreSQL design_db | design-service |
| sync-service (vps) | Python API stub | 8002 | FastAPI 0.115.6 | None | sync-service-vps |
| sync-service (office) | Python API stub | 8003 | FastAPI 0.115.6 | None | sync-service-office |
| calculator-service | Python API stub | (not in compose) | FastAPI (unpinned) | None | (none) |
| admin | React SPA | 3001 | React 19 / react-admin 5 / Vite 8 | None | xprnt-admin |
| postgres-order | PostgreSQL | 5432 | postgres:16 | order_db | postgres-order |
| postgres-design | PostgreSQL | 5433 | postgres:16 | design_db | postgres-design |
| minio | Object storage | 9000 (API), 9001 (console) | minio/minio:latest | — | minio |
| redis | Cache | 6379 | redis:7-alpine | — | redis |
| pgadmin | DB admin UI | 5050 | dpage/pgadmin4 | — | pgadmin |

## Infrastructure (docker-compose.dev.yml)

### order-service
- Build: ./services/order-service
- Ports: 8000:8000
- env_file: .env.dev
- depends_on: postgres-order (healthy), redis (healthy)
- Network: xprnt-network
- restart: unless-stopped

### design-service
- Build: ./services/design-service
- Ports: 8001:8000
- env_file: .env.dev
- depends_on: postgres-design (healthy), minio (healthy), redis (healthy)
- Network: xprnt-network
- restart: unless-stopped

### sync-service-vps
- Build: ./services/sync-service
- Ports: 8002:8000
- env_file: .env.dev + ROLE=vps
- Network: xprnt-network
- restart: unless-stopped

### sync-service-office
- Build: ./services/sync-service
- Ports: 8003:8002
- env_file: .env.dev + ROLE=office
- Network: xprnt-network
- restart: unless-stopped
- Note: port mapping 8003:8002 but app listens on 8000 — likely bug (fixed in prod)

### postgres-order
- Image: postgres:16
- Ports: 5432:5432
- POSTGRES_DB=order_db, POSTGRES_USER=postgres, POSTGRES_PASSWORD=postgres
- Volume: postgres_order_data + ./infra/postgres/init.sql
- Healthcheck: pg_isready -U postgres -d order_db (interval 10s, timeout 5s, retries 5)

### postgres-design
- Image: postgres:16
- Ports: 5433:5432
- POSTGRES_DB=design_db, POSTGRES_USER=postgres, POSTGRES_PASSWORD=postgres
- Volume: postgres_design_data
- Healthcheck: pg_isready -U postgres -d design_db

### minio
- Image: minio/minio:latest
- Ports: 9000:9000, 9001:9001
- MINIO_ROOT_USER=minioadmin, MINIO_ROOT_PASSWORD=minioadmin
- Volume: minio_data
- Command: server /data --console-address ":9001"
- Healthcheck: curl -f http://localhost:9000/minio/health/live

### redis
- Image: redis:7-alpine
- Ports: 6379:6379
- Volume: redis_data
- Healthcheck: redis-cli ping

### pgadmin
- Image: dpage/pgadmin4
- Ports: 5050:80
- PGADMIN_DEFAULT_EMAIL=admin@xprnt.dev, PGADMIN_DEFAULT_PASSWORD=admin
- depends_on: postgres-order, postgres-design

### admin
- Build: ./services/admin Dockerfile.dev
- Container name: xprnt-admin
- Ports: 3001:3001
- Volumes (hot reload): src/, public/, index.html, vite.config.js
- Environment: VITE_API_TARGET=http://order-service:8000
- depends_on: order-service

## Infrastructure (docker-compose.prod.yml)

Відмінності від dev. Детальніше — DEPLOY.md.

### Що включено
- order-service, design-service, sync-service-office, admin
- postgres-order, postgres-design, minio, redis

### Що виключено
- sync-service-vps (тільки на VPS)
- pgadmin

### Ключові відмінності
- Порти прив'язані до 127.0.0.1 (nginx проксіює, не відкриті назовні)
- restart: always
- env_file: .env.prod (не в git, зберігається на сервері)
- Без hot reload volumes для admin
- sync-service-office: виправлено порт 8002:8000 (в dev був баг 8003:8002)

## CI/CD

| Workflow | Файл | Тригер | Runner | Що робить |
|---|---|---|---|---|
| CI | `.github/workflows/ci.yml` | push/PR → main, develop | ubuntu-latest (GitHub) | Запускає pytest для order/design/sync-service + docker build |
| Deploy → Office Server | `.github/workflows/deploy-office.yml` | push → main | self-hosted (office, SVR) | git pull → migrate → docker compose up |

### Deploy послідовність (deploy-office.yml)
1. git pull origin main
2. docker compose down
3. Start infra only (postgres, redis, minio)
4. alembic upgrade head — order-service
5. alembic upgrade head — design-service
6. docker compose up -d --build (всі сервіси)
7. curl /health smoke test

## Cross-service dependencies

| Dependency | From | To | Mechanism | Field |
|---|---|---|---|---|
| design_id in cart items | order-service | design-service | UUID stored in cart_items.designId — no FK | designId (cross-DB, no constraint) |
| productId in FPD designs | design-service | order-service | UUID stored in fpd_designs.productId — no FK | productId (cross-DB, no constraint) |
| user_id in customer designs | design-service | order-service | UUID stored in customer_designs.user_id — no FK | user_id (cross-DB, no constraint) |
| Cart claim → design claim | order-service | design-service | HTTP POST {DESIGN_SERVICE_URL}/designs/claim with JWT; failure non-fatal | src/routes/cart.py |
| JWT verification | design-service | order-service | Shared JWT_SECRET; design-service decodes tokens issued by order-service | JWT_SECRET env var must match |
| "sync:designs" queue | design-service | sync-service | Redis lpush to "sync:designs" list on upload | app/services/design_service.py |
| Product data for calculation | calculator-service | order-service | Intended HTTP GET /api/v1/products/{id}; currently stub | app/services/order_client.py |

## Shared env vars
| Var | Services | Notes |
|---|---|---|
| JWT_SECRET | order-service, design-service | Must be identical — design-service decodes tokens issued by order-service |
| JWT_ALGORITHM | order-service, design-service | Must match; both default to HS256 |
| REDIS_URL | order-service, design-service | Both connect to same Redis instance |
| MINIO_ACCESS_KEY / MINIO_SECRET_KEY | design-service | Also set on minio container as MINIO_ROOT_USER/PASSWORD |

## Authentication model

order-service issues JWTs. design-service validates the same tokens without a DB lookup.

**Flow:**
1. Client calls POST /api/v1/auth/login (or /register, /sms/verify, /google/callback)
2. order-service creates HS256 JWT with payload: `{"sub": "<user_uuid>", "role": "<role_name>", "type": "access", "exp": <utcnow+30min>}`
3. Refresh token (same claims, type="refresh", exp=utcnow+30d) set as HttpOnly cookie `refresh_token`
4. Access token returned in response body as `access_token`
5. Client sends `Authorization: Bearer <token>` on subsequent requests
6. order-service: `get_current_user` calls `verify_token`, then fetches user from DB
7. design-service: `get_current_user` calls `jwt.decode` only — no DB lookup; returns payload dict
8. admin UI stores token in localStorage, decodes role client-side with `atob()`

**Token refresh:** POST /api/v1/auth/refresh reads `refresh_token` cookie; returns new access token + sets new refresh cookie. Admin UI does not call this automatically.

## Roles
| Role | Key permissions |
|---|---|
| admin | All endpoints; all status transitions |
| manager | Most management endpoints; full order status flow except some prepress/postpress steps |
| prepress | Order status: execution→printing→printed; order paths; read-only otherwise |
| postpress | Order status: printed→postprint→done/waiting_delivery; read-only otherwise |
| client | Own orders; own company view; cart operations; no management endpoints |

Roles are seeded at startup: admin, manager, prepress, postpress, client.
Teams seeded: Препрес, Постпрес, Менеджери.

## External services summary
| Service | Used by | Status |
|---|---|---|
| TurboSMS (api.turbosms.ua) | order-service — SMS OTP | Active; failure non-fatal |
| Google OAuth (accounts.google.com) | order-service — social login | Active |
| MinIO (self-hosted S3) | design-service — file/preview storage | Active |
| Redis | order-service (OTP/oauth state), design-service (sync queue) | Active |
| Nova Post API | order-service — intended delivery integration | Not implemented |

## What is NOT implemented (global)
| Feature | Service | Status |
|---|---|---|
| Paginated list responses with total count | order-service | PaginationParams defined; no route uses it |
| Nova Post delivery integration | order-service | Column + model exist; no service |
| FPD design upload/create | design-service | Model + table exist; no endpoint |
| Design listing / user-scoped design list | design-service | No GET /designs/ |
| sync-service file synchronisation | sync-service | Entire service is a stub |
| Calculator actual price logic | calculator-service | Returns 0.00 always |
| calculator-service Docker compose container | calculator-service | Not in docker-compose.dev.yml |
| Admin token auto-refresh | admin | Requires manual re-login after 30 min |
| Admin super orders / payments / deliveries management | admin | No Resource views |
| Admin order status transitions | admin | OrderShow is read-only |
| Email notifications | order-service | No email service |
| Fiscal/invoice document generation | order-service | Fields exist; no generation |
| Admin prod Dockerfile | admin | Dockerfile.dev used in prod — needs proper build + nginx Dockerfile |
| Order number display format (W-/O- prefix) | order-service | source field in DB; formatting not yet in routes/schemas |
