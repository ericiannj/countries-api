<h1 align="center">countries-api</h1>

<p align="center">
  A read-only REST API serving country data — name, capital, population, area, region, languages, currencies, and neighboring countries — backed by PostgreSQL.
</p>

---

## Why

This project replaces the static `assets/countries.json` bundled by the [vanilla-countries](https://github.com/ericiannj/vanilla-countries) frontend with a real backing service — a standalone portfolio piece demonstrating a Python/FastAPI/SQLAlchemy/PostgreSQL stack. It is **not** wired into that frontend (separate repo, CORS left open for testing) and stays deliberately read-only: no auth, no write endpoints, no versioning, no caching — just a clean, layered API over a seeded dataset. Full design rationale lives in the approved design spec, `docs/superpowers/specs/2026-07-01-countries-api-design.md`, in the sibling `vanilla-countries` repo this project was planned from.

## Features

- **Layered architecture** — `api/routes` (thin FastAPI routers) → `repositories` (query construction) → `models` (SQLAlchemy ORM), so each layer is testable and replaceable in isolation.
- **Fully async** — `AsyncSession`/`create_async_engine` end to end, no sync SQLAlchemy session anywhere in the request path.
- **Filtering & pagination** — list countries by `region`, `subregion`, or a case-insensitive `search` against the country's name, with `limit`/`offset` paging and a total count.
- **Single-country lookup** — fetch by ISO alpha-2 code (`cca2`), case-insensitive, 404 if not found.
- **Relational data model** — countries, languages, and currencies are proper many-to-many relations; a country's neighbors are modeled as a self-referential many-to-many (`borders`).
- **Schema as code** — Alembic migrations manage both the table schema and the data seed, so any environment can go from empty database to fully populated with one command.
- **Tested against real Postgres** — the test suite runs against an actual PostgreSQL database (not SQLite), since the schema relies on Postgres-specific features like `ARRAY` columns.

## Quick Start

```bash
docker compose up
```

This starts Postgres, runs migrations (schema + seed data for 250 countries), and serves the API at http://localhost:8000. Interactive docs: http://localhost:8000/docs.

### Local development (without Docker for the API)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

### Running tests

```bash
docker compose up -d db
pytest
```

Tests run against a separate `countries_test` database (auto-created by `docker/initdb/001_create_test_db.sql`), which is dropped and recreated before every test.

## Project Structure

```
countries-api/
├── app/
│   ├── main.py            # FastAPI() instance, CORS(*), router registration
│   ├── core/config.py     # pydantic-settings: DATABASE_URL, CORS origins, etc.
│   ├── db/                # DeclarativeBase, async engine/session, get_session dependency
│   ├── models/            # Country, Language, Currency ORM models + association tables
│   ├── schemas/           # Pydantic response models (CountryRead, PaginatedCountries)
│   ├── repositories/      # query layer: filtering, pagination, get-by-code
│   └── api/routes/        # GET /countries, GET /countries/{cca2}, GET /health
├── alembic/versions/      # 0001 schema, 0002 seed (bulk_insert from alembic/seed/countries.json)
├── tests/                 # pytest + pytest-asyncio + httpx against a real Postgres
├── docker-compose.yml     # postgres + api services, healthchecks
└── README.md
```

## Stack

Python 3.13 · FastAPI · Uvicorn · PostgreSQL 18 (Alpine) · SQLAlchemy 2.0 (async) · Alembic

## API

| Method & Path | Description |
|---|---|
| `GET /health` | Liveness check |
| `GET /countries` | Paginated list. Query params: `region`, `subregion`, `search`, `limit` (default 50, max 250), `offset` (default 0) |
| `GET /countries/{cca2}` | Single country by ISO alpha-2 code (case-insensitive). 404 if not found |

### Example

```bash
curl "http://localhost:8000/countries?region=Europe&search=and&limit=5"
curl "http://localhost:8000/countries/AD"
```

## Data

Seeded from a static dataset (see `alembic/versions/0002_seed_countries.py` and `alembic/seed/countries.json`), assembled from [mledoze/countries](https://github.com/mledoze/countries) and the World Bank population dataset — the same dataset bundled by the `vanilla-countries` frontend. **250** entries, one per ISO 3166-1 alpha-2 code, including non-sovereign territories (Puerto Rico, Hong Kong, Greenland, etc.) alongside sovereign states.

## Known Limitations

- **Read-only** — no create/update/delete endpoints, no auth, no versioning, no caching. Out of scope by design, not an oversight.
- **Static snapshot** — the seed data is bundled at a point in time rather than fetched live, so figures like population will drift out of date until the dataset is refreshed.
- **Not wired to the frontend** — `vanilla-countries` still ships its own bundled `assets/countries.json` independently; this API is a standalone service, not (yet) consumed by it.
- **Open CORS** — `CORS_ORIGINS=["*"]` is fine for a portfolio/testing context but is not a production security posture.
