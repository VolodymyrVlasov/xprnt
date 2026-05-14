# OrderService — Technical Summary

## Stack

| Package | Version |
|---|---|
| fastapi | 0.115.6 |
| uvicorn[standard] | 0.32.1 |
| pydantic | 2.10.3 |
| pydantic-settings | 2.7.0 |
| email-validator | >=2.1.0 |
| sqlalchemy | 2.0.36 |
| asyncpg | 0.30.0 |
| alembic | 1.14.0 |
| redis | 5.2.1 |
| python-jose[cryptography] | 3.3.0 |
| passlib[bcrypt] | 1.7.4 |
| bcrypt | 4.0.1 |
| python-multipart | >=0.0.9 |
| httpx | 0.28.1 |
| pytest | 8.3.4 |
| pytest-asyncio | 0.24.0 |

**Runtime:** Python 3.x, PostgreSQL (asyncpg driver), Redis (declared in config, not used at runtime yet).  
**Entry point:** `src/main.py`, FastAPI app at `/api/v1`, async lifespan, `UnicodeJSONResponse` as default response class.

---

## Database Models

All models use `TimestampMixin` (`createdAt`, `updatedAt`, UTC, `DateTime(timezone=True)`).  
Primary keys are UUID unless noted.

### reference.py

**`roles`**
- `id` UUID PK, `role` String UNIQUE

**`teams`**
- `id` UUID PK, `name` String, `description` Text optional

**`company_types`**
- `id` UUID PK, `name` String, `short_name` String optional

**`measurement_units`**
- `id` UUID PK, `measurement_unit` String, `classifier` String optional

**`delivery_types`**
- `id` UUID PK, `name` String, `description` Text optional, `data` JSON optional

**`addresses`**
- `id` UUID PK, `country`, `district`, `city`, `street`, `building`, `apartment`, `warehouse` — all String optional

**`images`**
- `id` UUID PK, `file_path` String, `description` Text optional

**`document_templates`**
- `id` UUID PK, `document` Text

**`sellers`**
- `id` UUID PK, `company_type_id` FK→company_types, `name` String, `short_name` String optional

**`sizes`**
- `id` UUID PK, `unit_id` FK→measurement_units
- Dimensions: `width`, `height`, `diameter`, `radius`, `volume` (Numeric 10,3), `roll_width`
- Apparel: `t_shirt_size_eu`, `t_shirt_size_age` String

**`bank_requisites`**
- `id` UUID PK, `seller_id` FK→sellers, `name`, `is_default` Bool
- Bank fields: `bank_name`, `bank_mfo`, `iban`, `swift_code`, `currency`, `account_name`, `edrpou`, `tax_status`
- `bank_address_id` FK→addresses, `legal_address_id` FK→addresses
- `finish_at` String optional (soft-expiry marker)
- `update_author_id` FK→users (`use_alter`)

**`payment_types`**
- `id` UUID PK, `name` String, `description` Text optional, `data` JSON optional
- `bank_requisite_id` FK→bank_requisites, `transaction_fee` Numeric(5,4)

---

### user.py

**`contracts`**
- `id` UUID PK, `document_template_id` FK→document_templates, `document_path` String

**`users`**
- `id` UUID PK
- `company_id` FK→companies (NOT NULL), `role_id` FK→roles (NOT NULL)
- `team_id` FK→teams optional, `nova_post_user_id` UUID optional (no FK — external)
- `comment_id` FK→comments (`use_alter`), `contract_id` FK→contracts optional
- Contact: `name`, `middlename`, `lastname`, `phone1`, `phone2`, `email` UNIQUE, `telegram`
- `hashed_password` Text optional (nullable for social auth / placeholder users)
- Relationships: `role` (selectin), `company` (selectin, back_populates)

---

### company.py

