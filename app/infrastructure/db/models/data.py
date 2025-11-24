from decimal import Decimal

from sqlalchemy import DECIMAL, String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.infrastructure.db.models import SimpleIDModelWithCreatedAt


class DataModel(SimpleIDModelWithCreatedAt):
    __tablename__ = "data"
    price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=True)
    region: Mapped[str] = mapped_column(String, nullable=True)
    complex_Label: Mapped[str] = mapped_column(String, nullable=True)
    area: Mapped[int] = mapped_column(Integer, nullable=True)
    price_per_area_metr: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=True)
    views: Mapped[int] = mapped_column(Integer, nullable=True)
    rooms: Mapped[int] = mapped_column(Integer, nullable=True)