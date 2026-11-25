# DEPLOY — xprnt
_Last updated: 2026-05-14_

---

## Принципи

- **Один код — різні env.** Репо однакове для офісу і VPS. Різниця — тільки `.env` і `docker-compose.prod.yml` на кожному сервері.
- **Окремі гілки для серверів не використовуємо** — антипатерн (розходження коду, подвійні merge).
- **Адмінка підключається тільки до офісного сервера** — менеджери через LAN або L2TP VPN.
- **VPS — поза scope зараз.** Підключається окремим етапом після реалізації адмінки і основних сервісів.

---

## Гілки

| Гілка | Призначення | Деплой |
|---|---|---|
| `develop` | Активна розробка | ❌ тільки локально |
| `feat/*`, `fix/*` | Фічі і фікси | ❌ тільки локально |
| `main` | Стабільний продакшн | ✅ автоматично → офісний сервер |

**Правило:** `develop` → PR → `main` → автодеплой на офіс.

---

## Автодеплой — механізм

> `<OFFICE_SERVER_IP>` — LAN-адреса офісного сервера; актуальне значення — в OFFICE_SERVER.md (не в репо).

GitHub не може сам підключитись до <OFFICE_SERVER_IP> (приватна мережа, зовні тільки 80/443).
**Рішення: self-hosted runner** — сервер сам підключається до GitHub outbound HTTPS і чекає задачі.

```
push → main
    ↓
GitHub Actions виявляє self-hosted runner (label: office)
    ↓
Runner на <OFFICE_SERVER_IP> отримує задачу
    ↓
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
    ↓
alembic upgrade head  ← order-service
alembic upgrade head  ← design-service
    ↓
curl /health  (smoke test)
```

---

## Структура файлів на сервері

```
/opt/xprnt/
├── repo/                     ← git clone (одноразово)
│   ├── docker-compose.prod.yml
│   ├── .github/workflows/
│   └── services/
├── .env.prod                 ← НЕ в git, тільки на сервері
├── actions-runner/           ← self-hosted runner
├── data/orders/              ← активні замовлення
├── tempdata/uploads/         ← тимчасові файли після sync
└── db_recovery/              ← pg_dump бекапи
```

---

## Одноразове налаштування сервера

### 1. Клонувати репо

```bash
cd /opt/xprnt
git clone https://github.com/VolodymyrVlasov/xprnt.git repo
```

### 2. Створити .env.prod

```bash
nano /opt/xprnt/.env.prod
```

```env
ENV=prod

# order-service
ORDER_DB_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@postgres-order:5432/order_db
REDIS_URL=redis://redis:6379
JWT_SECRET=CHANGE_THIS_TO_STRONG_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
TURBOSMS_API_KEY=
TURBOSMS_SENDER=xprnt
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://<OFFICE_SERVER_IP>:8000/api/v1/auth/google/callback
OTP_CODE_LENGTH=6
OTP_EXPIRE_MINUTES=5
OTP_MAX_ATTEMPTS=3
OTP_RESEND_COOLDOWN_SECONDS=60
DESIGN_SERVICE_URL=http://design-service:8001

# design-service
DESIGN_DB_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@postgres-design:5432/design_db
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=CHANGE_MINIO_SECRET
MINIO_SECURE=false

# postgres
POSTGRES_PASSWORD=STRONG_PASSWORD
```

### 3. Встановити self-hosted runner

GitHub → репо → Settings → Actions → Runners → **New self-hosted runner** → Linux x64.
Виконати команди які покаже GitHub:

```bash
cd /opt/xprnt
mkdir actions-runner && cd actions-runner
# команди завантаження і config.sh — копіювати з GitHub UI
./config.sh --url https://github.com/VolodymyrVlasov/xprnt --token TOKEN_FROM_GITHUB --labels office
```

Запустити як сервіс:

