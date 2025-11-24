from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.exceptions import (
    ObjectDoesNotExistException,
    ObjectAlreadyExistException,
)
from app.core.type_vars import MODEL
from .abstract import AbstractRepository
from typing import Generic, Any, TYPE_CHECKING
from sqlalchemy import UUID

if TYPE_CHECKING:
    from sqlalchemy import Select, Result


class SqlAlchemyBaseRepository(AbstractRepository[MODEL], Generic[MODEL]):
    """Base repository implementation using SQLAlchemy for asynchronous database operations."""

    def __init__(self, model: type[MODEL], session: AsyncSession):
        super().__init__(model)
        self._MODEL = model
        self.session = session

    async def get_by_id(self, obj_id: int | str | UUID) -> MODEL | None:
        """Retrieve an object by its unique identifier."""
        stmt: "Select" = select(self._MODEL).filter_by(id=obj_id, is_deleted=False)
        resp: "Result" = await self.session.execute(stmt)
        result = resp.scalar()
        await self.session.close()
        if result:
            return result
        else:
            raise ObjectDoesNotExistException(
                model_name=self._MODEL.__name__, object_id=obj_id
            )

    async def filter(self, **kwargs: dict[str, Any]) -> list[MODEL]:
        """Retrieve a list of objects based on filter criteria."""
        filters = {**kwargs, "is_deleted": False}
        stmt: "Select" = select(self._MODEL).filter_by(**filters)
        result: "Result" = await self.session.execute(stmt)
        await self.session.close()
        return result.scalars().all()

    async def create(self, **kwargs: dict[str, Any]) -> MODEL | None:
        """Create a new object with the given attributes and return it."""
        obj: MODEL = self._MODEL(**kwargs)
        self.session.add(obj)
        try:
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.session.rollback()
        finally:
            await self.session.close()

    async def update(
        self, obj_id: int | str | UUID, **kwargs: dict[str, Any]
    ) -> MODEL | None:
        """Update an existing object by its ID with the given attributes."""

        stmt: "Select" = select(self._MODEL).filter_by(id=obj_id, is_deleted=False)
        result: "Result" = await self.session.execute(stmt)
        obj: MODEL = result.scalars().first()
        if obj:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(obj, key, value)

            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            await self.session.close()
            return obj
        else:
            raise ObjectDoesNotExistException(
                model_name=self._MODEL.__name__, object_id=obj_id
            )

    async def delete(self, obj_id: int | str | UUID) -> None:
        """Delete an object by its unique identifier."""

        stmt: "Select" = select(self._MODEL).filter_by(id=obj_id)
        result: "Result" = await self.session.execute(stmt)
        obj: MODEL = result.scalars().first()
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            await self.session.close()
        else:
            raise ObjectDoesNotExistException(
                model_name=self._MODEL.__name__, object_id=obj_id
            )

    async def soft_delete(self, obj_id: int | str | UUID) -> None:
        """Soft delete an object by its unique identifier (set is_deleted=True)."""

        stmt: "Select" = select(self._MODEL).filter_by(id=obj_id, is_deleted=False)
        result: "Result" = await self.session.execute(stmt)
        obj: MODEL = result.scalars().first()
        if obj:
            obj.is_deleted = True
            self.session.add(obj)
            await self.session.commit()
            await self.session.close()
        else:
            raise ObjectDoesNotExistException(
                model_name=self._MODEL.__name__, object_id=obj_id
            )
