from sqlalchemy import ARRAY, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import country_borders, country_currencies, country_languages


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    cca2: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    flag: Mapped[str] = mapped_column(default="")
    name_common: Mapped[str]
    name_official: Mapped[str]
    capital: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    population: Mapped[int | None] = mapped_column(nullable=True)
    area: Mapped[float | None] = mapped_column(Float, nullable=True)
    region: Mapped[str | None] = mapped_column(index=True, nullable=True)
    subregion: Mapped[str | None] = mapped_column(nullable=True)

    languages: Mapped[list["Language"]] = relationship(
        secondary=country_languages, back_populates="countries", order_by="Language.code"
    )
    currencies: Mapped[list["Currency"]] = relationship(
        secondary=country_currencies, back_populates="countries", order_by="Currency.code"
    )
    borders: Mapped[list["Country"]] = relationship(
        secondary=country_borders,
        primaryjoin="Country.id == country_borders.c.country_id",
        secondaryjoin="Country.id == country_borders.c.border_country_id",
        order_by="Country.cca2",
    )
