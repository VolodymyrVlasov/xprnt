# order-service — Full Technical Snapshot

Generated: 2026-05-07

---

## 1. DATABASE TABLES

All tables use `UUID` primary keys (PostgreSQL `uuid` type, `default=uuid.uuid4`). All include `createdAt` / `updatedAt` timestamp columns via `TimestampMixin` unless noted.

### Reference / lookup tables

| Table | Key columns |
|-------|------------|
| `roles` | `id`, `role` (unique) |
| `teams` | `id`, `name`, `description` |
| `company_types` | `id`, `name`, `shortName` |
| `measurement_units` | `id`, `measurementUnit`, `classifier` |
| `delivery_types` | `id`, `name`, `description`, `data` (JSON) |
| `addresses` | `id`, `country`, `district`, `city`, `street`, `building`, `apartment`, `warehouse` |
| `images` | `id`, `filePath`, `description` |
| `document_templates` | `id`, `document` (Text) |
| `sellers` | `id`, `companyTypeId` → `company_types`, `name`, `shortName` |
| `sizes` | `id`, `unitId` → `measurement_units`, `width`, `height`, `diameter`, `radius`, `volume`, `tShirtSize_EU`, `tShirtSize_age`, `rollWidth` |
| `bank_requisites` | `id`, `sellerId`, `name`, `isDefault`, `bankName`, `bankMFO`, `iban`, `swiftCode`, `currency`, `bankAddressId`, `accountName`, `edrpou`, `legalAddressId`, `taxStatus`, `finishAt`, `updateAuthorId`→`users` (use_alter) |
| `payment_types` | `id`, `name`, `description`, `data` (JSON), `bankRequisiteId`, `transactionFee` |

### Core entity tables

| Table | Key columns |
|-------|------------|
| `contracts` | `id`, `documentTemplateId` → `document_templates`, `documentPath` |
| `companies` | `id`, `contactUserId`→`users` (use_alter), `edrpouCode` (unique), `itnCode` (unique), `name` (unique), `address1`, `address2`, `email`, `phone1`, `phone2`, `companyTypeId`, `contractId`, `headOfId`→`users` (use_alter) |
| `users` | `id`, `companyId`→`companies`, `name`, `middlename`, `lastname`, `phone1`, `phone2`, `email` (unique), `telegram`, `roleId`→`roles`, `teamId`→`teams`, `novaPostUserId`, `commentId`→`comments` (use_alter), `contractId`, `hashedPassword`, `phoneVerified` (bool, default false), `googleId` (unique, nullable), `authProvider` (default 'email') |
| `categories` | `id`, `name`, `description`, `imageId`, `teamId`, `classifier`, `upsellsCategoryId` (self-ref), `crossellsCategoryId` (self-ref) |
| `price_multipliers` | `id`, `values` (JSON) |
| `prices` | `id`, `productId`→`products`, `primeCostEUR`, `fxRateUsed`, `priceMultiplierId`, `values` (JSON), `previousPriceId` (self-ref), `nextPriceId` (self-ref), `startAt`, `finishAt` |
| `products` | `id`, `name`, `shortName`, `description`, `categoryId`→`categories`, `imageId`, `sizeId`, `isDeliverable` (bool), `inStock` (bool), `packageSizeId`, `measurementUnitId`, `activePriceId`→`prices` |
| `gallery` | `id`, `productId`→`products`, `categoryId`, `filePath` |
| `cart` | `id`, `status` (enum), `totalPrice`, `customerId`→`users` (nullable), `currency` (default UAH) |
| `cart_items` | `id`, `cartId`→`cart`, `categoryId`→`categories`, `cartItemType` (enum), `name`, `shortName`, `amount`, `unitPrice`, `totalPrice`, `pricedAt`, `designId` |
| `cart_item_products` | `id`, `cartItemId`→`cart_items`, `productId`→`products`, `priceId`→`prices` (nullable), `priceTierQty`, `pricedAt`, `name`, `shortName` (Text, nullable), `amount`, `price`, `priceTotal` |
| `order_numbers` | `id` (BigInteger, autoincrement), `createdAt`, `createdBy`→`users` — no TimestampMixin |
| `comments` | `id`, `entityType` (enum), `entityId` (uuid), `text`, `createdBy`→`users` |
| `super_orders` | `id`, `orderNumberId`→`order_numbers` (unique), `companyId`→`companies`, `contactUserId`→`users`, `paymentTypeId`, `currency`, `billingPeriodStart`, `billingPeriodEnd`, `invoiceNumber`, `invoiceDate`, `status` (enum), `total` |
| `order_paths` | `id`, `orderId`→`orders`, `path`, `docsPath` |
| `orders` | `id`, `orderNumberId`→`order_numbers` (unique), `superOrderId`→`super_orders`, `sellerId`→`sellers`, `customerId`→`users`, `paymentUserId`→`users`, `deliveryUserId`→`users`, `companyId`→`companies`, `managerId`→`users`, `paymentId`→`payments` (nullable), `deliveryId`→`deliveries` (nullable), `totalPrice`, `status` (enum), `orderPathId`→`order_paths` (use_alter), `cartId`→`cart` (unique), `finishAt`, `doneAt` |
| `payments` | `id`, `paymentTypeId`→`payment_types`, `orderId`→`orders` (use_alter, nullable), `superOrderId`→`super_orders` (nullable), `amount`, `currency`, `fiscalReceiptNumber`, `status` (enum) |
| `deliveries` | `id`, `deliveryUserId`→`users`, `deliveryTypeId`→`delivery_types`, `addressId`→`addresses`, `ttnNumber` |

