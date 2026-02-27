"""Python error model package."""

from error_model.python.base_error import (
    BaseError,
    ErrorCategory,
    ErrorLayer,
    ErrorSeverity,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    DependencyError,
    InternalError,
)

__all__ = [
    "BaseError",
    "ErrorCategory",
    "ErrorLayer",
    "ErrorSeverity",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "DependencyError",
    "InternalError",
]
