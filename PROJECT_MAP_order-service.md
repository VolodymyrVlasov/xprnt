# PROJECT MAP — order-service
_Last updated: 2026-05-14_

## Service overview
| Item | Value |
|---|---|
| Location | services/order-service/ |
| Runtime | Python 3.x / FastAPI 0.115.6 |
| Database | PostgreSQL — order_db |
| Cache | Redis 7 (OTP storage; oauth state; general cache not yet used) |
| API prefix | /api/v1 |
| Dev port | 8000 |
| Health | GET /health → {"status": "ok", "service": "order-service"} |
| Docs | /docs, /redoc |

## File index
| File | Responsibility |
|---|---|
| services/order-service/src/config.py | Pydantic settings — all env vars with defaults |
| services/order-service/src/main.py | FastAPI app factory, lifespan (Redis/services init, seeding), CORS, router registration |
| services/order-service/src/database.py | Async SQLAlchemy engine + session factory + DeclarativeBase |
| services/order-service/src/dependencies.py | get_db, get_current_user, get_current_user_optional, require_role factory, app-state accessors |
| services/order-service/src/seeds.py | On-startup seed: roles, teams, company types, measurement units, delivery types, admin user |
| services/order-service/src/models/base.py | TimestampMixin — createdAt / updatedAt mapped columns |
| services/order-service/src/models/user.py | Contracts, Users models |
| services/order-service/src/models/company.py | Companies model |
| services/order-service/src/models/product.py | Categories, PriceMultipliers, Prices, Products, Gallery models + product_article_seq |
| services/order-service/src/models/cart.py | Cart, CartItems, CartItemProducts models + CartStatus / CartItemType enums |
| services/order-service/src/models/order.py | OrderNumbers, Comments, SuperOrders, OrderPaths, Orders models + OrderSource / status enums |
| services/order-service/src/models/payment.py | Payments model + PaymentStatus enum |
| services/order-service/src/models/delivery.py | Deliveries model |
| services/order-service/src/models/reference.py | Roles, Teams, CompanyTypes, MeasurementUnits, DeliveryTypes, Addresses, Images, DocumentTemplates, Sellers, Sizes, BankRequisites, PaymentTypes |
| services/order-service/src/repository/base.py | Generic BaseRepository[T] — get, get_all, count, create, update, delete |
| services/order-service/src/repository/user.py | UserRepository — get_by_email, get_by_company, get_by_phone, get_by_google_id |
| services/order-service/src/repository/company.py | CompanyRepository — get_by_edrpou, get_by_name |
| services/order-service/src/repository/product.py | CategoryRepository (get_with_products), ProductRepository (get_by_category, get_filtered) |
| services/order-service/src/repository/cart.py | CartRepository (get_with_items, get_active_for_user), CartItemRepository, CartItemProductRepository |
| services/order-service/src/repository/order.py | OrderNumberRepository (create_number), OrderRepository (get_with_details, get_by_customer, get_by_company, get_by_status, get_by_cart) |
| services/order-service/src/repository/price.py | PriceMultiplierRepository, PriceRepository (get_by_product, get_active_for_product) |
| services/order-service/src/repository/payment.py | PaymentRepository (get_by_super_order, get_by_order_id) |
| services/order-service/src/repository/reference.py | RoleRepository, TeamRepository, DeliveryTypeRepository, PaymentTypeRepository, SellerRepository, MeasurementUnitRepository, SizeRepository |
| services/order-service/src/repository/comment.py | CommentRepository — get_by_entity |
| services/order-service/src/repository/delivery.py | DeliveryRepository — get_with_ttn |
| services/order-service/src/repository/order_path.py | OrderPathRepository — get_by_order, create_for_order (also links Orders.order_path_id) |
| services/order-service/src/repository/super_order.py | SuperOrderRepository — get_all (with filters), get_by_company, add_order, remove_order |
| services/order-service/src/routes/auth.py | Register, login, refresh, logout, SMS OTP send/verify, Google OAuth init/callback |
| services/order-service/src/routes/users.py | List users, get me, get by id, update user |
| services/order-service/src/routes/companies.py | List, create, get, update companies |
| services/order-service/src/routes/categories.py | List, create, get, update categories |
| services/order-service/src/routes/products.py | List (filtered), create, get, update, deactivate products |
| services/order-service/src/routes/cart.py | Create cart, get cart, add/update/remove items, lock cart, claim cart (anonymous→user) |
| services/order-service/src/routes/orders.py | Create order, my orders, list orders, get order, change status, attach delivery/payment, get path, get comments |
| services/order-service/src/routes/prices.py | Create price (with chain), get price history, get active price, get by id |
| services/order-service/src/routes/price_multipliers.py | List, create, get, update price multipliers |
| services/order-service/src/routes/payments.py | Register payment, list, get, update status |
| services/order-service/src/routes/deliveries.py | Create, list (with ttn filter), get, update delivery |
| services/order-service/src/routes/comments.py | Add, list, delete comments |
| services/order-service/src/routes/references.py | CRUD for roles, delivery types, payment types, sellers, measurement units, sizes, teams |
| services/order-service/src/routes/super_orders.py | Create, list, get, update super order; add/remove orders; change status (with transition guards) |
| services/order-service/src/routes/order_paths.py | Create, get by order, update order path |
| services/order-service/src/services/auth.py | hash_password, verify_password, create_access_token, create_refresh_token, verify_token |
| services/order-service/src/services/user.py | create_user, update_user |
| services/order-service/src/services/cart.py | create_cart, get_cart, add_item, update_item, remove_item, lock_cart, _recalculate_cart_total |
| services/order-service/src/services/order.py | create_order (locks cart), change_status (role-based state machine) |
| services/order-service/src/services/product.py | create_category, update_category, create_product, update_product, deactivate_product |
| services/order-service/src/services/otp.py | OTPService — generate_and_store (with cooldown), verify (with max attempts), delete |
| services/order-service/src/services/sms.py | TurboSMSService — send_otp, get_balance |
| services/order-service/src/services/google_auth.py | GoogleAuthService — get_auth_url, exchange_code, get_user_info |
| services/order-service/src/utils/pagination.py | PaginationParams, PaginatedResponse (generic; not wired to any route yet) |
| services/order-service/src/utils/phone.py | normalize_phone (→ +380XXXXXXXXX), validate_phone |
| services/order-service/alembic/versions/c684d3bf05cb_initial.py | Initial schema — all tables |
| services/order-service/alembic/versions/8cc7dccf0ddd_fix_datetime_fields_add_payments_order_.py | Fix datetime columns, add deferred FKs, add payments.orderId |
| services/order-service/alembic/versions/f12346e4fe8d_add_phone_verified_google_id_auth_provider_to_users.py | Add phoneVerified, googleId, authProvider to users |
| services/order-service/alembic/versions/a88b21717708_add_short_name_to_cart_item_products.py | Add shortName to cart_item_products |
| services/order-service/alembic/versions/2a85eeaaf683_add_article_sku_to_products_source_to_order_numbers.py | Add article (sequence), sku to products; add source enum to order_numbers |