### Circular FK chains resolved with `use_alter=True`
- `companies.contactUserId` → `users`
- `companies.headOfId` → `users`
- `users.commentId` → `comments`
- `orders.orderPathId` → `order_paths`
- `payments.orderId` → `orders`
- `bank_requisites.updateAuthorId` → `users`

---

## 2. ENUMS

All defined as Python `str` + `enum.Enum`, stored as PostgreSQL ENUM types.

| Enum | Values |
|------|--------|
| `CartStatus` | `active`, `locked`, `ordered`, `abandoned` |
| `CartItemType` | `configured`, `simple` |
| `OrderStatus` | `pending`, `paid`, `execution`, `printing`, `printed`, `postprint`, `done`, `waiting_delivery`, `shipped`, `successful`, `canceled`, `returned` |
| `SuperOrderStatus` | `open`, `invoiced`, `paid`, `closed`, `cancelled` |
| `CommentEntityType` | `order` |
| `PaymentStatus` | `pending`, `paid`, `failed`, `refunded` |

---

## 3. API ENDPOINTS

Base prefix: `/api/v1`. Auth = Bearer JWT unless noted.

### Auth — `/api/v1/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | — | Register with email/password; creates company + user; returns access token + refresh cookie |
| POST | `/login` | — | Email + password login; returns access token + refresh cookie |
| POST | `/refresh` | refresh cookie | Issue new access + refresh tokens |
| POST | `/logout` | — | Deletes `refresh_token` cookie |
| POST | `/sms/send-code` | — | Normalize phone, generate OTP in Redis, send via TurboSMS; returns `dev_code` if `ENV=dev` |
| POST | `/sms/verify` | — | Verify OTP, create or find user by phone, issue JWT |
| GET | `/google` | — | Generate OAuth2 state, store in Redis (TTL 600s), return Google auth URL |
| GET | `/google/callback` | — | Validate state, exchange code, get user info, create/link user, issue JWT |

### Users — `/api/v1/users`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/me` | required | Return current user |
| GET | `/` | manager/admin | List all users |
| GET | `/{user_id}` | required | Get user (self or manager/admin) |
| PUT | `/{user_id}` | required | Update user (self or manager/admin) |

### Companies — `/api/v1/companies`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | required | List companies |
| POST | `/` | manager/admin | Create company (409 if EDRPOU duplicate) |
| GET | `/{company_id}` | required | Get company |
| PUT | `/{company_id}` | manager/admin | Update company |

