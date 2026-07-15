from sqlalchemy.ext.asyncio import AsyncSession

from app.models.country import Country
from app.models.currency import Currency
from app.models.language import Language


async def _seed_countries(db_session: AsyncSession) -> None:
    portuguese = Language(code="por", name="Portuguese")
    english = Language(code="eng", name="English")
    brl = Currency(code="BRL", name="Brazilian real", symbol="R$")
    usd = Currency(code="USD", name="United States dollar", symbol="$")

    brazil = Country(
        cca2="BR",
        flag="🇧🇷",
        name_common="Brazil",
        name_official="Federative Republic of Brazil",
        capital=["Brasília"],
        population=203_000_000,
        area=8_515_767.0,
        region="Americas",
        subregion="South America",
        languages=[portuguese],
        currencies=[brl],
    )
    usa = Country(
        cca2="US",
        flag="🇺🇸",
        name_common="United States",
        name_official="United States of America",
        capital=["Washington, D.C."],
        population=331_000_000,
        area=9_372_610.0,
        region="Americas",
        subregion="North America",
        languages=[english],
        currencies=[usd],
    )

    db_session.add_all([portuguese, english, brl, usd, brazil, usa])
    await db_session.commit()


async def test_list_countries_returns_all(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {c["cca2"] for c in body["items"]} == {"BR", "US"}


async def test_list_countries_filters_by_region(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries", params={"region": "Americas"})

    assert response.json()["total"] == 2


async def test_list_countries_filters_by_subregion(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries", params={"subregion": "South America"})

    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["cca2"] == "BR"


async def test_list_countries_search_by_name(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries", params={"search": "braz"})

    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["cca2"] == "BR"


async def test_list_countries_pagination(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries", params={"limit": 1, "offset": 1})

    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["items"]) == 1


async def test_get_country_by_code_success(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries/BR")

    assert response.status_code == 200
    body = response.json()
    assert body["name"]["common"] == "Brazil"
    assert body["languages"][0]["code"] == "por"


async def test_get_country_by_code_not_found(client, db_session):
    await _seed_countries(db_session)

    response = await client.get("/countries/ZZ")

    assert response.status_code == 404
