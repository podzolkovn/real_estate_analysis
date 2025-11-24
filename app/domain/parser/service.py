from typing import Annotated, TYPE_CHECKING, Any, Optional

from fastapi import Depends
from sqlalchemy import func, select, tuple_

from app.core import logger
from app.infrastructure.db.repositories.data import DataModelRepository
from app.infrastructure.db.repositories.predict_data import PredictDataModelRepository
from app.infrastructure.parser_v2.start_parser import StartParser


class ParserService:
    def __init__(self, data_repo: Annotated[DataModelRepository, Depends()], predict_data_repo: Annotated[PredictDataModelRepository, Depends()]):
        self.data_repo = data_repo
        self.predict_data_repo = predict_data_repo

    async def run_parser(self):
        parser: StartParser = StartParser()
        raw_info = await parser.run()

        for item in raw_info:
            data = {
                "rooms": int(item.get("rooms") or 0),
                "area": float(item.get("area") or 0),
                "price": float(item.get("price") or 0),
                "price_per_area_metr": float(item.get("price_per_area_metr") or 0),
                "region": item.get("region") or "",
                "views": int(item.get("views") or 0),
                "complex_Label": item.get("complex_Label") or "",
            }
            try:
                await self.data_repo.upsert(data)
            except Exception as e:
                logger.exception(f"Ошибка при upsert данных: {e}")