## Models

### Contracts
Table: `contracts` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| documentTemplateId | UUID | FK → document_templates.id NOT NULL |
| documentPath | String | NOT NULL |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Users
Table: `users` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| companyId | UUID | FK → companies.id NOT NULL |
| name | String | NOT NULL |
| middlename | String | nullable |
| lastname | String | nullable |
| phone1 | String | nullable |
| phone2 | String | nullable |
| email | String | UNIQUE NOT NULL |
| telegram | String | nullable |
| roleId | UUID | FK → roles.id NOT NULL |
| teamId | UUID | FK → teams.id nullable |
| novaPostUserId | UUID | nullable (no FK — future Nova Post integration) |
| commentId | UUID | FK → comments.id use_alter nullable |
| contractId | UUID | FK → contracts.id nullable |
| hashed_password | Text | nullable |
| phoneVerified | Boolean | NOT NULL default false |
| googleId | String(128) | UNIQUE nullable |
| authProvider | String(32) | NOT NULL default "email" |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `role` (selectin → Roles), `company` (selectin → Companies, back_populates="users")

### Companies
Table: `companies` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| contactUserId | UUID | FK → users.id use_alter nullable |
| edrpouCode | String | UNIQUE NOT NULL |
| itnCode | String | UNIQUE nullable |
| name | String | UNIQUE NOT NULL |
| address1 | String | nullable |
| address2 | String | nullable |
| email | String | nullable |
| phone1 | String | nullable |
| phone2 | String | nullable |
| companyTypeId | UUID | FK → company_types.id nullable |
| contractId | UUID | FK → contracts.id nullable |
| headOfId | UUID | FK → users.id use_alter nullable |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `users` (selectin → list[Users], back_populates="company")

