# PROJECT MAP — design-service
_Last updated: 2026-05-13_

## Service overview
| Item | Value |
|---|---|
| Location | services/design-service/ |
| Runtime | Python 3.x / FastAPI 0.115.6 |
| Database | PostgreSQL — design_db |
| Object storage | MinIO (buckets: uploads, previews) |
| Cache | Redis 7 (sync queue: list key "sync:designs") |
| API prefix | /designs |
| Dev port | 8001 (host) → 8000 (container) |
| Health | GET /health → {"status": "ok", "service": "design-service"} |
| Docs | /docs, /redoc |

## File index
| File | Responsibility |
|---|---|
| services/design-service/app/config.py | Pydantic settings — DB, JWT, MinIO, Redis |
| services/design-service/app/main.py | FastAPI app factory, lifespan (MinIO bucket init, Redis init), CORS, router |
| services/design-service/app/database.py | Async SQLAlchemy engine + session factory + DeclarativeBase + get_db dependency |
| services/design-service/app/dependencies.py | get_current_user, get_current_user_optional (JWT decode only, no DB lookup), get_minio, get_redis |
| services/design-service/app/models/design.py | CustomerDesigns, FPDDesigns, Designs models + DesignType enum |
| services/design-service/app/repository/design_repository.py | DesignRepository — create_customer_design, create_design, update_customer_design, get_design_by_id, claim_by_session |
| services/design-service/app/routes/design.py | Upload design, claim designs, get design |
| services/design-service/app/services/design_service.py | upload_customer_design (11-step pipeline), get_design, claim_designs |
| services/design-service/app/schemas/design.py | DesignMetadata, CustomerDesignResponse, DesignResponse, ClaimDesignsRequest/Response |
| services/design-service/app/utils/file_storage.py | MinIOClient — ensure_buckets, upload_file, get_file_url (presigned 7d), delete_file, generate_object_name |
| services/design-service/app/utils/preview_generator.py | generate_preview — JPEG thumbnail from raster or PDF first page |
| services/design-service/app/utils/technical_validation.py | validate_design_metadata — DPI, dimensions, color model check for raster and PDF |
| services/design-service/app/utils/color_converter.py | cmyk_to_rgb, convert_image_cmyk_to_rgb (PIL) |
| services/design-service/app/utils/pdf_utils.py | get_pdf_page_size_mm (pypdf), get_pdf_color_model (pdfplumber), render_pdf_first_page_to_image (pdf2image/poppler) |
| services/design-service/alembic/versions/0001_initial_design_tables.py | Initial: customer_designs, fpd_designs, designs tables |
| services/design-service/alembic/versions/0002_add_guest_session_and_user_id.py | Add guest_session_id + index, user_id to customer_designs |

## Models

### CustomerDesigns
Table: `customer_designs` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| filename | String | NOT NULL |
| path | String | NOT NULL — MinIO object name in uploads bucket |
| previewPath | String | nullable — MinIO object name in previews bucket |
| metadata | JSONB | nullable — DesignMetadata JSON (dpi/width/height/color current+target) |
| guest_session_id | String(36) | nullable, indexed — anonymous session ID |
| user_id | UUID | nullable — order-service user UUID (no FK constraint, cross-DB) |
| createdAt | DateTime(tz) | NOT NULL server_default now() |
| updatedAt | DateTime(tz) | NOT NULL server_default now() onupdate now() |

### FPDDesigns
Table: `fpd_designs` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| productId | UUID | nullable — cross-DB ref to order-service products, no FK constraint |
| designJson | JSONB | NOT NULL — FPD design JSON payload |
| previewPath | String | nullable |
| svgPath | String | nullable |
| createdAt | DateTime(tz) | NOT NULL server_default now() |
| updatedAt | DateTime(tz) | NOT NULL server_default now() onupdate now() |

### Designs
Table: `designs` | PK: `id` UUID
Enum `designtype`: `CUSTOMER_DESIGN`, `FPD_DESIGN`, `OTHER_DESIGN`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| designType | Enum(designtype) | NOT NULL |
| customerDesignId | UUID | FK → customer_designs.id ON DELETE CASCADE nullable |
| fpdDesignId | UUID | FK → fpd_designs.id ON DELETE CASCADE nullable |
| createdAt | DateTime(tz) | NOT NULL server_default now() |
| updatedAt | DateTime(tz) | NOT NULL server_default now() onupdate now() |

Relationships: `customerDesign` (joined load → CustomerDesigns), `fpdDesign` (joined load → FPDDesigns)

## Endpoints

### /designs
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /designs/upload | Upload design file (multipart); runs validation + preview generation; pushes event to Redis sync queue | Optional | — |
| POST | /designs/claim | Claim all guest designs for a session (set user_id on unclaimed records) | Yes | any |
| GET | /designs/{design_id} | Get design with presigned file/preview URLs (7-day TTL) | Yes | any |

