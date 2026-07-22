set dotenv-load

backend := "backend"
frontend := "frontend"

# List available recipes
default:
    @just --list

# ── Dev ───────────────────────────────────────────────────────────────────────

# Start the API server
api:
    cd {{backend}} && uv run uvicorn src.main:app --port 9999 --reload

# Start the frontend dev server
ui:
    cd {{frontend}} && npm run dev

# ── Database ──────────────────────────────────────────────────────────────────

# Apply all pending migrations
migrate:
    cd {{backend}}/src && uv run alembic upgrade head

# Roll back the last migration
migrate-down:
    cd {{backend}}/src && uv run alembic downgrade -1

# Show migration history
migrate-history:
    cd {{backend}}/src && uv run alembic history --verbose

# Generate a new migration (usage: just migrate-new "description")
migrate-new msg:
    cd {{backend}}/src && uv run alembic revision --autogenerate -m "{{msg}}"

# ── Ingestion ─────────────────────────────────────────────────────────────────

# Ingest a fund factsheet PDF (usage: just ingest path/to/fund.pdf)
ingest pdf:
    cd {{backend}} && uv run python -m src.ingestion.pipeline {{pdf}}

# Seed the database with sample data
seed:
    cd {{backend}} && uv run python -m src.scripts.seed_data

# ── Install ───────────────────────────────────────────────────────────────────

# Install all dependencies
install:
    cd {{backend}} && uv sync
    cd {{frontend}} && npm install