### Categories
Table: `categories` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| name | String | NOT NULL |
| description | Text | nullable |
| imageId | UUID | FK → images.id nullable |
| teamId | UUID | FK → teams.id nullable |
| classifier | String | nullable |
| upsellsCategoryId | UUID | FK → categories.id (self-ref) nullable |
| crossellsCategoryId | UUID | FK → categories.id (self-ref) nullable |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `products` (selectin → list[Products], back_populates="category")

### PriceMultipliers
Table: `price_multipliers` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| values | JSON | nullable — tier multiplier dict |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Prices
Table: `prices` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| productId | UUID | FK → products.id NOT NULL |
| primeCostEUR | Numeric(10,4) | nullable |
| fxRateUsed | Numeric(10,6) | nullable |
| priceMultiplierId | UUID | FK → price_multipliers.id nullable |
| values | JSON | nullable — tier pricing table |
| previousPriceId | UUID | FK → prices.id (self-ref) nullable |
| nextPriceId | UUID | FK → prices.id (self-ref) nullable |
| startAt | DateTime(tz) | NOT NULL server_default now() |
| finishAt | DateTime(tz) | nullable — NULL means currently active |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Products
Table: `products` | PK: `id` UUID
Sequence: `product_article_seq` (start=1000)
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| name | String | NOT NULL |
| shortName | String | nullable |
| description | Text | nullable |
| categoryId | UUID | FK → categories.id NOT NULL |
| imageId | UUID | FK → images.id nullable |
| sizeId | UUID | FK → sizes.id nullable |
| isDeliverable | Boolean | NOT NULL default true |
| inStock | Boolean | NOT NULL default true |
| packageSizeId | UUID | FK → sizes.id nullable |
| measurementUnitId | UUID | FK → measurement_units.id NOT NULL |
| activePriceId | UUID | FK → prices.id (deferred fk_products_active_price) nullable |
| article | Integer | UNIQUE NOT NULL default nextval('product_article_seq') — auto-assigned sequential code |
| sku | String(64) | nullable — human-readable warehouse/catalog code (e.g. STK-A4-GLOS) |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `category` (→ Categories), `active_price` (selectin → Prices)

### Gallery
Table: `gallery` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| productId | UUID | FK → products.id NOT NULL |
| categoryId | UUID | FK → categories.id nullable |
| filePath | String | NOT NULL |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Cart
Table: `cart` | PK: `id` UUID
Enum `cart_status`: `active`, `locked`, `ordered`, `abandoned`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| status | Enum(cart_status) | NOT NULL default active |
| totalPrice | Numeric(10,2) | NOT NULL default 0 |
| customerId | UUID | FK → users.id nullable (anonymous carts allowed) |
| currency | String(3) | NOT NULL default "UAH" |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `items` (selectin → list[CartItems], cascade all/delete-orphan)

### CartItems
Table: `cart_items` | PK: `id` UUID
Enum `cart_item_type`: `configured`, `simple`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| cartId | UUID | FK → cart.id NOT NULL |
| categoryId | UUID | FK → categories.id NOT NULL |
| cartItemType | Enum(cart_item_type) | NOT NULL |
| name | String | NOT NULL |
| shortName | String | nullable |
| amount | Numeric(10,3) | NOT NULL |
| unitPrice | Numeric(10,2) | NOT NULL |
| totalPrice | Numeric(10,2) | NOT NULL |
| pricedAt | DateTime(tz) | nullable |
| designId | UUID | nullable — cross-service ref to design-service, no FK constraint |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `cart` (→ Cart), `products` (selectin → list[CartItemProducts], cascade)

