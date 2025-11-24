import gettext
import logging
from contextvars import ContextVar

from app.core import settings

supported_locales = ["en", "ru"]


class Translator:
    def __init__(self, locale: str):
        locale_dir = settings.LOCALE_DIR

        if locale == settings.DEFAULT_LOCALE or locale not in supported_locales:
            self.translations = None
        else:
            self.translations = gettext.translation(
                domain="messages",
                localedir=locale_dir,
                languages=[locale],
                fallback=True,
            )

    def translate(self, message: str):
        if not self.translations:
            return message

        translated = self.translations.gettext(message)
        return translated


locale: ContextVar[str] = ContextVar("locale")
translator: ContextVar[Translator] = ContextVar("translator")


def _(message: str) -> str:
    try:
        return translator.get().translate(message)
    except LookupError:
        logging.warning(
            f"Translation not found, returning message untranslated ({message})"
        )
        return message


def N_(message: str) -> str:
    return message


def render_message(raw: str, **params) -> str:
    text = _(raw)
    if not params:
        return text
    try:
        return text.format(**params)
    except Exception as e:
        logging.exception("i18n format error for %r params=%r: %s", raw, params, e)
        return text
