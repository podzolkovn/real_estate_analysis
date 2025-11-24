from sqlalchemy import Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models import SimpleIDMixin


class NDSModel(SimpleIDMixin):
    __tablename__ = 'nds'
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    percent: Mapped[float] = mapped_column(Float, nullable=False)