### CartItemProducts
Table: `cart_item_products` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| cartItemId | UUID | FK → cart_items.id NOT NULL |
| productId | UUID | FK → products.id NOT NULL |
| priceId | UUID | FK → prices.id nullable |
| priceTierQty | Integer | nullable |
| pricedAt | DateTime(tz) | nullable |
| name | String | NOT NULL |
| shortName | Text | nullable |
| amount | Numeric(10,3) | NOT NULL |
| price | Numeric(10,2) | NOT NULL |
| priceTotal | Numeric(10,2) | NOT NULL |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### OrderNumbers
Table: `order_numbers` | PK: `id` BigInteger autoincrement
Enum `order_source`: `web`, `office`
| Column | Type | Constraint |
|---|---|---|
| id | BigInteger | PK autoincrement |
| createdAt | DateTime(tz) | NOT NULL server_default now() |
| createdBy | UUID | FK → users.id nullable |
| source | Enum(order_source) | NOT NULL default 'office' — 'web'=VPS, 'office'=office server |

Display format: `W-{id:04d}` for web, `O-{id:04d}` for office. See DEPLOY.md → Нумерація замовлень.

### Comments
Table: `comments` | PK: `id` UUID
Enum `comment_entity_type`: `order`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| entityType | Enum(comment_entity_type) | NOT NULL |
| entityId | UUID | NOT NULL (polymorphic, no FK constraint) |
| text | Text | NOT NULL |
| createdBy | UUID | FK → users.id NOT NULL |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### SuperOrders
Table: `super_orders` | PK: `id` UUID
Enum `super_order_status`: `open`, `invoiced`, `paid`, `closed`, `cancelled`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| orderNumberId | BigInteger | FK → order_numbers.id UNIQUE NOT NULL |
| companyId | UUID | FK → companies.id NOT NULL |
| contactUserId | UUID | FK → users.id nullable |
| paymentTypeId | UUID | FK → payment_types.id NOT NULL |
| currency | String(3) | NOT NULL default "UAH" |
| billingPeriodStart | DateTime(tz) | nullable |
| billingPeriodEnd | DateTime(tz) | nullable |
| invoiceNumber | String | nullable |
| invoiceDate | DateTime(tz) | nullable |
| status | Enum(super_order_status) | NOT NULL default open |
| total | Numeric(12,2) | NOT NULL default 0 |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `orders` (selectin → list[Orders])

### OrderPaths
Table: `order_paths` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| orderId | UUID | FK → orders.id NOT NULL |
| path | String | nullable — filesystem path to print files |
| docsPath | String | nullable — filesystem path to documents |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Orders
Table: `orders` | PK: `id` UUID
Enum `order_status`: `pending`, `paid`, `execution`, `printing`, `printed`, `postprint`, `done`, `waiting_delivery`, `shipped`, `successful`, `canceled`, `returned`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| orderNumberId | BigInteger | FK → order_numbers.id UNIQUE NOT NULL |
| superOrderId | UUID | FK → super_orders.id nullable |
| sellerId | UUID | FK → sellers.id NOT NULL |
| customerId | UUID | FK → users.id NOT NULL |
| paymentUserId | UUID | FK → users.id NOT NULL |
| deliveryUserId | UUID | FK → users.id NOT NULL |
| companyId | UUID | FK → companies.id NOT NULL |
| managerId | UUID | FK → users.id nullable |
| paymentId | UUID | FK → payments.id nullable |
| deliveryId | UUID | FK → deliveries.id nullable |
| totalPrice | Numeric(10,2) | NOT NULL default 0 |
| status | Enum(order_status) | NOT NULL default pending |
| orderPathId | UUID | FK → order_paths.id use_alter nullable |
| cartId | UUID | FK → cart.id UNIQUE NOT NULL |
| finishAt | DateTime(tz) | nullable |
| doneAt | DateTime(tz) | nullable |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

Relationships: `cart` (selectin → Cart)

### Payments
Table: `payments` | PK: `id` UUID
Enum `payment_status`: `pending`, `paid`, `failed`, `refunded`
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| paymentTypeId | UUID | FK → payment_types.id NOT NULL |
| orderId | UUID | FK → orders.id use_alter nullable |
| superOrderId | UUID | FK → super_orders.id nullable |
| amount | Numeric(10,2) | NOT NULL |
| currency | String(3) | NOT NULL default "UAH" |
| fiscalReceiptNumber | String | nullable |
| status | Enum(payment_status) | NOT NULL default pending |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Deliveries
Table: `deliveries` | PK: `id` UUID
| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK default uuid4 |
| deliveryUserId | UUID | FK → users.id NOT NULL |
| deliveryTypeId | UUID | FK → delivery_types.id NOT NULL |
| addressId | UUID | FK → addresses.id NOT NULL |
| ttnNumber | String(32) | nullable — Nova Post TTN tracking number |
| createdAt | DateTime(tz) | NOT NULL |
| updatedAt | DateTime(tz) | NOT NULL |