**`companies`**
- `id` UUID PK
- `edrpou_code` String UNIQUE NOT NULL, `itn_code` String UNIQUE optional, `name` String UNIQUE
- Contact: `address1`, `address2`, `email`, `phone1`, `phone2`
- `company_type_id` FK→company_types, `contract_id` FK→contracts
- `contact_user_id` FK→users (`use_alter`), `head_of_id` FK→users (`use_alter`)
- Relationship: `users` → list[Users] (selectin, back_populates)

---

### product.py

**`categories`**
- `id` UUID PK, `name` String, `description` Text, `classifier` String
- `image_id` FK→images, `team_id` FK→teams
- `upsells_category_id` FK→categories (self), `crossells_category_id` FK→categories (self)
- Relationship: `products` → list[Products] (selectin, back_populates)

**`price_multipliers`**
- `id` UUID PK, `values` JSON optional (tier structure — schema not enforced at DB level)

**`prices`**
- `id` UUID PK, `product_id` FK→products
- `prime_cost_eur` Numeric(10,4), `fx_rate_used` Numeric(10,6)
- `price_multiplier_id` FK→price_multipliers optional
- `values` JSON optional (computed tier prices)
- `previous_price_id` FK→prices (self), `next_price_id` FK→prices (self)
- `start_at` String, `finish_at` String — active price has `finish_at IS NULL`

**`products`**
- `id` UUID PK, `name`, `short_name`, `description`
- `category_id` FK→categories (NOT NULL), `measurement_unit_id` FK→measurement_units (NOT NULL)
- `image_id` FK→images, `size_id` FK→sizes, `package_size_id` FK→sizes
- `is_deliverable` Bool default True, `in_stock` Bool default True
- `active_price_id` FK→prices optional (deferred FK to break cycle with prices)
- Relationships: `category` (back_populates), `active_price` (selectin)

**`gallery`**
- `id` UUID PK, `product_id` FK→products, `category_id` FK→categories optional, `file_path` String

---

### cart.py

**`cart`** — Statuses: `active` → `locked` → `ordered` / `abandoned`
- `id` UUID PK, `status` Enum(CartStatus), `total_price` Numeric(10,2), `currency` String(3)
- `customer_id` FK→users optional (anonymous cart supported)
- Relationship: `items` → list[CartItems] (selectin, cascade delete-orphan)

**`cart_items`** — Types: `configured` (multi-product bundle), `simple`
- `id` UUID PK, `cart_id` FK→cart, `category_id` FK→categories
- `cart_item_type` Enum, `name`, `short_name`, `amount` Numeric(10,3)
- `unit_price` Numeric(10,2), `total_price` Numeric(10,2), `priced_at` String
- `design_id` UUID optional (cross-service ref to design-service, no FK)
- Relationships: `cart` (back_populates), `products` → list[CartItemProducts] (selectin, cascade)

**`cart_item_products`** — Line items within a cart item
- `id` UUID PK, `cart_item_id` FK→cart_items, `product_id` FK→products
- `price_id` FK→prices optional, `price_tier_qty` Int optional, `priced_at` String
- `name`, `amount` Numeric(10,3), `price` Numeric(10,2), `price_total` Numeric(10,2)

---

### order.py

**`order_numbers`** — Sequential autoincrement counter (BigInt, not UUID)
- `id` BigInt PK autoincrement, `created_at` String, `created_by` FK→users

**`comments`**
- `id` UUID PK, `entity_type` Enum(`order`), `entity_id` UUID (generic ref, no FK)
- `text` Text, `created_by` FK→users

**`super_orders`** — Billing container for multiple orders
- `id` UUID PK, `order_number_id` FK→order_numbers UNIQUE
- `company_id` FK→companies, `contact_user_id` FK→users optional
- `payment_type_id` FK→payment_types, `currency` String(3)
- `billing_period_start`, `billing_period_end`, `invoice_number`, `invoice_date` String optional
- `status` Enum(`open`, `invoiced`, `paid`, `closed`, `cancelled`), `total` Numeric(12,2)

