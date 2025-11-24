from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import DataModel
from app.infrastructure.db.repositories.sqlalchemy_base import SqlAlchemyBaseRepository
from app.infrastructure.db.sessions import get_async_session
from sqlalchemy import select


if TYPE_CHECKING:
    from sqlalchemy import Select, Result


class DataModelRepository(SqlAlchemyBaseRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(model=DataModel, session=session)

    async def upsert(self, data: dict):
        # пробуем найти существующую запись по уникальным полям логики
        query = select(DataModel).where(
            DataModel.rooms == int(data.get("rooms", 0)),
            DataModel.area == float(data.get("area", 0)),
            DataModel.price == float(data.get("price", 0)),
            DataModel.region == data.get("region")
        )
        result = await self.session.execute(query)
        instance = result.scalar_one_or_none()

        if instance:
            # обновляем существующую запись
            for key, value in data.items():
                setattr(instance, key, value)
            await self.session.commit()
            return instance
        else:
            # создаём новую запись
            instance = DataModel(**data)
            self.session.add(instance)
            await self.session.commit()
            return instance