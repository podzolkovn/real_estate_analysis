from datetime import date as DateType
from decimal import Decimal

from sqlalchemy import Date, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models import SimpleIDMixin


class CurrencyRateModel(SimpleIDMixin):
    __tablename__ = 'currency_rate'
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    usd: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)