### Reference tables (flat, minimal relations)
- **roles**: id UUID PK, role String UNIQUE NOT NULL
- **teams**: id UUID PK, name String NOT NULL, description Text nullable
- **company_types**: id UUID PK, name String NOT NULL, shortName String nullable
- **measurement_units**: id UUID PK, measurementUnit String NOT NULL, classifier String nullable
- **delivery_types**: id UUID PK, name String NOT NULL, description Text nullable, data JSON nullable
- **addresses**: id UUID PK, country/district/city/street/building/apartment/warehouse all String nullable
- **images**: id UUID PK, filePath String NOT NULL, description Text nullable
- **document_templates**: id UUID PK, document Text NOT NULL
- **sellers**: id UUID PK, companyTypeId UUID FK→company_types NOT NULL, name String NOT NULL, shortName String nullable
- **sizes**: id UUID PK, unitId UUID FK→measurement_units NOT NULL, width/height/diameter/radius/volume/rollWidth Numeric(10,3) nullable, tShirtSize_EU/tShirtSize_age String nullable
- **bank_requisites**: id UUID PK, sellerId FK→sellers NOT NULL, isDefault Boolean NOT NULL, bankName/bankMFO/iban/swiftCode/currency/accountName/edrpou/taxStatus String nullable, bankAddressId/legalAddressId FK→addresses nullable, finishAt DateTime(tz) nullable, updateAuthorId UUID FK→users use_alter nullable
- **payment_types**: id UUID PK, name String NOT NULL, description Text nullable, data JSON nullable, bankRequisiteId UUID FK→bank_requisites nullable, transactionFee Numeric(5,4) nullable

## Endpoints

### /api/v1/auth
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/auth/register | Register new user + company; returns access token | No | — |
| POST | /api/v1/auth/login | Email+password login; returns access token | No | — |
| POST | /api/v1/auth/refresh | Exchange refresh cookie for new access token | Cookie | — |
| POST | /api/v1/auth/logout | Clear refresh cookie | No | — |
| POST | /api/v1/auth/sms/send-code | Send OTP to phone via TurboSMS | No | — |
| POST | /api/v1/auth/sms/verify | Verify OTP; auto-registers new user if phone not found | No | — |
| GET | /api/v1/auth/google | Get Google OAuth redirect URL | No | — |
| GET | /api/v1/auth/google/callback | Handle Google OAuth callback; register or link user | No | — |

### /api/v1/users
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/users/me | Get current user | Yes | any |
| GET | /api/v1/users/ | List users | Yes | manager, admin |
| GET | /api/v1/users/{user_id} | Get user by id | Yes | own or manager/admin |
| PUT | /api/v1/users/{user_id} | Update user | Yes | own or manager/admin |

### /api/v1/companies
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/companies/ | List companies | Yes | any |
| POST | /api/v1/companies/ | Create company | Yes | manager, admin |
| GET | /api/v1/companies/{company_id} | Get company | Yes | any |
| PUT | /api/v1/companies/{company_id} | Update company | Yes | manager, admin |

### /api/v1/categories
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/categories/ | List categories | No | — |
| POST | /api/v1/categories/ | Create category | Yes | manager, admin |
| GET | /api/v1/categories/{category_id} | Get category with products | No | — |
| PUT | /api/v1/categories/{category_id} | Update category | Yes | manager, admin |

### /api/v1/products
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/products/ | List products (filter: category_id, in_stock) | No | — |
| POST | /api/v1/products/ | Create product | Yes | manager, admin |
| GET | /api/v1/products/{product_id} | Get product | No | — |
| PUT | /api/v1/products/{product_id} | Update product | Yes | manager, admin |
| DELETE | /api/v1/products/{product_id} | Deactivate product (sets inStock=false) | Yes | manager, admin |

