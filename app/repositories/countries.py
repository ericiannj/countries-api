from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.country import Country


async def list_countries(
    session: AsyncSession,
    *,
    region: str | None = None,
    subregion: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Country], int]:
    filters = []
    if region:
        filters.append(Country.region == region)
    if subregion:
        filters.append(Country.subregion == subregion)
    if search:
        pattern = f"%{search}%"
        filters.append(Country.name_common.ilike(pattern) | Country.name_official.ilike(pattern))

    count_query = select(func.count()).select_from(Country)
    query = select(Country).options(
        selectinload(Country.languages),
        selectinload(Country.currencies),
        selectinload(Country.borders),
    )
    for condition in filters:
        count_query = count_query.where(condition)
        query = query.where(condition)

    total = (await session.execute(count_query)).scalar_one()

    query = query.order_by(Country.name_common).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all()), total


async def get_country_by_code(session: AsyncSession, cca2: str) -> Country | None:
    query = (
        select(Country)
        .where(func.upper(Country.cca2) == cca2.upper())
        .options(
            selectinload(Country.languages),
            selectinload(Country.currencies),
            selectinload(Country.borders),
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()
