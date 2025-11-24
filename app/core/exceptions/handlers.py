from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError

from app.core import logger
from app.core.exceptions.error_codes import error_codes
from app.core.exceptions.exceptions import (
    ParserError,
    ObjectDoesNotExistException,
    HttpConnectionException,
    ObjectAlreadyExistException,
)
from app.core.schemas import ErrorSchema, BaseResponseSchema


def exception_response(status_code: int, errors: list[ErrorSchema]) -> JSONResponse:
    content = BaseResponseSchema(data=None, errors=errors)
    logger.error("status_code=%d, content=%s", status_code, content.model_dump())
    return JSONResponse(
        status_code=status_code,
        content=content.model_dump(),
    )


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    ERROR_CODE = error_codes["ERROR_FORM_VALIDATION"]
    """Handles request validation errors and returns a 400 response with details."""
    errors = [
        ErrorSchema(
            code=ERROR_CODE["code"],
            message=ERROR_CODE["message"],
            details=[
                {
                    "error": e["type"],
                    "field": ".".join(str(loc) for loc in e["loc"][1:]),
                    "message": f"{(e['msg'])} (input: {e.get('input')})",
                }
                for e in exc.errors()
            ],
        )
    ]
    return exception_response(ERROR_CODE["status"], errors)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = str(exc.status_code)
    message = exc.detail if isinstance(exc.detail, str) else "Unexpected error"
    details = exc.detail if isinstance(exc.detail, dict | list) else None

    error = ErrorSchema(
        code=code,
        message=message,
        details=details,
    )
    return exception_response(exc.status_code, [error])


def parser_exception_handler(request: Request, exc: ParserError) -> JSONResponse:
    error = exc.to_error_schema()
    return exception_response(exc.code, [error])


def object_does_not_exist_exception_handler(
    request: Request,
    exc: ObjectDoesNotExistException,
) -> JSONResponse:  # noqa: E501
    """Handles exceptions for non-existent objects and returns a 404 response."""
    ERROR_CODE = error_codes["ERROR_OBJECT_NOT_FOUND"]
    error = ErrorSchema(
        code=ERROR_CODE["code"],
        message=ERROR_CODE["message"],
        details=[{"message": exc.args[0], "object_id": str(exc.args[1])}],
    )
    return exception_response(ERROR_CODE["status"], errors=[error])


def object_already_exist_exception_handler(
    request: Request,
    exc: ObjectAlreadyExistException,
) -> JSONResponse:  # noqa: E501
    """Handles exceptions for duplicate objects and returns a 404 response."""
    ERROR_CODE = error_codes["ERROR_ALREADY_EXISTS"]
    error = ErrorSchema(
        code=ERROR_CODE["code"],
        message=ERROR_CODE["message"],
        details=[{"message": exc.args[0], "object_id": str(exc.args[1])}],
    )
    return exception_response(ERROR_CODE["status"], errors=[error])


def connection_error_handler(
    request: Request, exc: HttpConnectionException
) -> JSONResponse:
    ERROR_CODE = error_codes["ERROR_INFRASTRUCTURE"]
    error = ErrorSchema(
        code=ERROR_CODE["code"],
        message=ERROR_CODE["message"],
        details=[{"message": exc.args[0]}],
    )
    return exception_response(ERROR_CODE["status"], errors=[error])


async def internal_server_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    ERROR_CODE = error_codes["ERROR_INTERNAL_SERVER"]
    errors = [
        ErrorSchema(
            code=ERROR_CODE["code"],
            message=ERROR_CODE["message"],
            details=[
                {
                    "message": exc.args[0],
                }
            ],
        )
    ]
    return exception_response(ERROR_CODE["status"], errors)


def custom_value_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    ERROR_CODE = error_codes["ERROR_FORM_VALIDATION"]
    """Handles other data validation errors and returns a 400 response with details."""
    errors = [
        ErrorSchema(
            code=ERROR_CODE["code"],
            message=ERROR_CODE["message"],
            details=[
                {
                    "error": e["type"],
                    "field": e["loc"][0] if e["loc"] else None,
                    "message": f"{e["msg"].replace("Value error, ", "")}",  # (input: {e["input"]})
                }
                for e in exc.errors()
            ],
        )
    ]
    return exception_response(ERROR_CODE["status"], errors)