### /api/v1/cart
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/cart/ | Create cart (anonymous or authenticated) | Optional | — |
| GET | /api/v1/cart/{cart_id} | Get cart with items | Optional | — |
| POST | /api/v1/cart/{cart_id}/items | Add item to cart | Optional | — |
| PUT | /api/v1/cart/{cart_id}/items/{item_id} | Update cart item | Optional | — |
| DELETE | /api/v1/cart/{cart_id}/items/{item_id} | Remove cart item | Optional | — |
| POST | /api/v1/cart/{cart_id}/lock | Lock cart for ordering | Yes | any |
| POST | /api/v1/cart/{cart_id}/claim | Claim anonymous cart; calls design-service /designs/claim for guest designs | Yes | any |

### /api/v1/orders
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/orders/ | Create order from locked cart | Yes | any |
| GET | /api/v1/orders/my | Get current user's orders | Yes | any |
| GET | /api/v1/orders/ | List orders (staff all; client own company) | Yes | any |
| GET | /api/v1/orders/{order_id} | Get order details | Yes | any |
| PUT | /api/v1/orders/{order_id}/status | Change order status (role-based state machine) | Yes | manager, admin, prepress, postpress |
| POST | /api/v1/orders/{order_id}/delivery | Attach delivery to order | Yes | manager, admin |
| POST | /api/v1/orders/{order_id}/payment | Attach payment to order; auto-advance to paid if payment.status==paid | Yes | manager, admin |
| GET | /api/v1/orders/{order_id}/path | Get order path (print files location) | Yes | manager, prepress, postpress, admin |
| GET | /api/v1/orders/{order_id}/comments | Get order comments | Yes | any |

### /api/v1/prices
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/prices/ | Create price (closes previous active; updates product.activePriceId) | Yes | manager, admin |
| GET | /api/v1/prices/product/{product_id} | Get price history for product | No | — |
| GET | /api/v1/prices/product/{product_id}/active | Get active price for product | No | — |
| GET | /api/v1/prices/{id} | Get price by id | No | — |

### /api/v1/price-multipliers
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/price-multipliers/ | List all price multipliers | No | — |
| POST | /api/v1/price-multipliers/ | Create price multiplier | Yes | admin |
| GET | /api/v1/price-multipliers/{id} | Get price multiplier | No | — |
| PUT | /api/v1/price-multipliers/{id} | Update price multiplier | Yes | admin |

### /api/v1/payments
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/payments/ | Register payment (auto-attaches to order if order_id given) | Yes | manager, admin |
| GET | /api/v1/payments/ | List payments (filter: order_id, super_order_id) | Yes | manager, admin |
| GET | /api/v1/payments/{id} | Get payment | Yes | manager, admin |
| PUT | /api/v1/payments/{id}/status | Update payment status | Yes | manager, admin |

### /api/v1/deliveries
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/deliveries/ | Create delivery | Yes | any |
| GET | /api/v1/deliveries/ | List deliveries (filter: has_ttn) | Yes | manager, admin |
| GET | /api/v1/deliveries/{id} | Get delivery | Yes | any |
| PUT | /api/v1/deliveries/{id} | Update delivery ttn_number | Yes | manager, admin |

### /api/v1/comments
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/comments/ | Add comment to entity | Yes | any |
| GET | /api/v1/comments/ | List comments (query: entity_type, entity_id) | Yes | any |
| DELETE | /api/v1/comments/{id} | Delete comment (own or manager/admin) | Yes | any |

### /api/v1/references
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| GET | /api/v1/references/roles | List roles | No | — |
| POST | /api/v1/references/roles | Create role | Yes | admin |
| GET | /api/v1/references/delivery-types | List delivery types | No | — |
| POST | /api/v1/references/delivery-types | Create delivery type | Yes | manager, admin |
| GET | /api/v1/references/delivery-types/{id} | Get delivery type | No | — |
| PUT | /api/v1/references/delivery-types/{id} | Update delivery type | Yes | manager, admin |
| GET | /api/v1/references/payment-types | List payment types | No | — |
| POST | /api/v1/references/payment-types | Create payment type | Yes | manager, admin |
| GET | /api/v1/references/payment-types/{id} | Get payment type | No | — |
| PUT | /api/v1/references/payment-types/{id} | Update payment type | Yes | manager, admin |
| GET | /api/v1/references/sellers | List sellers | No | — |
| POST | /api/v1/references/sellers | Create seller | Yes | admin |
| GET | /api/v1/references/sellers/{id} | Get seller | No | — |
| PUT | /api/v1/references/sellers/{id} | Update seller | Yes | admin |
| GET | /api/v1/references/measurement-units | List measurement units | No | — |
| POST | /api/v1/references/measurement-units | Create measurement unit | Yes | manager, admin |
| GET | /api/v1/references/sizes | List sizes (filter: unit_id) | No | — |
| POST | /api/v1/references/sizes | Create size | Yes | manager, admin |
| GET | /api/v1/references/sizes/{id} | Get size | No | — |
| PUT | /api/v1/references/sizes/{id} | Update size | Yes | manager, admin |
| GET | /api/v1/references/teams | List teams | No | — |
| POST | /api/v1/references/teams | Create team | Yes | admin |
| PUT | /api/v1/references/teams/{id} | Update team | Yes | admin |

