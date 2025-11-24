from decimal import Decimal

from sqlalchemy import Integer, String, Date, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models import SimpleIDMixin


class BuildingForecastModel(SimpleIDMixin):
    __tablename__ = 'building_forecast'

    geo: Mapped[int] = mapped_column(Integer, nullable=False)
    geo_title: Mapped[str] = mapped_column(String, nullable=False)
    forecast_date: Mapped[Date] = mapped_column(Date, nullable=False)
    forecast_kzt: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    lower_bound_kzt: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=True)
    upper_bound_kzt: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=True)