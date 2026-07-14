# countries-api — Claude Code Guide

Standalone, read-only REST API serving country data (name, capital, population, area,
region, languages, currencies, neighboring countries) — a portfolio piece demonstrating
Python/FastAPI/SQLAlchemy/PostgreSQL. Replaces the static `assets/countries.json` bundled
by the `vanilla-countries` frontend, but is **not** wired into it (separate repo, CORS
left open for testing).

## Structure

```
app/
├── main.py                    # FastAPI() instance, CORS(*), router registration
├── core/config.py             # pydantic-settings: DATABASE_URL, CORS origins, etc.
├── db/                        # DeclarativeBase, async engine/session, get_session dependency
├── models/                    # Country, Language, Currency ORM models + association tables
├── schemas/                   # Pydantic response models (CountryRead, PaginatedCountries)
├── repositories/               # query layer: filtering, pagination, get-by-code
└── api/routes/                 # GET /countries, GET /countries/{cca2}, GET /health

alembic/versions/               # 0001 schema, 0002 seed (bulk_insert from alembic/seed/countries.json)
tests/                          # pytest + pytest-asyncio + httpx (ASGITransport) against a real Postgres
docker-compose.yml              # postgres + api services, healthchecks
```

Layering: routes → repository → models. Routes stay thin (parse params, call repository,
return schema); repository owns all query construction; models are plain ORM mappings.

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | Python 3.13 | via pyenv; plan originally specified 3.12, bumped since 3.12 isn't installed locally and 3.13 is current-stable |
| Framework | FastAPI (async) | |
| Server | Uvicorn | |
| Database | PostgreSQL 18 (Alpine) | via Docker Compose |
| ORM | SQLAlchemy 2.0, async (`asyncpg`) | `Mapped`/`mapped_column`, `AsyncSession`/`create_async_engine` — never mix in sync sessions |
| Migrations | Alembic, async template | `alembic init -t async`; schema (0001) + data seed (0002) as separate migrations |
| Settings | pydantic-settings | `Settings` in `app/core/config.py` |
| Testing | pytest + pytest-asyncio + httpx | `asyncio_mode = "auto"`, `asyncio_default_fixture_loop_scope = "function"` in `pyproject.toml` (required by pytest-asyncio 1.x) |
| Containerization | Docker Compose | `db` + `api` services, healthchecks |

## Key Conventions

- **Read-only.** No create/update/delete endpoints, no auth, no versioning, no caching —
  see the design spec's "explicitly out of scope" section. Don't add any of it unless asked.
- **All DB access is async.** Never introduce a sync SQLAlchemy session.
- **Response shape must match `CountryRead`** exactly as defined in the plan: `name`
  nested as `{common, official}`, `languages`/`currencies` as lists of objects, `borders`
  as a list of `cca2` strings.
- **Dependency pins must be current, not copied verbatim from the plan.** The plan
  document was written ~18 months before implementation started; its pinned versions
  were stale on day one. Before pinning or bumping a dependency, check the actual
  current stable release (`pip index versions <pkg>` or context7) rather than trusting
  the plan's literal numbers.

## Principles

- **English only** in code, comments, identifiers, and commit messages. Conversation
  with the user can stay in Portuguese.
- **Simplicity first / YAGNI.** No premature abstraction; don't build ahead of the
  current task in the plan.
- **Root cause over workaround.** If a fix feels like a patch, say so and propose the
  clean alternative.

## Rules

### Teach as you go
The person building this alongside Claude is using it to *learn* how to build APIs in
Python, not just to end up with a working API. After finishing each implementation task
(or logical chunk of one), explain what was built **in a teaching style**, grounded in
the actual code just written (with file references):
- What was done, concretely, and *why* it was done that way.
- The underlying concept(s) the task illustrates (dependency injection via `Depends`,
  async sessions vs. sync, migrations as versioned schema history, the repository
  pattern, Pydantic validation boundaries, self-referential many-to-many relationships,
  etc.) — explained as if teaching someone learning Python API development, not
  assuming the concept is obvious.
- Where relevant, the tradeoff or alternative not chosen, and why.
This applies task after task, throughout the whole plan, until the API is complete.

### No automatic commits
Do not run `git commit` without explicit user approval — staging (`git add`) is fine.
Before proposing a commit, explain what will be committed and why (per "teach as you
go" above), then wait for the green light. This applies to subagents too — never commit
as the final step of a task without surfacing it first. If a subagent pauses waiting for
approval, stop and surface that to the user rather than pushing it forward or acting in
its place.

### Tests
Run the relevant tests (`pytest`) before proposing a commit. Tests run against a real
Postgres (`countries_test` database), not SQLite — the `ARRAY(String)` column and
relational joins are Postgres-specific, per the design spec's testing strategy.

### Plan before non-trivial work
Follow the implementation plan's tasks in order. For anything the plan doesn't cover,
present the approach and get approval before writing code.

### Verify before declaring done
Never claim a task is complete without evidence — run the task's verification steps and
cite the actual output.

### Verify syntax against official docs
Before writing code against a library in the stack (FastAPI, SQLAlchemy, Alembic,
pydantic-settings, pytest-asyncio), use context7 to confirm current API and
configuration syntax rather than relying on training data, which may be outdated.
