from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_204_NO_CONTENT, HTTP_200_OK,
)
from app.domain.parser.service import ParserService

parser_router = APIRouter(prefix="/parsing", tags=["Parser"])


@parser_router.get(
    "/test",
    response_description="Successful.",
    status_code=HTTP_200_OK,
    summary="Старт Парсера в ручную",
    description="""""",
)
async def parse(
    service: Annotated[ParserService, Depends()],
):
    return await service.predict_data()
