from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import PredictDataModel
from app.infrastructure.db.repositories.sqlalchemy_base import SqlAlchemyBaseRepository
from app.infrastructure.db.sessions import get_async_session

if TYPE_CHECKING:
    from sqlalchemy import Select, Result


class PredictDataModelRepository(SqlAlchemyBaseRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(model=PredictDataModel, session=session)
