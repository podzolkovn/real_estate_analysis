from datetime import datetime
from typing import ClassVar
from sqlalchemy import Integer, DateTime, func, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.config import Base


class SimpleIDMixin(Base):

    __abstract__: ClassVar[bool] = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class CreatedAtTimeStampMixin(Base):
    __abstract__: ClassVar[bool] = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class UpdatedAtTimeStampMixin(Base):
    __abstract__: ClassVar[bool] = True

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )


class SoftDeleteMixin(Base):
    __abstract__: ClassVar[bool] = True
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        default=False,
        nullable=True,
    )


class BaseModelIntID(
    SimpleIDMixin, CreatedAtTimeStampMixin, UpdatedAtTimeStampMixin, SoftDeleteMixin
):
    __abstract__: ClassVar[bool] = True


class SimpleIDModelWithOutTime(SimpleIDMixin, SoftDeleteMixin):
    __abstract__: ClassVar[bool] = True


class SimpleIDModelWithCreatedAt(
    SimpleIDMixin, SoftDeleteMixin, CreatedAtTimeStampMixin
):
    __abstract__: ClassVar[bool] = True


class SimpleIDModelWithUpdatedAt(
    SimpleIDMixin, SoftDeleteMixin, UpdatedAtTimeStampMixin
):
    __abstract__: ClassVar[bool] = True
