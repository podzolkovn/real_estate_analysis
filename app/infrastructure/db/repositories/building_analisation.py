from datetime import date, datetime
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select, Select, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.type_vars import MODEL
from app.infrastructure.db.models import BuildingAnalisationModel
from app.infrastructure.db.repositories.sqlalchemy_base import SqlAlchemyBaseRepository
from app.infrastructure.db.sessions import get_async_session



class BuildingAnalisationModelRepository(SqlAlchemyBaseRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(model=BuildingAnalisationModel, session=session)

    async def get_all(self, **kwargs: dict[str, Any]) -> list[MODEL]:
        """Retrieve a list of objects based on filter criteria."""
        filters = {**kwargs}
        stmt: "Select" = select(self._MODEL).filter_by(**filters)
        result: "Result" = await self.session.execute(stmt)
        await self.session.close()
        return result.scalars().all()

    async def upsert_many(self, records: list[dict], chunk_size: int = 1000):
        if not records:
            return

        def normalize_date(v):
            if isinstance(v, date):
                return v
            if isinstance(v, str):
                return datetime.strptime(v, "%Y-%m-%d").date()
            return None

        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]

            # нормализация
            for r in chunk:
                r["last_updated"] = normalize_date(r.get("last_updated"))
                r["created_at"] = normalize_date(r.get("created_at"))

            stmt = insert(self.model).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=['geo_title', 'last_updated', 'created_at'],
                set_={
                    'geo': stmt.excluded.geo,
                    'geo_title': stmt.excluded.geo_title,
                    'average': stmt.excluded.average,
                    'average_kzt': stmt.excluded.average_kzt,
                    'rate_kzt': stmt.excluded.rate_kzt,
                    'calculated': stmt.excluded.calculated,
                    'total': stmt.excluded.total,
                    'rooms': stmt.excluded.rooms,
                    'building': stmt.excluded.building,
                    'last_updated': stmt.excluded.last_updated,
                    'min_average': stmt.excluded.min_average,
                    'max_rate': stmt.excluded.max_rate,
                    'value_on_axis': stmt.excluded.value_on_axis,
                }
            )

            await self.session.execute(stmt)

        await self.session.commit()