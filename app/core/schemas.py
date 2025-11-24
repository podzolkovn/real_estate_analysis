from typing import Any, Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with configuration to allow attribute-based model initialization."""

    class Config:
        from_attributes = True


class PaginationMeta(BaseSchema):
    current_page: int = Field(default=1, description="Текущая страница")
    per_page: int = Field(default=10, description="Количество элементов на странице")
    total_items: int = Field(..., description="Общее количество элементов")
    total_pages: int = Field(..., description="Общее количество страниц")


class PaginationLinks(BaseSchema):
    self: str
    first: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None
    last: Optional[str] = None


class PaginationResponse(BaseSchema):
    meta: PaginationMeta
    links: PaginationLinks


class ErrorSchema(BaseSchema):
    code: str
    message: str
    details: Any | None = None


class WarningsSchema(BaseSchema):
    code: str
    message: str


class BaseResponseSchema(BaseSchema):
    data: list[Any] | None = None
    errors: list[ErrorSchema] | None = None
    pagination: PaginationResponse | None = None
    warnings: list[WarningsSchema] | None = None
