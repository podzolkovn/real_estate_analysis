from fastapi import (
    APIRouter,
    FastAPI,
)
from prometheus_client import generate_latest
from starlette.responses import Response

from app.presentation.api.parser import parser_router

misc_router = APIRouter(prefix="", tags=["misc"])


@misc_router.get(path="/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


@misc_router.get(path="/healthcheck")
def health_check():
    return {"status": "healthy"}


@misc_router.get("/health")
def health_check_docker():
    return {"status": "ok"}


def bind_routers(app: FastAPI):
    """Binds and registers API routers to the FastAPI application with a common prefix."""
    router = APIRouter(prefix="/api/v1")
    router.include_router(router=parser_router)

    app.include_router(router=router)
    app.include_router(router=misc_router)
