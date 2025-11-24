import fastapi as fa
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic_core import ValidationError

from app.core.exceptions.exceptions import (
    ParserError,
    ObjectDoesNotExistException,
    ObjectAlreadyExistException,
    HttpConnectionException,
)
from app.core.exceptions.handlers import (
    validation_exception_handler,
    http_exception_handler,
    parser_exception_handler,
    object_does_not_exist_exception_handler,
    custom_value_exception_handler,
    connection_error_handler,
    object_already_exist_exception_handler,
)


def register_exception_handler(app: fa.FastAPI):
    """Registers custom exception handlers for application-specific and validation errors in FastAPI."""
    app.add_exception_handler(
        ObjectDoesNotExistException,
        object_does_not_exist_exception_handler,
    )
    app.add_exception_handler(
        ObjectAlreadyExistException,
        object_already_exist_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        ValidationError,
        custom_value_exception_handler,
    )
    app.add_exception_handler(
        HttpConnectionException,
        connection_error_handler,
    )
    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )
    app.add_exception_handler(
        ParserError,
        parser_exception_handler,
    )
