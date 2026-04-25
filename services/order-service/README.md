# order-service

Manages customer print orders for xprnt.

## Endpoints

- `GET /health` — health check
- `GET /docs` — Swagger UI

## Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

## Tests

```bash
pytest tests/ -v
```
