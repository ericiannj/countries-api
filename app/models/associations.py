from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

country_languages = Table(
    "country_languages",
    Base.metadata,
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
    Column("language_id", Integer, ForeignKey("languages.id"), primary_key=True),
)

country_currencies = Table(
    "country_currencies",
    Base.metadata,
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
    Column("currency_id", Integer, ForeignKey("currencies.id"), primary_key=True),
)

country_borders = Table(
    "country_borders",
    Base.metadata,
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
    Column("border_country_id", Integer, ForeignKey("countries.id"), primary_key=True),
)
