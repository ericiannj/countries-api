"""schema

Revision ID: 0001_schema
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cca2", sa.String(2), nullable=False, unique=True),
        sa.Column("flag", sa.String, nullable=False, server_default=""),
        sa.Column("name_common", sa.String, nullable=False),
        sa.Column("name_official", sa.String, nullable=False),
        sa.Column("capital", sa.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("population", sa.Integer, nullable=True),
        sa.Column("area", sa.Float, nullable=True),
        sa.Column("region", sa.String, nullable=True),
        sa.Column("subregion", sa.String, nullable=True),
    )
    op.create_index("ix_countries_cca2", "countries", ["cca2"], unique=True)
    op.create_index("ix_countries_region", "countries", ["region"])

    op.create_table(
        "languages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False),
    )
    op.create_index("ix_languages_code", "languages", ["code"], unique=True)

    op.create_table(
        "currencies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("symbol", sa.String, nullable=False, server_default=""),
    )
    op.create_index("ix_currencies_code", "currencies", ["code"], unique=True)

    op.create_table(
        "country_languages",
        sa.Column("country_id", sa.Integer, sa.ForeignKey("countries.id"), primary_key=True),
        sa.Column("language_id", sa.Integer, sa.ForeignKey("languages.id"), primary_key=True),
    )
    op.create_table(
        "country_currencies",
        sa.Column("country_id", sa.Integer, sa.ForeignKey("countries.id"), primary_key=True),
        sa.Column("currency_id", sa.Integer, sa.ForeignKey("currencies.id"), primary_key=True),
    )
    op.create_table(
        "country_borders",
        sa.Column("country_id", sa.Integer, sa.ForeignKey("countries.id"), primary_key=True),
        sa.Column("border_country_id", sa.Integer, sa.ForeignKey("countries.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("country_borders")
    op.drop_table("country_currencies")
    op.drop_table("country_languages")
    op.drop_table("currencies")
    op.drop_table("languages")
    op.drop_table("countries")