```bash
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

Перевірка: GitHub → Settings → Actions → Runners → статус **Idle**.

---

## GitHub Actions Workflow

Файл: `.github/workflows/deploy-office.yml`

```yaml
name: Deploy → Office Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: [self-hosted, office]
    timeout-minutes: 15

    steps:
      - name: Pull latest code
        run: |
          cd /opt/xprnt/repo
          git fetch origin main
          git reset --hard origin/main

      - name: Copy .env.prod
        run: |
          cp /opt/xprnt/.env.prod /opt/xprnt/repo/.env.prod

      - name: Stop containers
        run: |
          cd /opt/xprnt/repo
          docker compose -f docker-compose.prod.yml down

      - name: Build and start containers
        run: |
          cd /opt/xprnt/repo
          docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

      - name: Wait for DBs
        run: |
          sleep 10
          docker exec postgres-order pg_isready -U postgres -d order_db
          docker exec postgres-design pg_isready -U postgres -d design_db

      - name: Run migrations — order-service
        run: |
          docker exec order-service alembic upgrade head

      - name: Run migrations — design-service
        run: |
          docker exec design-service alembic upgrade head

      - name: Smoke test
        run: |
          sleep 5
          curl -f http://localhost:8000/health
          curl -f http://localhost:8001/health
          curl -f http://localhost:8002/health
```

---

## Rollback

```bash
cd /opt/xprnt/repo
git log --oneline -5           # знайти попередній commit
git reset --hard <commit_hash>
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
docker exec order-service alembic upgrade head
docker exec design-service alembic upgrade head
```

---

## docker-compose.prod.yml — відмінності від dev

| Параметр | Dev | Prod |
|---|---|---|
| env_file | `.env.dev` | `.env.prod` |
| Порти postgres/redis | відкриті назовні | тільки внутрішня мережа |
| pgadmin | є | прибрати |
| restart | unless-stopped | always |
| Hot reload volumes | є | прибрати |
| SQLAlchemy echo | увімкнено (ENV=dev) | вимкнено (ENV=prod) |

---

## Архітектура двох серверів (майбутнє)

```
VPS (публічний)                    Офіс <OFFICE_SERVER_IP>
├── order-service   :8000          ├── order-service   :8000
├── design-service  :8001          ├── design-service  :8001
├── sync-service    :8002          ├── sync-service    :8002
├── postgres-order                 ├── postgres-order
├── postgres-design                ├── postgres-design
├── minio                          ├── minio
│   ├── previews (постійно)        │   ├── originals (постійно)
│   └── originals (тимчасово)      │   └── previews (копія)
└── redis (черга sync)             └── redis
              ↕  sync-service
```

---

## Синхронізація між серверами

### Нумерація замовлень

`order_numbers` — BigInt autoincrement незалежно на кожному сервері.
Щоб уникнути колізій при злитті, поле `source` ENUM(`web`, `office`) + префікс при відображенні:

| Сервер | source | Відображення |
|---|---|---|
| VPS | `web` | W-0001, W-0002 |
| Офіс | `office` | O-0001, O-0002 |

Реалізація: поле `source` в таблиці `order_numbers`, NOT NULL, default `office`.
Номер для відображення: `{W або O}-{id:04d}` — формується на рівні сервісу або схеми відповіді.

### Таблиця синхронізації

| Сутність | Напрямок | Коментар |
|---|---|---|
| Замовлення (orders + cart) | ↔ двосторонній | Разом із залежним user |
| Користувачі (users) | ↔ двосторонній | Синхронізуються разом із замовленням |
| Продукти / Категорії / Ціни | Офіс → VPS | Тільки офіс створює (менеджер/адмін) |
| Оригінали дизайн-файлів з VPS | VPS → Офіс | Клієнт завантажив на сайті |
| Оригінали дизайн-файлів з офісу | Залишаються на офісі | Не рухаються |
| Превью з VPS | Залишаються на VPS | Не рухаються |
| Превью з офісу | Офіс → VPS | Щоб клієнт бачив замовлення онлайн |

### Обмеження поточної версії

Sync-service не реалізований — обидва сервери є **незалежними інстансами** з власними БД.
Синхронізація буде додана окремим етапом разом з реалізацією sync-service.

---

## Артикул і SKU продукту

Додано до моделі `Products`:

| Поле | Тип | Опис |
|---|---|---|
| `article` | Integer, autoincrement, unique, NOT NULL | Системний числовий код. Генерується автоматично. Тільки офіс створює продукти — колізій між серверами немає. |
| `sku` | String, nullable | Людиночитаємий код (напр. `STK-A4-GLOS`). Вводить менеджер вручну. |

---

## Додавання VPS (пізніше)

1. Встановити self-hosted runner на VPS, label: `vps`
2. Покласти `.env.prod` на VPS (інші значення: DB URL, MinIO endpoint, домен, GOOGLE_REDIRECT_URI)
3. Додати job у workflow:

```yaml
  deploy-vps:
    runs-on: [self-hosted, vps]
    needs: deploy    # спочатку офіс, потім VPS
    steps:
      # ті самі steps що і для офісу
```
