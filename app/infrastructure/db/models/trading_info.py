from datetime import date

from sqlalchemy import String, Float, Date
from sqlalchemy.orm import mapped_column, Mapped

from app.infrastructure.db.models import SimpleIDModelWithCreatedAt


class TradingInfoModel(SimpleIDModelWithCreatedAt):
    __tablename__ = "trading_info"
    indicator: Mapped[str] = mapped_column(String, nullable=True)
    last: Mapped[float] = mapped_column(Float, nullable=True)
    previous: Mapped[float] = mapped_column(Float, nullable=True)
    highest: Mapped[float] = mapped_column(Float, nullable=True)
    lowest: Mapped[float] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=True)
    created_date: Mapped[date] = mapped_column(Date, nullable=True)