**`order_paths`**
- `id` UUID PK, `order_id` FK→orders, `path` String, `docs_path` String

**`orders`**
- `id` UUID PK, `order_number_id` FK→order_numbers UNIQUE, `cart_id` FK→cart UNIQUE
- `super_order_id` FK→super_orders optional
- `seller_id` FK→sellers, `company_id` FK→companies
- `customer_id`, `payment_user_id`, `delivery_user_id`, `manager_id` FK→users
- `payment_id` FK→payments optional, `delivery_id` FK→deliveries optional
- `total_price` Numeric(10,2), `currency` String(3)
- `status` Enum(OrderStatus) default `pending`
- `order_path_id` FK→order_paths (`use_alter`), `finish_at`, `done_at` String optional
- Relationship: `cart` (selectin)

---

### payment.py

**`payments`** — Statuses: `pending`, `paid`, `failed`, `refunded`
- `id` UUID PK, `payment_type_id` FK→payment_types, `super_order_id` FK→super_orders optional
- `amount` Numeric(10,2), `currency` String(3), `fiscal_receipt_number` String optional
- `status` Enum(PaymentStatus) default `pending`

---

### delivery.py

**`deliveries`**
- `id` UUID PK, `delivery_user_id` FK→users, `delivery_type_id` FK→delivery_types
- `address_id` FK→addresses, `ttn_number` String(32) optional (Nova Poshta TTN)

---

## API Endpoints

All routes are under `/api/v1`. Auth = Bearer JWT required. Roles listed where `require_role()` is used.

### Auth — `/api/v1/auth`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/auth/register` | Register new user + company | No | — |
| POST | `/auth/login` | Login, returns access token + refresh cookie | No | — |
| POST | `/auth/refresh` | Refresh access token using httpOnly cookie | No (cookie) | — |
| POST | `/auth/logout` | Delete refresh cookie | No | — |

### Users — `/api/v1/users`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/users/me` | Get own profile | Yes | any |
| GET | `/users/` | List all users | Yes | manager, admin |
| GET | `/users/{user_id}` | Get user (own or any if staff) | Yes | self or manager/admin |
| PUT | `/users/{user_id}` | Update user (own or any if staff) | Yes | self or manager/admin |

### Companies — `/api/v1/companies`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/companies/` | List companies | Yes | any |
| POST | `/companies/` | Create company | Yes | any |
| GET | `/companies/{company_id}` | Get company | Yes | any |
| PUT | `/companies/{company_id}` | Update company | Yes | any |

### Categories — `/api/v1/categories`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/categories/` | List categories | No | — |
| POST | `/categories/` | Create category | Yes | manager, admin |
| GET | `/categories/{category_id}` | Get category with products | No | — |
| PUT | `/categories/{category_id}` | Update category | Yes | manager, admin |

### Products — `/api/v1/products`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/products/` | List products (filter: category_id, in_stock) | No | — |
| POST | `/products/` | Create product | Yes | manager, admin |
| GET | `/products/{product_id}` | Get product | No | — |
| PUT | `/products/{product_id}` | Update product | Yes | manager, admin |
| DELETE | `/products/{product_id}` | Deactivate product (sets in_stock=False) | Yes | manager, admin |

### Prices — `/api/v1/prices`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/prices/` | Create price (closes previous active price) | Yes | manager, admin |
| GET | `/prices/product/{product_id}` | Get price history for product | No | — |
| GET | `/prices/product/{product_id}/active` | Get current active price | No | — |
| GET | `/prices/{id}` | Get price by id | No | — |

### Price Multipliers — `/api/v1/price-multipliers`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/price-multipliers/` | List all multipliers | No | — |
| POST | `/price-multipliers/` | Create multiplier | Yes | admin |
| GET | `/price-multipliers/{id}` | Get multiplier | No | — |
| PUT | `/price-multipliers/{id}` | Update multiplier | Yes | admin |

