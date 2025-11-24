from datetime import date

from sqlalchemy import Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from app.infrastructure.db.models import SimpleIDMixin


class BuildingAnalisationModel(SimpleIDMixin):
    __tablename__ = 'building_analisation'
    __table_args__ = (
        UniqueConstraint(
            "geo_title",
            "last_updated",
            "created_at",
            name="uq_geo_title_last_updated_created_at"
        ),
    )

    geo: Mapped[int] = mapped_column(Integer, nullable=True, doc="Идентификатор географического региона")
    geo_title: Mapped[str] = mapped_column(String, nullable=True, doc="Название региона/города.")
    average: Mapped[int] = mapped_column(Integer, nullable=True, doc="Средняя цена за м² в USD")
    average_kzt: Mapped[int] = mapped_column(Integer, nullable=True, doc="Средняя цена за м² в тенге")
    rate_kzt: Mapped[float] = mapped_column(Float, nullable=True)
    calculated: Mapped[int] = mapped_column(Integer, nullable=True)
    total: Mapped[int] = mapped_column(Integer, nullable=True, doc="Общее количество объектов.")
    rooms: Mapped[str] = mapped_column(String, nullable=True, doc="Количество комнат")
    building: Mapped[str] = mapped_column(String, nullable=True)
    last_updated: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=True)
    min_average: Mapped[float] = mapped_column(Float, nullable=True)
    max_rate: Mapped[float] = mapped_column(Float, nullable=True)
    value_on_axis: Mapped[float] = mapped_column(Float, nullable=True)