### Products — `/api/v1/products`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | List products; filter by `category_id`, `in_stock` |
| POST | `/` | manager/admin | Create product |
| GET | `/{product_id}` | — | Get product |
| PUT | `/{product_id}` | manager/admin | Update product |
| DELETE | `/{product_id}` | manager/admin | Deactivate product (sets `inStock=false`) |

### Categories — `/api/v1/categories`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | List categories |
| POST | `/` | manager/admin | Create category |
| GET | `/{category_id}` | — | Get category with products |
| PUT | `/{category_id}` | manager/admin | Update category |

### Cart — `/api/v1/cart`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | optional | Create cart; assigns `customerId` if authenticated |
| GET | `/{cart_id}` | optional | Get cart; enforces ownership if both user and `customer_id` set |
| POST | `/{cart_id}/items` | optional | Add item + products to cart |
| PUT | `/{cart_id}/items/{item_id}` | optional | Update item amount/price/name |
| DELETE | `/{cart_id}/items/{item_id}` | optional | Remove item |
| POST | `/{cart_id}/lock` | required | Lock cart for ordering |
| POST | `/{cart_id}/claim` | required | Assign anonymous cart to authenticated user |

### Orders — `/api/v1/orders`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | required | Create order from locked cart |
| GET | `/my` | required | Get current user's orders |
| GET | `/` | required | List orders (staff: all; client: own company) |
| GET | `/{order_id}` | required | Get order (with company access check for clients) |
| PUT | `/{order_id}/status` | manager/admin/prepress/postpress | Change order status (role-gated transitions) |
| POST | `/{order_id}/delivery` | manager/admin | Attach delivery record |
| POST | `/{order_id}/payment` | manager/admin | Attach payment; auto-advance to `paid` if payment already paid |
| GET | `/{order_id}/path` | manager/prepress/postpress/admin | Get order path |
| GET | `/{order_id}/comments` | required | Get comments for order |

### Super Orders — `/api/v1/super-orders`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | manager/admin | Create super order |
| GET | `/` | manager/admin | List super orders; filter by `company_id`, `status` |
| GET | `/{id}` | manager/admin | Get super order |
| PUT | `/{id}` | manager/admin | Update super order fields |
| POST | `/{id}/orders` | manager/admin | Add order (validates same company, non-terminal status) |
| DELETE | `/{id}/orders/{order_id}` | manager/admin | Remove order (only if super order is `open`) |
| PUT | `/{id}/status` | manager/admin | Transition status (open→invoiced→paid→closed; open→cancelled) |

### Payments — `/api/v1/payments`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | manager/admin | Register payment; auto-attaches to order if `order_id` provided |
| GET | `/` | manager/admin | List payments; filter by `order_id` or `super_order_id` |
| GET | `/{id}` | manager/admin | Get payment |
| PUT | `/{id}/status` | manager/admin | Update payment status |

### Deliveries — `/api/v1/deliveries`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | required | Create delivery |
| GET | `/` | manager/admin | List deliveries; filter by `has_ttn` |
| GET | `/{id}` | required | Get delivery |
| PUT | `/{id}` | manager/admin | Update TTN number |

### Order Paths — `/api/v1/order-paths`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | manager/prepress/admin | Create order path (409 if already exists for order) |
| GET | `/order/{order_id}` | manager/prepress/postpress/admin | Get path by order |
| PUT | `/{order_path_id}` | manager/prepress/admin | Update path/docs_path |

### Prices — `/api/v1/prices`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | manager/admin | Create price; closes current active price (sets `finishAt`, `nextPriceId`); sets `activePriceId` on product |
| GET | `/product/{product_id}` | — | Get full price history |
| GET | `/product/{product_id}/active` | — | Get active price |
| GET | `/{id}` | — | Get price by ID |

### Price Multipliers — `/api/v1/price-multipliers`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | List all |
| POST | `/` | admin | Create |
| GET | `/{id}` | — | Get |
| PUT | `/{id}` | admin | Update `values` JSON |

### Comments — `/api/v1/comments`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | required | Add comment to any entity |
| GET | `/` | required | List comments by `entity_type` + `entity_id` |
| DELETE | `/{id}` | required | Delete comment (own or manager/admin) |