### Cart — `/api/v1/cart`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/cart/` | Create cart (links to current user if authenticated) | Yes | any |
| GET | `/cart/{cart_id}` | Get cart with items | No | — |
| POST | `/cart/{cart_id}/items` | Add item to cart | No | — |
| PUT | `/cart/{cart_id}/items/{item_id}` | Update cart item | No | — |
| DELETE | `/cart/{cart_id}/items/{item_id}` | Remove cart item | No | — |
| POST | `/cart/{cart_id}/lock` | Lock cart (prerequisite for order creation) | No | — |

### Orders — `/api/v1/orders`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/orders/` | Create order from locked cart | Yes | any |
| GET | `/orders/my` | List own orders | Yes | any |
| GET | `/orders/` | List orders (all for staff, company-scoped for clients) | Yes | any |
| GET | `/orders/{order_id}` | Get order details (access-checked) | Yes | any |
| PUT | `/orders/{order_id}/status` | Change order status (role-gated transitions) | Yes | manager, admin, prepress, postpress |
| POST | `/orders/{order_id}/delivery` | Attach delivery to order | Yes | manager, admin |
| POST | `/orders/{order_id}/payment` | Attach payment to order (auto-advances to paid) | Yes | manager, admin |
| GET | `/orders/{order_id}/comments` | Get comments for an order | Yes | any |

### Deliveries — `/api/v1/deliveries`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/deliveries/` | Create delivery record | Yes | any |
| GET | `/deliveries/` | List deliveries (filter: has_ttn) | Yes | manager, admin |
| GET | `/deliveries/{id}` | Get delivery | Yes | any |
| PUT | `/deliveries/{id}` | Update TTN number | Yes | manager, admin |

### Payments — `/api/v1/payments`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/payments/` | Register payment | Yes | manager, admin |
| GET | `/payments/` | List payments (filter: order_id, super_order_id) | Yes | manager, admin |
| GET | `/payments/{id}` | Get payment | Yes | manager, admin |
| PUT | `/payments/{id}/status` | Update payment status | Yes | manager, admin |

### Comments — `/api/v1/comments`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | `/comments/` | Add comment | Yes | any |
| GET | `/comments/` | List comments by entity_type + entity_id | Yes | any |
| DELETE | `/comments/{id}` | Delete comment (own or manager/admin) | Yes | own or manager/admin |

### References — `/api/v1/references`

| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | `/references/roles` | List roles | No | — |
| POST | `/references/roles` | Create role | Yes | admin |
| GET | `/references/delivery-types` | List delivery types | No | — |
| POST | `/references/delivery-types` | Create delivery type | Yes | manager, admin |
| GET | `/references/delivery-types/{id}` | Get delivery type | No | — |
| PUT | `/references/delivery-types/{id}` | Update delivery type | Yes | manager, admin |
| GET | `/references/payment-types` | List payment types | No | — |
| POST | `/references/payment-types` | Create payment type | Yes | manager, admin |
| GET | `/references/payment-types/{id}` | Get payment type | No | — |
| PUT | `/references/payment-types/{id}` | Update payment type | Yes | manager, admin |
| GET | `/references/sellers` | List sellers | No | — |
| POST | `/references/sellers` | Create seller | Yes | admin |
| GET | `/references/sellers/{id}` | Get seller | No | — |
| PUT | `/references/sellers/{id}` | Update seller | Yes | admin |
| GET | `/references/measurement-units` | List measurement units | No | — |
| POST | `/references/measurement-units` | Create measurement unit | Yes | manager, admin |
| GET | `/references/sizes` | List sizes (filter: unit_id) | No | — |
| POST | `/references/sizes` | Create size | Yes | manager, admin |
| GET | `/references/sizes/{id}` | Get size | No | — |
| PUT | `/references/sizes/{id}` | Update size | Yes | manager, admin |
| GET | `/references/teams` | List teams | No | — |
| POST | `/references/teams` | Create team | Yes | admin |
| PUT | `/references/teams/{id}` | Update team | Yes | admin |

