import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core import settings
from app.core.i18n import locale, translator, Translator

logger = logging.getLogger(__name__)


def normalize_locale(locale_header: str) -> str:
    return locale_header.split(",")[0].split("-")[0]


class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware для установки контекста переводов"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        accept_language = request.headers.get(
            "Accept-Language", settings.DEFAULT_LOCALE
        )

        locale_value = normalize_locale(accept_language)
        token_locale = locale.set(locale_value)
        token_translator = translator.set(Translator(locale=locale_value))

        try:
            response = await call_next(request)
            response.headers["Content-Language"] = locale_value
            return response
        finally:
            locale.reset(token_locale)
            translator.reset(token_translator)