### References — `/api/v1/references`

Sub-resources with standard CRUD. All GET endpoints are public (no auth).

| Sub-resource | Write auth |
|--------------|-----------|
| `/roles` | admin |
| `/delivery-types` | manager/admin |
| `/payment-types` | manager/admin |
| `/sellers` | admin |
| `/measurement-units` | manager/admin |
| `/sizes` | manager/admin |
| `/teams` | admin |

### Health
`GET /health` — returns `{"status": "ok", "service": "order-service"}`

---

## 4. SCHEMAS

All Pydantic v2. Response models use `ConfigDict(from_attributes=True)`.

### Auth (`src/schemas/auth.py`)
- `RegisterRequest`: email, password, name, lastname, phone1, company_name, company_edrpou
- `LoginRequest`: email, password
- `TokenResponse`: access_token, token_type="bearer"
- `RefreshRequest`: refresh_token
- `SMSSendCodeRequest`: phone (validated Ukrainian format via `field_validator`)
- `SMSVerifyRequest`: phone, code, name? , lastname?
- `SMSVerifyResponse`: access_token, token_type, is_new_user
- `GoogleAuthUrlResponse`: auth_url
- `GoogleCallbackResponse`: access_token, token_type, is_new_user

### Cart (`src/schemas/cart.py`)
- `CartItemProductCreate`: product_id, name, amount, price; optional: price_id, price_tier_qty, priced_at, price_total, short_name
- `CartItemCreate`: category_id, cart_item_type (default `simple`), name, amount, unit_price; optional: short_name, design_id, total_price, priced_at, products[]
- `CartItemUpdate`: amount?, unit_price?, name?
- `CartItemProductResponse`: id, cart_item_id, product_id, name, amount, price, price_total; optional: price_id, price_tier_qty, priced_at, short_name
- `CartItemResponse`: id, cart_id, category_id, cart_item_type, name, amount, unit_price, total_price; optional: short_name, priced_at, design_id, products[]
- `CartResponse`: id, status, total_price, currency; optional: customer_id; items[]

### Order (`src/schemas/order.py`)
- `OrderCreate`: cart_id, seller_id, payment_type_id, currency="UAH"; optional: delivery_type_id, delivery_address_id
- `OrderStatusUpdate`: status (OrderStatus)
- `OrderResponse`: id, order_number_id, customer_id, company_id, seller_id, status, total_price, currency, cart_id; optional: super_order_id, payment_id, delivery_id, manager_id, finish_at, done_at

### Super Order (`src/schemas/super_order.py`)
- `SuperOrderCreate`: company_id, payment_type_id, currency; optional: contact_user_id, billing_period_start, billing_period_end
- `SuperOrderUpdate`: optional: invoice_number, invoice_date, status, total
- `SuperOrderStatusUpdate`: status
- `SuperOrderAddOrder`: order_id
- `SuperOrderResponse`: full fields + `orders: list[OrderBriefResponse]`
- `OrderBriefResponse`: id, order_number_id, status, total_price, created_at

### Other schemas (one file per domain)
- `UserCreate`, `UserUpdate`, `UserResponse` — user fields
- `CompanyCreate`, `CompanyUpdate`, `CompanyResponse` — company fields
- `ProductCreate`, `ProductUpdate`, `ProductResponse` — product fields + active_price
- `CategoryCreate`, `CategoryUpdate`, `CategoryResponse` — category + products list
- `PriceCreate`, `PriceResponse` — price fields + JSON values
- `PriceMultiplierCreate`, `PriceMultiplierUpdate`, `PriceMultiplierResponse`
- `PaymentCreate`, `PaymentStatusUpdate`, `PaymentResponse`
- `DeliveryCreate`, `DeliveryResponse`
- `OrderPathCreate`, `OrderPathUpdate`, `OrderPathResponse`
- `CommentCreate`, `CommentResponse`
- Reference schemas: `RoleCreate/Response`, `TeamCreate/Update/Response`, `DeliveryTypeCreate/Update/Response`, `PaymentTypeCreate/Update/Response`, `SellerCreate/Update/Response`, `MeasurementUnitCreate/Response`, `SizeCreate/Update/Response`