### Health

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/health` | Liveness check | No |

---

## Business Logic

### JWT

- **Algorithm:** HS256, secret from `JWT_SECRET` env var
- **Access token:** expires in `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min), claim `"type": "access"`
- **Refresh token:** expires in `JWT_REFRESH_TOKEN_EXPIRE_DAYS` (default 30 days), claim `"type": "refresh"`, stored as httpOnly cookie `refresh_token` (SameSite=lax)
- **Payload:** `{"sub": str(user.id), "role": role_name, "exp": ..., "type": ...}`
- **Refresh flow:** `POST /auth/refresh` reads cookie → verifies token type → re-fetches user from DB (role may have changed) → issues new access + refresh tokens
- **`get_current_user` dependency:** decodes access token → fetches full `Users` row from DB on every request (role loaded via `selectin`)

### Order Status Machine

All transitions defined in `src/services/order.py:_STATUS_TRANSITIONS`.

**`OrderStatus` values:** `pending`, `paid`, `execution`, `printing`, `printed`, `postprint`, `done`, `waiting_delivery`, `shipped`, `successful`, `canceled`, `returned`

| From | To | Roles |
|---|---|---|
| pending | paid, canceled | manager, admin |
| paid | execution, canceled | manager, admin |
| execution | printing, canceled | manager, admin |
| printing | printed, canceled | manager, admin |
| printed | postprint, canceled | manager, admin |
| postprint | done, waiting_delivery, canceled | manager, admin |
| done | successful, waiting_delivery | manager, admin |
| waiting_delivery | shipped, canceled | manager, admin |
| shipped | successful, returned | manager, admin |
| successful | *(terminal)* | — |
| canceled | *(terminal)* | — |
| returned | *(terminal)* | — |
| execution | printing | prepress |
| printing | printed | prepress |
| printed | postprint | postpress |
| postprint | done, waiting_delivery | postpress |
| *any* | *any* | admin (no restrictions) |

**Special case:** `POST /orders/{id}/payment` — if a `paid` payment is attached to a `pending` order, status auto-advances to `paid` in the same request without going through the status transition table.

**`SuperOrderStatus`** (`super_orders` table): `open`, `invoiced`, `paid`, `closed`, `cancelled` — no transition logic implemented yet, only stored.

### Price Chain

Each `Prices` row is a node in a **doubly-linked list** per product:

- **Active price:** `finish_at IS NULL` — identified by `price_repo.get_active_for_product()`
- **Creating a new price:**
  1. Find current active price (`old_price`)
  2. Create new price with `previous_price_id = old_price.id`
  3. Close old price: set `finish_at = now()` and `next_price_id = new_price.id`
  4. Update `products.active_price_id = new_price.id`
- **`values`** field (JSON): stores computed tier prices (structure is application-defined, not enforced by DB)
- **`prime_cost_eur` + `fx_rate_used`**: raw cost inputs for price calculation — calculation itself is not in the codebase, result is stored in `values`
- **History query:** `GET /prices/product/{id}` returns all prices ordered by `start_at`

### Seeding

Runs at every startup (idempotent — skips existing records):

**`seed_reference_data()`:**
- **Roles:** `admin`, `manager`, `prepress`, `postpress`, `client`
- **Teams:** `Препрес`, `Постпрес`, `Менеджери`
- **Company types:** `Фізична особа (ФО)`, `ФОП`, `Товариство з обмеженою відповідальністю (ТОВ)`, `Акціонерне товариство (АТ)`
- **Measurement units:** `шт (EA)`, `м² (MTK)`, `м.п. (MTR)`, `компл (SET)`
- **Delivery types:** `Нова Пошта`, `Самовивіз`, `Кур'єр`

