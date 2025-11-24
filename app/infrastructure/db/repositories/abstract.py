from abc import ABC, abstractmethod
from typing import Generic, Any
from uuid import UUID

from app.core.type_vars import MODEL


class AbstractRepository(ABC, Generic[MODEL]):
    """Abstract base class for a repository pattern, defining common CRUD operations."""

    _MODEL: type[MODEL]

    def __init__(self, model: type[MODEL]):
        self.model = model

    @abstractmethod
    async def get_by_id(self, obj_id: int | str | UUID) -> MODEL | None:
        """Retrieve an object by its unique identifier."""
        raise NotImplementedError()

    @abstractmethod
    async def filter(self, **kwargs: dict[Any, Any]) -> list[MODEL]:
        """Retrieve a list of objects based on filter criteria."""
        raise NotImplementedError()

    @abstractmethod
    async def create(self, **kwargs: dict[Any, Any]) -> MODEL | None:
        """Create a new object with the given attributes and return it."""
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self, obj_id: int | str | UUID, **kwargs: dict[Any, Any]
    ) -> MODEL | None:
        """Update an existing object by its ID with the given attributes."""
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, obj_id: int | str | UUID) -> None:
        """Delete an object by its unique identifier."""
        raise NotImplementedError()
