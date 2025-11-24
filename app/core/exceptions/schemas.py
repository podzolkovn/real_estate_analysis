from pydantic import BaseModel, ConfigDict


class BadRequestErrorDetailSchema(BaseModel):
    """Schema for detailing field-specific validation errors in a bad request."""

    field: str
    message: str

    model_config = ConfigDict(extra="forbid")


class BadRequestErrorSchema(BaseModel):
    """Schema for representing a bad request error with multiple validation details."""

    error: str
    detail: list[BadRequestErrorDetailSchema]

    model_config = ConfigDict(extra="forbid")


class NotFoundErrorDetailSchema(BaseModel):
    """Schema for representing a not found error with a message field."""

    message: str

    model_config = ConfigDict(extra="forbid")
