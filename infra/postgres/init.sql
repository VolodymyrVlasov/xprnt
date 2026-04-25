-- xprnt PostgreSQL initialization
-- This script runs on first startup for postgres-order.
-- postgres-design uses its own container with POSTGRES_DB=design_db.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
