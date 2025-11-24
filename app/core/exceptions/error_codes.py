from starlette import status

error_codes = {
    "ERROR_OBJECT_NOT_FOUND": {
        "status": status.HTTP_404_NOT_FOUND,
        "code": "ERROR:NOT_FOUND:ENTITY",
        "message": "Requested object doesn't exist",
    },
    "ERROR_FORM_VALIDATION": {
        "status": status.HTTP_400_BAD_REQUEST,
        "code": "ERROR:BAD_REQUEST:VALIDATION_ERROR",
        "message": "Query form validation error",
    },
    "ERROR_INFRASTRUCTURE": {
        "status": status.HTTP_503_SERVICE_UNAVAILABLE,
        "code": "ERROR:INFRASTRUCTURE",
        "message": "Something went wrong, try again later",
    },
    "ERROR_AUTH_REQUIRED": {
        "status": status.HTTP_401_UNAUTHORIZED,
        "code": "ERROR:UNAUTHORIZED",
        "message": "Authentication credentials were not provided",
    },
    "ERROR_BAD_REQUEST": {
        "status": status.HTTP_409_CONFLICT,
        "code": "ERROR:BAD_REQUEST",
        "message": "Bad request: {details}",
    },
    "ERROR_ALREADY_EXISTS": {
        "status": status.HTTP_409_CONFLICT,
        "code": "ERROR:DUPLICATE:ENTITY",
        "message": "Requested {model_name} with id {object_id} already exists",
    },
}
