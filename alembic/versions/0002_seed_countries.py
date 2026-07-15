"""seed countries data

Revision ID: 0002_seed_countries
Revises: 0001_schema
"""
import json
from pathlib import Path

from alembic import op
from sqlalchemy import ARRAY, Float, Integer, String, column, table

revision = "0002_seed_countries"
down_revision = "0001_schema"
branch_labels = None
depends_on = None

SEED_PATH = Path(__file__).resolve().parents[1] / "seed" / "countries.json"

countries_table = table(
    "countries",
    column("id", Integer),
    column("cca2", String),
    column("flag", String),
    column("name_common", String),
    column("name_official", String),
    column("capital", ARRAY(String)),
    column("population", Integer),
    column("area", Float),
    column("region", String),
    column("subregion", String),
)
languages_table = table(
    "languages", column("id", Integer), column("code", String), column("name", String)
)
currencies_table = table(
    "currencies",
    column("id", Integer),
    column("code", String),
    column("name", String),
    column("symbol", String),
)
country_languages_table = table(
    "country_languages", column("country_id", Integer), column("language_id", Integer)
)
country_currencies_table = table(
    "country_currencies", column("country_id", Integer), column("currency_id", Integer)
)
country_borders_table = table(
    "country_borders", column("country_id", Integer), column("border_country_id", Integer)
)


def upgrade() -> None:
    with SEED_PATH.open(encoding="utf-8") as f:
        raw_countries = json.load(f)

    languages_by_code: dict[str, str] = {}
    currencies_by_code: dict[str, dict] = {}
    for c in raw_countries:
        for code, name in (c.get("languages") or {}).items():
            languages_by_code.setdefault(code, name)
        for code, info in (c.get("currencies") or {}).items():
            currencies_by_code.setdefault(code, info)

    language_ids = {code: idx + 1 for idx, code in enumerate(sorted(languages_by_code))}
    currency_ids = {code: idx + 1 for idx, code in enumerate(sorted(currencies_by_code))}
    country_ids = {c["cca2"]: idx + 1 for idx, c in enumerate(raw_countries)}

    op.bulk_insert(
        languages_table,
        [
            {"id": language_ids[code], "code": code, "name": name}
            for code, name in languages_by_code.items()
        ],
    )
    op.bulk_insert(
        currencies_table,
        [
            {
                "id": currency_ids[code],
                "code": code,
                "name": info.get("name", ""),
                "symbol": info.get("symbol", ""),
            }
            for code, info in currencies_by_code.items()
        ],
    )
    op.bulk_insert(
        countries_table,
        [
            {
                "id": country_ids[c["cca2"]],
                "cca2": c["cca2"],
                "flag": c.get("flag", ""),
                "name_common": c["name"]["common"],
                "name_official": c["name"].get("official", c["name"]["common"]),
                "capital": c.get("capital") or [],
                "population": c.get("population"),
                "area": c.get("area"),
                "region": c.get("region"),
                "subregion": c.get("subregion"),
            }
            for c in raw_countries
        ],
    )

    country_language_rows = []
    country_currency_rows = []
    country_border_rows = []
    for c in raw_countries:
        cid = country_ids[c["cca2"]]
        for code in c.get("languages") or {}:
            country_language_rows.append({"country_id": cid, "language_id": language_ids[code]})
        for code in c.get("currencies") or {}:
            country_currency_rows.append({"country_id": cid, "currency_id": currency_ids[code]})
        for border_code in c.get("borders") or []:
            border_id = country_ids.get(border_code)
            if border_id is not None:
                country_border_rows.append({"country_id": cid, "border_country_id": border_id})

    if country_language_rows:
        op.bulk_insert(country_languages_table, country_language_rows)
    if country_currency_rows:
        op.bulk_insert(country_currencies_table, country_currency_rows)
    if country_border_rows:
        op.bulk_insert(country_borders_table, country_border_rows)

    for table_name in ("languages", "currencies", "countries"):
        op.execute(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
            f"(SELECT COALESCE(MAX(id), 1) FROM {table_name}))"
        )


def downgrade() -> None:
    op.execute("DELETE FROM country_borders")
    op.execute("DELETE FROM country_currencies")
    op.execute("DELETE FROM country_languages")
    op.execute("DELETE FROM countries")
    op.execute("DELETE FROM currencies")
    op.execute("DELETE FROM languages")