**`seed_admin_user()`:**
- Creates company `xprnt` with `edrpou_code = "00000000"` if not exists
- Creates user `admin@xprnt.com` / `Admin123!` with `admin` role
- Skips if any admin-role user already exists

---

## Known Issues or TODOs

1. **`Companies` endpoint has no role guard** — `POST /companies/`, `PUT /companies/{id}` require only `get_current_user` (any authenticated user). Any `client` can create or modify companies.

2. **Cart endpoints are mostly unauthenticated** — `GET /cart/{id}`, `POST /cart/{id}/items`, `PUT`, `DELETE`, `POST /cart/{id}/lock` have no auth at all. Anyone with a cart UUID can modify it.

3. **`BaseRepository.update()` skips `None` values** — `if value is not None: setattr(...)` makes it impossible to explicitly set a field to `None` via update. This is a silent limitation.

4. **`order_numbers.created_at` is `String` not `DateTime`** — inconsistent with the rest of the schema which uses `DateTime(timezone=True)` via `TimestampMixin`. The field is not in `TimestampMixin` (no `createdAt`/`updatedAt`) but has its own `created_at: String`.

5. **`Users.nova_post_user_id`** — stored as UUID with no FK constraint and no integration code. Placeholder for future Nova Poshta API integration.

6. **Redis is declared in config but never used** — `REDIS_URL` exists in settings, but `redis` package is imported nowhere in the service layer. No caching, no queues implemented.

7. **`SuperOrders` has no CRUD routes** — the model and migration exist but there is no router for creating, reading, or managing super-orders.

8. **`OrderPaths` has no CRUD routes** — model and migration exist, `order_path_id` is on `Orders`, but no endpoints to create or manage order paths (file paths for order documents).

9. **`Gallery` has no CRUD routes** — model exists, no endpoints.

10. **`BankRequisites` has no CRUD routes** — model exists, referenced by `PaymentTypes`, but no endpoints.

11. **`Contracts` and `DocumentTemplates` have no CRUD routes** — models exist, referenced by `Users` and `Companies`, but no endpoints.

12. **`Sizes` DELETE endpoint missing** — only GET list, GET by id, POST, PUT are implemented.

13. **`Teams` GET by id endpoint missing** — only GET list, POST, PUT are implemented.

14. **`delivery_type_repo` has no `get_with_ttn` method** — `delivery_repo.get_with_ttn()` is implemented in the delivery repository, but the filter in `GET /deliveries/` queries for TTN on `Deliveries`, not `DeliveryTypes`.

15. **`Comments.entity_type` only supports `"order"`** — the enum has a single value. Extending to other entities (e.g., `product`, `user`) would require a migration.

---

## What Is NOT Implemented Yet

| Feature | Status |
|---|---|
| SuperOrders API (invoicing / billing periods) | Model + migration exist, no routes |
| OrderPaths API (file path management) | Model + migration exist, no routes |
| Gallery API (product images) | Model + migration exist, no routes |
| BankRequisites API | Model + migration exist, no routes |
| Contracts + DocumentTemplates API | Models + migration exist, no routes |
| Redis usage (caching, queues, sessions) | Config only, no implementation |
| Nova Poshta integration (`nova_post_user_id`) | Field exists, no integration |
| Price calculation engine | `prime_cost_eur × fx_rate_used × multiplier` — inputs stored, formula not implemented |
| Pagination metadata in responses | `skip`/`limit` accepted, but responses return raw arrays with no total count |
| Password change / reset endpoint | No `/auth/change-password` or `/auth/forgot-password` |
| User creation endpoint (`POST /users/`) | `create_user` service exists but no route — only registration via `/auth/register` |
| Super-order status transitions | Status enum exists, no state machine |
| Design–order integration | `design_id` on `cart_items` is a plain UUID, no validation against design-service |
| Soft delete | No soft-delete pattern — `DELETE /products/` sets `in_stock=False`, all other deletes are hard |
| Tests | `tests/` directory exists with framework configured, but no actual test cases written |
