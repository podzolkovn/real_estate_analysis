from typing import Any, Union
from uuid import UUID

from app.core.i18n import _
from app.core.schemas import ErrorSchema


class ApplicationBaseException(Exception):
    """Base exception class for application-specific errors."""

    def __init__(self, *args):
        super().__init__(*args)


class ParserError(Exception):
    def __init__(self, code: int, message: str, details: Any = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_error_schema(self) -> ErrorSchema:
        return ErrorSchema(
            code=str(self.code), message=self.message, details=self.details
        )


class ObjectDoesNotExistException(ApplicationBaseException):
    """Raised when an object with the given ID does not exist in the database."""

    def __init__(self, model_name: str, object_id: Union[UUID, str, int]):
        msg = _("{model_name} with id {object_id} not found").format(
            model_name=model_name, object_id=object_id
        )
        super().__init__(msg, object_id)


class ObjectAlreadyExistException(ApplicationBaseException):
    """Raised when an object with the given ID does not exist in the database."""

    def __init__(self, model_name: str, object_id: Union[UUID, str, int]):
        msg = _("{model_name} with id {object_id} already added").format(
            model_name=model_name, object_id=object_id
        )
        super().__init__(msg, object_id)


class HttpConnectionException(ApplicationBaseException):
    def __init__(self, url):
        msg = _("Error connecting to remote server: {url}").format(url=url)
        super().__init__(msg)