---

## 5. SERVICES & BUSINESS LOGIC

### `src/services/auth.py`
- `hash_password(password)` / `verify_password(plain, hashed)` — bcrypt via passlib
- `create_access_token(data, expires_delta?)` — HS256 JWT, `type=access`, TTL from config
- `create_refresh_token(data)` — HS256 JWT, `type=refresh`, TTL 30 days
- `verify_token(token, token_type)` — decodes + validates `type` field

### `src/services/cart.py`
- `create_cart(db, customer_id?)` — creates active cart
- `get_cart(db, cart_id)` — fetches with items+products; raises 404
- `add_item(db, cart_id, data)` — validates cart active, creates CartItems + CartItemProducts, recalculates total
- `update_item(db, cart_id, item_id, data)` — updates fields, recalculates total_price when amount/unit_price change
- `remove_item(db, cart_id, item_id)` — deletes item, recalculates total
- `lock_cart(db, cart_id)` — sets status=locked (validates active)
- `_recalculate_cart_total(db, cart)` — sums item total_prices

### `src/services/order.py`
- `create_order(db, data, current_user_id)` — validates cart locked + no existing order, creates OrderNumber, creates Order with status=pending, transitions cart to ordered
- `change_status(db, order_id, data, role)` — validates transition against `_STATUS_TRANSITIONS` table:
  - **manager**: full lifecycle except execution/printing/postprint-specific steps
  - **prepress**: only `execution→printing`, `printing→printed`
  - **postpress**: only `printed→postprint`, `postprint→done/waiting_delivery`
  - **admin**: any status → any status

### `src/services/otp.py` — `OTPService`
- `generate_and_store(phone_e164)` — checks 60s resend cooldown; stores JSON `{code, attempts, created_at}` in Redis with TTL (`OTP_EXPIRE_MINUTES * 60`)
- `verify(phone_e164, code)` — increments attempts; raises 429 on max exceeded (deletes key); deletes key on correct match; persists updated attempts on mismatch
- `delete(phone_e164)` — removes key

### `src/services/sms.py` — `TurboSMSService`
- `send_otp(phone, code)` — POSTs to `https://api.turbosms.ua/message/send.json` with `Authorization: Bearer {api_key}`; message template: `"xprnt код: {code}. Дійсний 5 хвилин."`. Never raises — returns `True`/`False`.
- `get_balance()` — GET `/user/balance.json`

### `src/services/google_auth.py` — `GoogleAuthService`
- `get_auth_url(state)` — builds Google OAuth2 URL with `openid email profile` scope
- `exchange_code(code)` — POSTs to `https://oauth2.googleapis.com/token`
- `get_user_info(access_token)` — GET `https://www.googleapis.com/oauth2/v3/userinfo` → `{sub, email, name, given_name, family_name, picture}`

### `src/services/product.py`
- `create_category`, `update_category` — thin wrappers around repo
- `create_product` — validates category exists, creates product
- `update_product` — validates product exists, applies partial update
- `deactivate_product` — sets `in_stock=False`

### `src/services/user.py`
- `create_user` — validates email unique, hashes password, creates user
- `update_user` — validates user exists, applies `model_dump(exclude_none=True)`

---

## 6. UTILS

### `src/utils/phone.py`
```
normalize_phone(phone) → "+380XXXXXXXXX"
```
Accepts `0XXXXXXXXX`, `380XXXXXXXXX`, `+380XXXXXXXXX`. Strips spaces/dashes. Raises `ValueError` on invalid format.

```
validate_phone(phone) → bool
```
Wraps `normalize_phone`, returns bool.

### `src/utils/pagination.py`
- `PaginationParams` — FastAPI dependency: `skip` (ge=0), `limit` (ge=1, le=100)
- `PaginatedResponse[T]` — generic Pydantic model: `items`, `total`, `skip`, `limit`