### /api/v1/super-orders
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/super-orders/ | Create super order | Yes | manager, admin |
| GET | /api/v1/super-orders/ | List super orders (filter: company_id, status) | Yes | manager, admin |
| GET | /api/v1/super-orders/{super_order_id} | Get super order with nested orders | Yes | manager, admin |
| PUT | /api/v1/super-orders/{super_order_id} | Update super order fields | Yes | manager, admin |
| POST | /api/v1/super-orders/{super_order_id}/orders | Add order to super order | Yes | manager, admin |
| DELETE | /api/v1/super-orders/{super_order_id}/orders/{order_id} | Remove order from super order (only when status=open) | Yes | manager, admin |
| PUT | /api/v1/super-orders/{super_order_id}/status | Change super order status (guarded transitions) | Yes | manager, admin |

### /api/v1/order-paths
| Method | Path | Description | Auth | Roles |
|---|---|---|---|---|
| POST | /api/v1/order-paths/ | Create order path (once per order; conflicts 409) | Yes | manager, prepress, admin |
| GET | /api/v1/order-paths/order/{order_id} | Get order path by order | Yes | manager, prepress, postpress, admin |
| PUT | /api/v1/order-paths/{order_path_id} | Update order path | Yes | manager, prepress, admin |

## Services / Business logic
| File | Method | Description |
|---|---|---|
| src/services/auth.py | hash_password | bcrypt hash via passlib |
| src/services/auth.py | verify_password | bcrypt verify |
| src/services/auth.py | create_access_token | JWT HS256, type="access", exp=JWT_ACCESS_TOKEN_EXPIRE_MINUTES |
| src/services/auth.py | create_refresh_token | JWT HS256, type="refresh", exp=JWT_REFRESH_TOKEN_EXPIRE_DAYS |
| src/services/auth.py | verify_token | Decode JWT; validate type claim; raise 401 on failure |
| src/services/user.py | create_user | Validate unique email, hash password, create via user_repo |
| src/services/user.py | update_user | Patch user via user_repo |
| src/services/cart.py | create_cart | Create Cart with status=active |
| src/services/cart.py | add_item | Create CartItems + CartItemProducts; recalculate cart total |
| src/services/cart.py | update_item | Patch item; recalculate total |
| src/services/cart.py | remove_item | Delete item; recalculate total |
| src/services/cart.py | lock_cart | Set status=locked (prerequisite for ordering) |
| src/services/order.py | create_order | Validates cart is locked; allocates OrderNumber; creates Orders; marks cart ordered |
| src/services/order.py | change_status | Role-based transitions: manager (full), prepress (execution→printed), postpress (printed→done/waiting_delivery), admin (any) |
| src/services/product.py | deactivate_product | Sets inStock=false (soft delete) |
| src/services/otp.py | generate_and_store | 6-digit OTP; OTP_RESEND_COOLDOWN_SECONDS enforced; stored in Redis with TTL |
| src/services/otp.py | verify | Increments attempt counter; deletes on success; raises 429 on OTP_MAX_ATTEMPTS exceeded |
| src/services/sms.py | send_otp | POST to TurboSMS /message/send.json; returns bool (never raises) |
| src/services/google_auth.py | exchange_code | Exchange auth code for Google tokens |
| src/services/google_auth.py | get_user_info | GET Google userinfo; returns sub, email, given_name, family_name |

