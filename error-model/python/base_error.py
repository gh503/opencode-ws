"""Python error model implementation following AE-OS unified error schema."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class ErrorCategory(str, Enum):
    """Unified error categories across all languages."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    DEPENDENCY = "dependency"
    INTERNAL = "internal"


class ErrorLayer(str, Enum):
    """Application layer where error occurred."""
    PRESENTATION = "presentation"
    SERVICE = "service"
    DATA = "data"
    INFRASTRUCTURE = "infrastructure"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BaseError(Exception):
    """
    Base error class for all Python services.
    
    Follows AE-OS unified error modeling specification.
    All errors must have:
    - error_code: Language prefix + Category + Sequential number
    - category: One of ErrorCategory values
    - severity: ErrorSeverity level
    - message: User-safe message for external exposure
    - correlation_id: Request tracing ID
    
    Internal context (root_cause, stack_context, fix) is logged separately
    and NOT exposed in API responses.
    """
    
    # Language prefix for error codes
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        error_code: str,
        category: ErrorCategory,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        layer: ErrorLayer = ErrorLayer.SERVICE,
        root_cause: Optional[str] = None,
        stack_context: Optional[str] = None,
        fix: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.category = category
        self.message = message
        self.severity = severity
        self.layer = layer
        self.root_cause = root_cause
        self.stack_context = stack_context
        self.fix = fix
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
        
        super().__init__(message)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (for internal logging)."""
        return {
            "error_code": self.error_code,
            "category": self.category.value,
            "layer": self.layer.value,
            "severity": self.severity.value,
            "message": self.message,
            "root_cause": self.root_cause,
            "stack_context": self.stack_context,
            "fix": self.fix,
            "correlation_id": self.correlation_id,
            "details": self.details,
            "timestamp": self.timestamp,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())
    
    def to_safe_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for external API response.
        Excludes internal details (root_cause, stack_context, fix).
        """
        return {
            "error_code": self.error_code,
            "category": self.category.value,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "details": self.details,
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code!r}, "
            f"category={self.category.value!r}, "
            f"message={self.message!r})"
        )


# Specific error types for common categories
class ValidationError(BaseError):
    """Raised when input validation fails."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str,
        error_code: str = "PY-VAL-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.VALIDATION,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            correlation_id=correlation_id,
            details=details,
        )


class AuthenticationError(BaseError):
    """Raised when authentication fails."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "PY-AUTH-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.AUTHENTICATION,
            message=message,
            severity=ErrorSeverity.HIGH,
            correlation_id=correlation_id,
            details=details,
        )


class AuthorizationError(BaseError):
    """Raised when authorization fails."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Access denied",
        error_code: str = "PY-AUTHZ-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.AUTHORIZATION,
            message=message,
            severity=ErrorSeverity.HIGH,
            correlation_id=correlation_id,
            details=details,
        )


class NotFoundError(BaseError):
    """Raised when requested resource is not found."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "PY-NOTF-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.NOT_FOUND,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            correlation_id=correlation_id,
            details=details,
        )


class ConflictError(BaseError):
    """Raised when resource conflict occurs."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "PY-CONF-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.CONFLICT,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            correlation_id=correlation_id,
            details=details,
        )


class RateLimitError(BaseError):
    """Raised when rate limit is exceeded."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "PY-RATE-001",
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.RATE_LIMIT,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            correlation_id=correlation_id,
            details=details,
        )


class DependencyError(BaseError):
    """Raised when external dependency fails."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "External service unavailable",
        error_code: str = "PY-DEP-001",
        root_cause: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.DEPENDENCY,
            message=message,
            severity=ErrorSeverity.HIGH,
            root_cause=root_cause,
            correlation_id=correlation_id,
            details=details,
        )


class InternalError(BaseError):
    """Raised for internal server errors."""
    LANG_PREFIX = "PY"
    
    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "PY-INT-001",
        root_cause: Optional[str] = None,
        fix: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.INTERNAL,
            message=message,
            severity=ErrorSeverity.CRITICAL,
            root_cause=root_cause,
            fix=fix,
            correlation_id=correlation_id,
            details=details,
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
