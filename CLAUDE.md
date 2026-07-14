# countries-api

Read-only FastAPI + PostgreSQL + SQLAlchemy (async) + Alembic REST API, built as a
portfolio piece. Design spec and implementation plan live in
`docs/superpowers/specs/` (spec) and `docs/superpowers/specs/plans/` (task-by-task plan).

## Working convention: teach as you go

The person building this alongside Claude is using this project to learn how to build
APIs in Python — not just to get a working API out the other end. Because of that:

- After finishing each implementation task (or logical chunk of one), explain what was
  just built **in a teaching style**, not just a status recap. Cover:
  - What was done, concretely.
  - *Why* it was done that way — the reasoning, not just the mechanics.
  - The underlying concept(s) the task illustrates (e.g. dependency injection via
    FastAPI's `Depends`, async SQLAlchemy sessions vs. sync, Alembic migrations as
    versioned schema history, the repository pattern, Pydantic validation boundaries,
    self-referential many-to-many relationships, etc.), explained as if teaching
    someone who is learning Python API development, not assuming the concept is obvious.
  - Where relevant, a short note on the tradeoff or alternative approach not chosen,
    and why.
- Keep it concise and concrete — grounded in the actual code just written, with file
  references — not a generic tutorial detached from what happened.
- This applies throughout the whole implementation plan, task after task, until the
  API is complete.