## Config / Env vars
| Var | Default | Purpose |
|---|---|---|
| ENV | dev | Enables SQLAlchemy echo; exposes dev_code in OTP response |
| ORDER_DB_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/order_db | Async PostgreSQL URL |
| REDIS_URL | redis://localhost:6379 | Redis connection |
| JWT_SECRET | change_me_in_production | HMAC key for JWT |
| JWT_ALGORITHM | HS256 | JWT algorithm |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Access token TTL (minutes) |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | 30 | Refresh token TTL (days) |
| TURBOSMS_API_KEY | "" | TurboSMS bearer token |
| TURBOSMS_SENDER | xprnt | SMS sender ID |
| GOOGLE_CLIENT_ID | "" | Google OAuth client id |
| GOOGLE_CLIENT_SECRET | "" | Google OAuth client secret |
| GOOGLE_REDIRECT_URI | http://localhost:8000/api/v1/auth/google/callback | OAuth redirect URI |
| OTP_CODE_LENGTH | 6 | Number of OTP digits |
| OTP_EXPIRE_MINUTES | 5 | OTP TTL in Redis |
| OTP_MAX_ATTEMPTS | 3 | Max wrong guesses before invalidation |
| OTP_RESEND_COOLDOWN_SECONDS | 60 | Cooldown before re-send |
| DESIGN_SERVICE_URL | http://design-service:8001 | Internal URL for design-service HTTP calls |

## External services
| Service | Used for | Files | Status |
|---|---|---|---|
| TurboSMS (api.turbosms.ua) | SMS OTP delivery | src/services/sms.py | Active; failure is non-fatal (logged, returns False) |
| Google OAuth (accounts.google.com) | Social login | src/services/google_auth.py, src/routes/auth.py | Active |
| design-service (internal HTTP) | Claim guest designs on cart claim | src/routes/cart.py | Active; failure is non-fatal (logged as warning) |

## Migrations
| Revision | Down revision | Tables affected | Description |
|---|---|---|---|
| c684d3bf05cb | None | addresses, company_types, delivery_types, document_templates, images, measurement_units, price_multipliers, roles, teams, contracts, sellers, sizes, categories, products, prices, bank_requisites, companies, payment_types, users, cart, comments, deliveries, order_numbers, gallery, cart_items, super_orders, cart_item_products, payments, orders, order_paths | Initial schema — all tables |
| 8cc7dccf0ddd | c684d3bf05cb | bank_requisites, cart_item_products, cart_items, companies, order_numbers, orders, payments, prices, super_orders, users | Fix VARCHAR→DateTime(tz); add deferred FKs for circular refs; add payments.orderId column |
| f12346e4fe8d | 8cc7dccf0ddd | users | Add phoneVerified Boolean, googleId String(128) UNIQUE, authProvider String(32) |
| a88b21717708 | f12346e4fe8d | cart_item_products | Add shortName Text nullable |
| 2a85eeaaf683 | a88b21717708 | products, order_numbers | Add article (sequence product_article_seq, start=1000), sku String(64) to products; add source Enum(order_source) to order_numbers |

## Requirements
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

## Known issues and TODOs
| Location | Note |
|---|---|
| src/utils/pagination.py | PaginatedResponse defined but no route uses it — all list endpoints return bare arrays with no total count |
| src/services/cart.py:45 | Uses deprecated `datetime.utcnow()` — should use `datetime.now(timezone.utc)` |
| src/services/order.py | `create_order` omits `currency` field from Orders.create dict — relies on model default |
| seeds.py | Admin password hardcoded as "Admin123!" — must be changed for production |
| src/models/user.py | novaPostUserId stored as UUID with no FK — future Nova Post integration field, no supporting code |
| authlib==1.3.1 | Listed in requirements.txt but unused — Google OAuth is implemented with raw httpx |
| src/models/order.py | order_numbers.source default is 'office' — when VPS is deployed, its .env or seed must set source='web' for orders created there |

## What is NOT implemented
| Feature | Status |
|---|---|
| Paginated responses with total count | PaginationParams/PaginatedResponse defined but not wired to any route |
| Nova Post integration | Column exists; no service or routes |
| Fiscal/invoice document generation | invoiceNumber field exists; no generation logic |
| Email notifications | No email service |
| Product image upload | images table exists; no upload endpoint in order-service |
| Payment refund/cancellation flow | Statuses exist; no refund logic |
| Token auto-refresh | No refresh cycle implemented; access tokens expire after 30 min |
| Order number display format (W-/O- prefix) | source field added to DB; formatting logic not yet implemented in routes/schemas |
