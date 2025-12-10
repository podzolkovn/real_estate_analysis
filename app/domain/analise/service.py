from typing import Annotated

from fastapi import Depends

from app.infrastructure.db.repositories.building_analisation import (
    BuildingAnalisationModelRepository,
)
from app.infrastructure.db.repositories.building_forecast import (
    BuildingForecastModelRepository,
)
from app.infrastructure.db.repositories.currency_rate import CurrencyRateModelRepository
from app.infrastructure.db.repositories.inflation import InflationModelRepository
from app.infrastructure.db.repositories.nds import NDSModelRepository


class AnaliseService:
    def __init__(
        self,
        build_analise_repo: Annotated[BuildingAnalisationModelRepository, Depends()],
        currency_rate_repo: Annotated[CurrencyRateModelRepository, Depends()],
        building_forecast_repo: Annotated[BuildingForecastModelRepository, Depends()],
        inflation_repo: Annotated[InflationModelRepository, Depends()],
        nds_repo: Annotated[NDSModelRepository, Depends()],
    ):
        self.build_analise_repo = build_analise_repo
        self.currency_rate_repo = currency_rate_repo
        self.building_forecast_repo = building_forecast_repo
        self.inflation_repo = inflation_repo
        self.nds_repo = nds_repo

    async def get_analise(self):
        pass
