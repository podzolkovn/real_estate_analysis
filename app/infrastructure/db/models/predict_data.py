from decimal import Decimal

from sqlalchemy import Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models import SimpleIDMixin


class PredictDataModel(SimpleIDMixin):
    __tablename__ = 'predict_data'
    year: Mapped[int]= mapped_column(Integer, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=True)
