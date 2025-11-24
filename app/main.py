from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import settings, logger
from app.core.exceptions.register import register_exception_handler
from app.core.middleware.i18n import I18nMiddleware
from app.core.middleware.metrics import RequestMetricsMiddleware
from app.core.routers import bind_routers
from app.core.scheduler import scheduler
# from app.core.tasks.shutdown import close_browser
# from app.core.tasks.startup import setup_browser, start_scheduler


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         await setup_browser()
#     except Exception as e:
#         logger.exception(f"Ошибка setup_browser: {e}")
#     try:
#         await start_scheduler()
#     except Exception as e:
#         logger.exception(f"Ошибка start_scheduler: {e}")
#     yield
#     try:
#         scheduler.shutdown(wait=False)
#     except Exception as e:
#         logger.warning(f"Ошибка при завершении scheduler: {e}")
#
#     await close_browser()


def setup_application():
    app_ = FastAPI(
        title="Real Estate Analisis",
        version=settings.version,
        docs_url="/swagger",
        # lifespan=lifespan,
    )
    app_.add_middleware(I18nMiddleware)
    bind_routers(app=app_)

    register_exception_handler(app=app_)

    app_.add_middleware(RequestMetricsMiddleware)

    return app_


app = setup_application()