### `src/models/base.py` — `TimestampMixin`
Adds `createdAt` / `updatedAt` (`DateTime(timezone=True)`) to any model. Default is `datetime.now(tz=timezone.utc)`; `updatedAt` uses `onupdate=_utcnow`.

---

## 7. CONFIG VARIABLES

File: `src/config.py`. Loads from `.env.dev` via `pydantic-settings`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENV` | `"dev"` | Controls dev mode (e.g. `dev_code` in OTP response) |
| `ORDER_DB_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/order_db` | Async PostgreSQL DSN |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `JWT_SECRET` | `"change_me_in_production"` | HMAC key for JWT |
| `JWT_ALGORITHM` | `"HS256"` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `TURBOSMS_API_KEY` | `""` | TurboSMS Bearer API key |
| `TURBOSMS_SENDER` | `"xprnt"` | SMS sender name |
| `GOOGLE_CLIENT_ID` | `""` | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | `""` | Google OAuth2 client secret |
| `GOOGLE_REDIRECT_URI` | `"http://localhost:8000/api/v1/auth/google/callback"` | OAuth2 redirect URI |
| `OTP_CODE_LENGTH` | `6` | OTP digit count |
| `OTP_EXPIRE_MINUTES` | `5` | OTP Redis TTL |
| `OTP_MAX_ATTEMPTS` | `3` | Max wrong OTP attempts before invalidation |
| `OTP_RESEND_COOLDOWN_SECONDS` | `60` | Min seconds between OTP sends |

---

## 8. SEEDS

File: `src/seeds.py`. Run automatically on startup in lifespan.

### `seed_reference_data()`
Idempotent (skips if already exists):

| Function | Data seeded |
|----------|------------|
| `_seed_roles` | `admin`, `manager`, `prepress`, `postpress`, `client` |
| `_seed_teams` | `Препрес`, `Постпрес`, `Менеджери` |
| `_seed_company_types` | ФО, ФОП, ТОВ, АТ |
| `_seed_measurement_units` | шт (EA), м² (MTK), м.п. (MTR), компл (SET) |
| `_seed_delivery_types` | Нова Пошта, Самовивіз, Кур'єр |

### `seed_admin_user()`
Creates admin user only if no user with role `admin` exists:
- Company: EDRPOU `00000000`, name `xprnt`
- User: `admin@xprnt.com` / `Admin123!`, role `admin`

---

## 9. MIGRATIONS

Alembic, async SQLAlchemy. Config in `alembic/env.py`. All migrations are linear (no branches).

| Revision | Down-rev | Description |
|----------|----------|-------------|
| `c684d3bf05cb` | — (initial) | Full initial schema: all tables, enums, foreign keys |
| `8cc7dccf0ddd` | `c684d3bf05cb` | Fix DateTime fields to timezone-aware; add `payments.orderId` FK; add `orders.currency`; fix circular FK constraints |
| `f12346e4fe8d` | `8cc7dccf0ddd` | Add `users.phoneVerified` (bool, default false), `users.googleId` (String 128, unique), `users.authProvider` (String 32, default 'email') |
| `a88b21717708` | `f12346e4fe8d` | Add `cart_item_products.shortName` (Text, nullable) |

---

## 10. DEPENDENCIES (requirements.txt)

```
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0
email-validator>=2.1.0
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.0
redis==5.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart>=0.0.9
httpx==0.28.1
authlib==1.3.1
itsdangerous==2.2.0
pytest==8.3.4
pytest-asyncio==0.24.0
```

Key choices:
- **FastAPI 0.115.6** + **uvicorn** — async HTTP framework
- **SQLAlchemy 2.0** + **asyncpg** — async ORM with PostgreSQL
- **Alembic 1.14** — schema migrations
- **redis 5.2.1** — async Redis client (`redis.asyncio`)
- **python-jose** — JWT encode/decode (HS256)
- **passlib + bcrypt** — password hashing
- **httpx** — async HTTP for TurboSMS + Google OAuth calls
- **authlib** / **itsdangerous** — listed but not used at runtime (Redis handles OAuth state; raw httpx handles Google token exchange)
- **pytest + pytest-asyncio** — test infrastructure (no test files currently present)
