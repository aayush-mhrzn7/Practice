from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError


class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    type: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: list[ValidationErrorDetail] = []


class APIErrorResponse(BaseModel):
    success: bool = False
    error: ErrorPayload


def _validation_details(errors: list) -> list[dict]:
    details = []
    for err in errors:
        loc = err.get("loc", ())
        details.append({
            "field": ".".join(str(part) for part in loc),
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })
    return details


def _error_response(status_code: int, code: str, message: str, details: list[dict] | None = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
        },
    )


async def http_validation_error_handler(_request: Request, exc: RequestValidationError):
    """OpenAPI HTTPValidationError — invalid path, query, or body."""
    return _error_response(
        status_code=422,
        code="HTTP_VALIDATION_ERROR",
        message="Request validation failed",
        details=_validation_details(exc.errors()),
    )


async def pydantic_validation_error_handler(_request: Request, exc: ValidationError):
    """Pydantic ValidationError raised outside request parsing."""
    return _error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Data validation failed",
        details=_validation_details(exc.errors()),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, http_validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
