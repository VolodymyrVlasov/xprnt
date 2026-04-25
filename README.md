# xprnt — Printing Services Platform

A microservices-based platform for managing print orders, designs, and
synchronization between VPS and office print stations.

## Overview

xprnt automates the end-to-end workflow for a printing business:
customers submit orders with design files, the system stores and processes
designs, and syncs jobs to physical print stations at the office.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   xprnt-network                     │
│                                                     │
│  order-service ──► postgres-order                   │
│       │                                             │
│       ▼                                             │
│     redis ◄── design-service ──► postgres-design   │
│                    │                                │
│                    ▼                                │
│                  minio (S3-compatible storage)      │
│                                                     │
│  sync-service-vps ◄──► sync-service-office          │
└─────────────────────────────────────────────────────┘
```

## Services

| Service | Port | Description |
|---|---|---|
| order-service | 8000 | Manages customer orders |
| design-service | 8001 | Handles design files and previews |
| sync-service (VPS) | 8002 | Sync node running on VPS |
| sync-service (Office) | 8003 | Sync node running at the print office |
| postgres-order | 5432 | Database for orders |
| postgres-design | 5433 | Database for designs |
| minio | 9000/9001 | Object storage for design files |
| redis | 6379 | Cache and message queue |
| pgadmin | 5050 | Database admin UI |

## Quick Start (Dev)

```bash
# 1. Clone the repo
git clone https://github.com/VolodymyrVlasov/xprnt.git
cd xprnt

# 2. Create your dev env file
cp .env.example .env.dev
# Edit .env.dev with your local values

# 3. Start all services
docker-compose -f docker-compose.dev.yml up --build

# 4. Verify health
curl http://localhost:8000/health   # order-service
curl http://localhost:8001/health   # design-service
curl http://localhost:8002/health   # sync-service (vps)
curl http://localhost:8003/health   # sync-service (office)
```

API docs available at:
- http://localhost:8000/docs
- http://localhost:8001/docs
- http://localhost:8002/docs

## Environment Variables

See [.env.example](.env.example) for all required variables.

Copy to `.env.dev` for local development and to `.env.prod` for production.
Never commit `.env.dev` or `.env.prod` to version control.

Key variables:

| Variable | Description |
|---|---|
| `ENV` | Environment name (`dev` / `prod`) |
| `ORDER_DB_URL` | PostgreSQL connection for order-service |
| `DESIGN_DB_URL` | PostgreSQL connection for design-service |
| `MINIO_ENDPOINT` | MinIO/S3 endpoint |
| `REDIS_URL` | Redis connection URL |
| `JWT_SECRET` | Secret key for JWT signing — change in production |

## Git Flow

```
main          ← production-ready, triggers deploy
  └─ develop  ← integration branch
       ├─ feature/xxx
       ├─ fix/xxx
       └─ chore/xxx
```

- Branch from `develop` for all new work
- PR into `develop` first; merge to `main` only for releases
- CI runs on every push and PR to `develop` and `main`
- Deploy runs automatically on push to `main`

## Deployment

Deployment is handled via GitHub Actions (see [.github/workflows/deploy.yml](.github/workflows/deploy.yml)).

On push to `main`:
1. GitHub Actions SSHes into the VPS
2. Pulls latest code
3. Rebuilds and restarts all containers via `docker-compose.prod.yml`
4. Sends a Telegram notification with the result

Required GitHub Secrets:

| Secret | Description |
|---|---|
| `VPS_HOST` | VPS IP address or hostname |
| `VPS_USER` | SSH username |
| `VPS_SSH_KEY` | Private SSH key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel ID |
