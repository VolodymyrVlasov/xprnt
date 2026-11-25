# PROJECT MAP — admin
_Last updated: 2026-05-24_

## ⚠️ Статус переходу

| Версія | Стек | Стан |
|---|---|---|
| **v1 (поточна)** | react-admin 5 + MUI 9 | Заморожена. Задеплоєна на SVR, працює. Нові фічі не розробляються. |
| **v2 (нова)** | React + Vite + shadcn/ui + Tailwind | В розробці. Фігма — в процесі. Поки не замінює v1. |

---

## Service overview

| Item | Value |
|---|---|
| Location | services/admin/ |
| Dev port | 3001 |
| Prod URL | https://admin.xprnt.top |
| API target | VITE_API_TARGET env var → http://order-service:8000 (Docker) |
| Docker (dev) | Dockerfile.dev — node:20-alpine; src/ volume-mounted для hot reload |
| Docker (prod) | Dockerfile.dev — src/ volume-mounted read-only з /opt/xprnt/repo/services/admin/ |

---

## Stack — v2 (нова адмінка)

| Шар | Пакет | Призначення |
|---|---|---|
| UI framework | React 19 + Vite | Базовий стек |
| Компоненти | shadcn/ui | Кастомні компоненти поверх Radix UI |
| Стилі | Tailwind CSS | Лейаут, утиліти, адаптивність |
| Таблиці | TanStack Table | Фільтрація, сортування, пагінація |
| Data fetching | TanStack Query | Кешування, стан запитів, інвалідація |
| Форми | React Hook Form + Zod | Валідація схем, контрольовані форми |
| Навігація | React Router | SPA routing |
| Design system (Figma) | shadcn/ui Design System by Pietro Schirano | Кіт компонентів у Figma |

### Що прибрали і чому

| Пакет | Причина |
|---|---|
| react-admin 5 | Обмежує кастомний дизайн; сильно прив'язаний до MUI; складно стилізувати під власну дизайн-систему |
| MUI (@mui/material) | Замінено на shadcn/ui + Tailwind |
| ra-data-json-server | Був невикористаним навіть у v1 |

---

## Stack — v1 (заморожена, тільки для довідки)

| Пакет | Версія |
|---|---|
| react | ^19.2.6 |
| react-admin | ^5.14.6 |
| @mui/material | ^9.0.1 |
| vite | ^8.0.12 |

---

## File index — v1 (поточна структура в репо)

| File | Responsibility |
|---|---|
| services/admin/package.json | Залежності та скрипти (v1 стек) |
| services/admin/vite.config.js | Vite dev server port 3001; proxy /api → VITE_API_TARGET; allowedHosts: admin.xprnt.top |
| services/admin/src/main.jsx | React root mount |
| services/admin/src/App.jsx | react-admin компонент з усіма Resource деклараціями |
| services/admin/src/authProvider.js | Login/logout, token storage, identity fetch, permissions |
| services/admin/src/dataProvider.js | Кастомний data provider поверх /api/v1 REST API |
| services/admin/src/resources/users/ | UserList, UserShow |
| services/admin/src/resources/companies/ | CompanyList, CompanyEdit |
| services/admin/src/resources/categories/ | CategoryList, CategoryEdit, CategoryCreate |
| services/admin/src/resources/products/ | ProductList, ProductEdit, ProductCreate |
| services/admin/src/resources/prices/ | PriceList, PriceCreate |
| services/admin/src/resources/priceMultipliers/ | MultiplierList, MultiplierEdit, MultiplierCreate |
| services/admin/src/resources/orders/ | OrderList, OrderShow |
| services/admin/src/resources/sizes/ | SizeList, SizeEdit, SizeCreate |
| services/admin/src/resources/measurementUnits/ | UnitList, UnitCreate |
| services/admin/Dockerfile.dev | node:20-alpine; WORKDIR /app; npm install; EXPOSE 3001 |

---

## Планована структура файлів — v2

```
services/admin/
├── src/
│   ├── main.jsx
│   ├── App.jsx                    ← React Router + layout
│   ├── lib/
│   │   ├── api.js                 ← базовий fetch wrapper
│   │   └── queryClient.js         ← TanStack Query клієнт
│   ├── hooks/
│   │   └── useAuth.js             ← JWT + refresh логіка
│   ├── components/
│   │   ├── ui/                    ← shadcn/ui компоненти (auto-generated)
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   └── AppLayout.jsx
│   │   └── shared/
│   │       ├── DataTable.jsx      ← обгортка TanStack Table
│   │       ├── PageHeader.jsx
│   │       └── StatusBadge.jsx
│   ├── pages/
│   │   ├── auth/
│   │   │   └── LoginPage.jsx
│   │   ├── orders/
│   │   │   ├── OrdersPage.jsx
│   │   │   └── OrderDetailPage.jsx
│   │   ├── products/
│   │   │   ├── ProductsPage.jsx
│   │   │   ├── ProductEditPage.jsx
│   │   │   └── ProductCreatePage.jsx
│   │   ├── categories/
│   │   ├── companies/
│   │   ├── users/
│   │   ├── prices/
│   │   ├── super-orders/
│   │   ├── payments/
│   │   └── deliveries/
│   └── schemas/                   ← Zod схеми для форм
│       ├── product.schema.js
│       └── order.schema.js
├── package.json
├── vite.config.js
├── tailwind.config.js
├── components.json                ← shadcn/ui конфіг
└── Dockerfile.dev
```

