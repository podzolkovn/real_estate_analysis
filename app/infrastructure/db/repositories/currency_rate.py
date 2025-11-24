from datetime import date, datetime
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select, Select, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.type_vars import MODEL
from app.infrastructure.db.models import CurrencyRateModel
from app.infrastructure.db.repositories.sqlalchemy_base import SqlAlchemyBaseRepository
from app.infrastructure.db.sessions import get_async_session



class CurrencyRateModelRepository(SqlAlchemyBaseRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(model=CurrencyRateModel, session=session)

    async def get_all(self, **kwargs: dict[str, Any]) -> list[MODEL]:
        """Retrieve a list of objects based on filter criteria."""
        filters = {**kwargs}
        stmt: "Select" = select(self._MODEL).filter_by(**filters)
        result: "Result" = await self.session.execute(stmt)
        await self.session.close()
        return result.scalars().all()