from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_204_NO_CONTENT,
)
from app.domain.parser.service import ParserService

parser_router = APIRouter(prefix="/parsing", tags=["Parser"])


@parser_router.get(
    "/test",
    response_description="Successful.",
    status_code=HTTP_204_NO_CONTENT,
    summary="Старт Парсера в ручную",
    description="""""",
)
async def parse(
    service: Annotated[ParserService, Depends()],
):
    await service.run_parser()
