# design-service

Handles design file uploads, storage (MinIO), and preview generation for xprnt.

## Endpoints

- `GET /health` — health check
- `GET /docs` — Swagger UI

## Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```

## Tests

```bash
pytest tests/ -v
```
