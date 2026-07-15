from pydantic import BaseModel, ConfigDict

from app.models.country import Country


class NameSchema(BaseModel):
    common: str
    official: str


class LanguageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str


class CurrencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    symbol: str


class CountryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cca2: str
    flag: str
    name: NameSchema
    capital: list[str]
    population: int | None
    area: float | None
    region: str | None
    subregion: str | None
    languages: list[LanguageRead]
    currencies: list[CurrencyRead]
    borders: list[str]

    @classmethod
    def from_model(cls, country: Country) -> "CountryRead":
        return cls(
            cca2=country.cca2,
            flag=country.flag,
            name=NameSchema(common=country.name_common, official=country.name_official),
            capital=country.capital,
            population=country.population,
            area=country.area,
            region=country.region,
            subregion=country.subregion,
            languages=[LanguageRead.model_validate(lang) for lang in country.languages],
            currencies=[CurrencyRead.model_validate(cur) for cur in country.currencies],
            borders=[b.cca2 for b in country.borders],
        )


class PaginatedCountries(BaseModel):
    items: list[CountryRead]
    total: int
    limit: int
    offset: int
