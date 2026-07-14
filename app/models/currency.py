from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import country_currencies


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    symbol: Mapped[str] = mapped_column(default="")

    countries: Mapped[list["Country"]] = relationship(
        secondary=country_currencies, back_populates="currencies"
    )
