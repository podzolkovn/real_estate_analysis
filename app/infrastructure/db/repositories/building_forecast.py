from datetime import date, datetime
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select, Select, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.type_vars import MODEL
from app.infrastructure.db.models import BuildingForecastModel
from app.infrastructure.db.repositories.sqlalchemy_base import SqlAlchemyBaseRepository
from app.infrastructure.db.sessions import get_async_session



class BuildingForecastModelRepository(SqlAlchemyBaseRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(model=BuildingForecastModel, session=session)

    async def bulk_save_forecasts(self, forecasts: list[BuildingForecastModel]):
        """
        Сохраняет список прогнозов в базе данных асинхронно.
        """
        if not forecasts:
            return

        self.session.add_all(forecasts)
        await self.session.commit()