---

## Ресурси і сторінки (v2 — план)

| Ресурс | Сторінки | Ключові поля | API endpoint |
|---|---|---|---|
| orders | List, Detail, StatusChange | orderNumber, status, company, totalPrice, items | GET/PUT /api/v1/orders/ |
| super-orders | List, Detail, Create, Edit | orderNumber, company, status, total, invoiceNumber | GET/POST/PUT /api/v1/super-orders/ |
| products | List, Create, Edit, Deactivate | name, shortName, category, inStock, article, sku, activePrice | GET/POST/PUT /api/v1/products/ |
| categories | List, Create, Edit | name, classifier, description | GET/POST/PUT /api/v1/categories/ |
| prices | List (per product), Create | values (tiers), primeCostEUR, fxRateUsed, startAt | GET/POST /api/v1/prices/ |
| price-multipliers | List, Create, Edit | values (JSON tier multipliers) | GET/POST/PUT /api/v1/price-multipliers/ |
| companies | List, Edit | name, edrpouCode, email, phone1 | GET/PUT /api/v1/companies/ |
| users | List, Show | name, email, role, phone1, authProvider | GET /api/v1/users/ |
| payments | List, Create, StatusChange | amount, status, paymentType, orderId | GET/POST/PUT /api/v1/payments/ |
| deliveries | List, Create, Edit | ttnNumber, deliveryType, address | GET/POST/PUT /api/v1/deliveries/ |
| sizes | List, Create, Edit | width, height, diameter, radius | GET/POST/PUT /api/v1/references/sizes |
| measurement-units | List, Create | measurementUnit, classifier | GET/POST /api/v1/references/measurement-units |
| references | — | delivery-types, payment-types, sellers, teams, roles | /api/v1/references/* |

---

## Auth flow (v1 і v2 однакові)

- Login: POST /api/v1/auth/login → {email, password}
- Token storage: localStorage — `token` (JWT access), `role` (string)
- JWT decode: client-side `atob(token.split('.')[1])` для отримання role
- Logout: POST /api/v1/auth/logout + localStorage.clear()
- Identity: GET /api/v1/users/me → {id, name, role}
- **Проблема v1 і v2:** немає auto-refresh — після 30хв access token протухає, потрібен re-login

---

## Data fetching — v2 (план)

TanStack Query з централізованим queryClient:

```js
// Приклад: список замовлень
useQuery({
  queryKey: ['orders', filters],
  queryFn: () => api.get('/api/v1/orders/', { params: filters }),
})

// Приклад: зміна статусу
useMutation({
  mutationFn: (data) => api.put(`/api/v1/orders/${id}/status`, data),
  onSuccess: () => queryClient.invalidateQueries(['orders']),
})
```

---

## Config / Env vars

| Var | Default | Призначення |
|---|---|---|
| VITE_API_TARGET | http://localhost:8000 | Proxy target для /api запитів |

---

## Figma Design System

| Item | Value |
|---|---|
| Кіт | shadcn/ui Design System by Pietro Schirano |
| Статус | В процесі — дизайн починається, не фінальний |
| Інструмент | Figma (новий для команди) |
| Принцип | Компоненти з Figma-кіту відповідають shadcn/ui компонентам у коді 1-до-1 |

---

## Known issues and TODOs

| Location | Note |
|---|---|
| v1 src/authProvider.js | No token refresh — після 30хв access token expired, потрібен re-login |
| v1 src/authProvider.js | JWT role decoded client-side через atob() — без верифікації підпису |
| v1 src/dataProvider.js | getList повертає list.length як total — пагінація некоректна |
| v1 src/resources/products/ | Показує categoryId UUID замість назви категорії |
| v1 src/resources/orders/ | Показує companyId UUID замість назви компанії |
| v1 + v2 | Auth token auto-refresh не реалізовано |
| docker-compose.prod.yml | Admin використовує Dockerfile.dev з Vite dev server — потрібен prod Dockerfile з vite build + nginx |
| v2 | Figma дизайн незавершений — розробка не почалась |

---

## What is NOT implemented

| Функція | Статус |
|---|---|
| Super orders management | v1: немає. v2: заплановано |
| Payments management | v1: немає. v2: заплановано |
| Deliveries management | v1: немає. v2: заплановано |
| References management (delivery types, payment types, sellers, teams, roles) | v1: немає. v2: заплановано |
| Order status change UI | v1: OrderShow read-only. v2: заплановано |
| User creation by admin | v1: немає. v2: заплановано |
| Role assignment UI | v1: read-only text. v2: заплановано |
| Token auto-refresh | Не реалізовано ні в v1, ні в v2 |
| Design management | Немає інтеграції з design-service |
| Admin prod Dockerfile | Vite dev server у prod — потрібен build + nginx Dockerfile |
| Order number display format (W-/O- prefix) | source поле є в БД; форматування не реалізовано |
