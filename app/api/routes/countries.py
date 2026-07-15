from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories import countries as countries_repo
from app.schemas.country import CountryRead, PaginatedCountries

router = APIRouter(prefix="/countries", tags=["countries"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=PaginatedCountries)
async def list_countries_route(
    session: SessionDep,
    region: str | None = None,
    subregion: str | None = None,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=250)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedCountries:
    countries, total = await countries_repo.list_countries(
        session,
        region=region,
        subregion=subregion,
        search=search,
        limit=limit,
        offset=offset,
    )
    return PaginatedCountries(
        items=[CountryRead.from_model(c) for c in countries],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{cca2}", response_model=CountryRead)
async def get_country_route(cca2: str, session: SessionDep) -> CountryRead:
    country = await countries_repo.get_country_by_code(session, cca2)
    if country is None:
        raise HTTPException(status_code=404, detail=f"Country '{cca2}' not found")
    return CountryRead.from_model(country)