Upload multipart form fields:
- `file` (required) — UploadFile; allowed: jpg, jpeg, png, pdf; max 200 MB
- `targetWidth` (float, optional) — target width mm
- `targetHeight` (float, optional) — target height mm
- `targetColor` (string, default "cmyk") — expected color model
- `targetDpi` (int, default 300) — expected DPI
- `X-Guest-Session-ID` (header, optional) — anonymous session id for guest linking

## Services / Business logic
| File | Method | Description |
|---|---|---|
| app/services/design_service.py | upload_customer_design | 1. Validate extension; 2. Read bytes (check 200 MB limit); 3. Upload original to tmp/ in MinIO uploads; 4. Generate JPEG preview via generate_preview; 5. Upload preview to MinIO previews bucket; 6. Run validate_design_metadata (non-fatal); 7. Write CustomerDesigns + Designs to DB; 8. lpush to Redis "sync:designs" (non-fatal on failure); 9. Move original to permanent {design_id}/{filename}; 10. Delete tmp object; 11. Build DesignResponse with presigned URLs |
| app/services/design_service.py | get_design | Fetch from DB; generate presigned URLs for file and preview |
| app/services/design_service.py | claim_designs | Bulk UPDATE customer_designs SET user_id=X WHERE guest_session_id=Y AND user_id IS NULL; returns count |
| app/utils/technical_validation.py | validate_design_metadata | PIL for raster (DPI/size/color); pypdf+pdfplumber for PDF; returns DesignMetadata with isValid flags; never raises |
| app/utils/preview_generator.py | generate_preview | 1200x1200 max JPEG thumbnail; CMYK→RGB conversion; returns None on failure |
| app/utils/file_storage.py | get_file_url | presigned_get_object with 7-day expiry |
| app/utils/file_storage.py | generate_object_name | uuid4_hex + safe_name, optional prefix (tmp/ or previews/) |

## Config / Env vars
| Var | Default | Purpose |
|---|---|---|
| DESIGN_DB_URL | postgresql+asyncpg://postgres:postgres@postgres-design:5432/design_db | Async PostgreSQL URL |
| JWT_SECRET | change_me_in_production | Shared HMAC key — must match order-service JWT_SECRET |
| JWT_ALGORITHM | HS256 | JWT algorithm |
| MINIO_ENDPOINT | minio:9000 | MinIO host:port |
| MINIO_ACCESS_KEY | minioadmin | MinIO access key |
| MINIO_SECRET_KEY | minioadmin | MinIO secret key |
| MINIO_SECURE | false | Use HTTPS for MinIO |
| REDIS_URL | redis://redis:6379 | Redis connection |

## External services
| Service | Used for | Files | Status |
|---|---|---|---|
| MinIO (S3-compatible, port 9000) | File upload, preview storage, presigned URL generation | app/utils/file_storage.py | Active |
| Redis (port 6379) | Push design events to "sync:designs" list for sync-service | app/services/design_service.py | Active; push failure is non-fatal |

## Migrations
| Revision | Down revision | Tables affected | Description |
|---|---|---|---|
| 0001 | None | customer_designs, fpd_designs, designs | Initial tables + designtype enum |
| 0002 | 0001 | customer_designs | Add guest_session_id String(36) with index; add user_id UUID nullable |

## Requirements
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.0
redis==5.2.1
minio==7.2.12
python-multipart==0.0.20
python-jose[cryptography]==3.3.0
Pillow==11.0.0
pdf2image==1.17.0
pypdf==5.1.0
pdfplumber==0.11.4
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
```

## Known issues and TODOs
| Location | Note |
|---|---|
| app/dependencies.py | get_current_user decodes JWT but does NOT verify user exists in DB — a valid token for a deleted user passes auth |
| app/utils/pdf_utils.py | render_pdf_first_page_to_image depends on poppler-utils system package in Docker image |
| app/services/design_service.py | On MinIO move failure (step 9/10), DB record may retain tmp/ path — potential orphan object |
| app/models/design.py | No index on customer_designs.user_id — queries by user will scan at scale |
| app/utils/technical_validation.py | Raster DPI defaults to 72 when EXIF DPI absent — may produce false isValid=false for images without DPI metadata |
| app/utils/file_storage.py | upload_file and get_file_url use asyncio.get_event_loop() (deprecated pattern — should use asyncio.get_running_loop()) |

## What is NOT implemented
| Feature | Status |
|---|---|
| FPD design upload/create endpoint | FPDDesigns model + table exist; no route or service logic |
| Design delete endpoint | No DELETE /designs/{id} route |
| Design list endpoint | No GET /designs/ list; no user-scoped listing |
| Permanent (non-expiring) file URLs | All URLs are presigned with 7-day TTL |
| sync-service consumer | Redis "sync:designs" events are pushed but the sync-service consumer is a stub |
| Access control on design GET | Any authenticated user can fetch any design_id — no ownership check |
