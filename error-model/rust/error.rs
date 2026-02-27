//! Rust error model implementation following AE-OS unified error schema

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fmt;

/// Error category enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorCategory {
    Validation,
    Authentication,
    Authorization,
    NotFound,
    Conflict,
    RateLimit,
    Dependency,
    Internal,
}

impl fmt::Display for ErrorCategory {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorCategory::Validation => write!(f, "validation"),
            ErrorCategory::Authentication => write!(f, "authentication"),
            ErrorCategory::Authorization => write!(f, "authorization"),
            ErrorCategory::NotFound => write!(f, "not_found"),
            ErrorCategory::Conflict => write!(f, "conflict"),
            ErrorCategory::RateLimit => write!(f, "rate_limit"),
            ErrorCategory::Dependency => write!(f, "dependency"),
            ErrorCategory::Internal => write!(f, "internal"),
        }
    }
}

/// Application layer where error occurred
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorLayer {
    Presentation,
    Service,
    Data,
    Infrastructure,
}

impl Default for ErrorLayer {
    fn default() -> Self {
        ErrorLayer::Service
    }
}

impl fmt::Display for ErrorLayer {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorLayer::Presentation => write!(f, "presentation"),
            ErrorLayer::Service => write!(f, "service"),
            ErrorLayer::Data => write!(f, "data"),
            ErrorLayer::Infrastructure => write!(f, "infrastructure"),
        }
    }
}

/// Error severity level
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorSeverity {
    Critical,
    High,
    Medium,
    Low,
    Info,
}

impl fmt::Display for ErrorSeverity {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorSeverity::Critical => write!(f, "critical"),
            ErrorSeverity::High => write!(f, "high"),
            ErrorSeverity::Medium => write!(f, "medium"),
            ErrorSeverity::Low => write!(f, "low"),
            ErrorSeverity::Info => write!(f, "info"),
        }
    }
}

/// Unified error structure following AE-OS specification
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnifiedError {
    /// Language prefix + Category + Sequential number (e.g., "RS-NULL-001")
    pub error_code: String,
    /// Error category
    pub category: ErrorCategory,
    /// Application layer
    #[serde(default)]
    pub layer: ErrorLayer,
    /// Severity level
    pub severity: ErrorSeverity,
    /// User-safe message for external exposure
    pub message: String,
    /// Internal technical root cause (not exposed externally)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub root_cause: Option<String>,
    /// Stack trace or context information
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stack_context: Option<String>,
    /// Suggested fix or remediation
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fix: Option<String>,
    /// Request correlation ID for tracing
    pub correlation_id: String,
    /// Additional structured metadata
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub details: Option<serde_json::Value>,
    /// ISO 8601 timestamp
    pub timestamp: DateTime<Utc>,
}

impl fmt::Display for UnifiedError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.error_code, self.message)
    }
}

impl std::error::Error for UnifiedError {}

impl UnifiedError {
    /// Create a new unified error
    pub fn new(
        error_code: impl Into<String>,
        category: ErrorCategory,
        message: impl Into<String>,
        severity: ErrorSeverity,
    ) -> Self {
        Self {
            error_code: error_code.into(),
            category,
            layer: ErrorLayer::default(),
            severity,
            message: message.into(),
            root_cause: None,
            stack_context: None,
            fix: None,
            correlation_id: uuid::Uuid::new_v4().to_string(),
            details: None,
            timestamp: Utc::now(),
        }
    }

    /// Set the layer
    pub fn with_layer(mut self, layer: ErrorLayer) -> Self {
        self.layer = layer;
        self
    }

    /// Set root cause (internal only)
    pub fn with_root_cause(mut self, cause: impl Into<String>) -> Self {
        self.root_cause = Some(cause.into());
        self
    }

    /// Set stack context (internal only)
    pub fn with_stack_context(mut self, context: impl Into<String>) -> Self {
        self.stack_context = Some(context.into());
        self
    }

    /// Set fix suggestion (internal only)
    pub fn with_fix(mut self, fix: impl Into<String>) -> Self {
        self.fix = Some(fix.into());
        self
    }

    /// Set correlation ID
    pub fn with_correlation_id(mut self, id: impl Into<String>) -> Self {
        self.correlation_id = id.into();
        self
    }

    /// Set details
    pub fn with_details(mut self, details: serde_json::Value) -> Self {
        self.details = Some(details);
        self
    }

    /// Convert to map for logging (includes all fields)
    pub fn to_log_map(&self) -> serde_json::Value {
        serde_json::to_value(self).unwrap_or_default()
    }

    /// Convert to safe map for API response (excludes internal details)
    pub fn to_safe_map(&self) -> serde_json::Value {
        serde_json::json!({
            "errorCode": self.error_code,
            "category": self.category.to_string(),
            "message": self.message,
            "correlationId": self.correlation_id,
            "details": self.details,
        })
    }
}

// Convenience constructors for common error types

/// Create a validation error
pub fn validation_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-VAL-001",
        ErrorCategory::Validation,
        message,
        ErrorSeverity::Medium,
    )
}

/// Create an authentication error
pub fn authentication_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-AUTH-001",
        ErrorCategory::Authentication,
        message,
        ErrorSeverity::High,
    )
}

/// Create an authorization error
pub fn authorization_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-AUTHZ-001",
        ErrorCategory::Authorization,
        message,
        ErrorSeverity::High,
    )
}

/// Create a not found error
pub fn not_found_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-NOTF-001",
        ErrorCategory::NotFound,
        message,
        ErrorSeverity::Medium,
    )
}

/// Create a conflict error
pub fn conflict_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-CONF-001",
        ErrorCategory::Conflict,
        message,
        ErrorSeverity::Medium,
    )
}

/// Create a rate limit error
pub fn rate_limit_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-RATE-001",
        ErrorCategory::RateLimit,
        message,
        ErrorSeverity::Medium,
    )
}

/// Create a dependency error
pub fn dependency_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-DEP-001",
        ErrorCategory::Dependency,
        message,
        ErrorSeverity::High,
    )
}

/// Create an internal error
pub fn internal_error(message: impl Into<String>) -> UnifiedError {
    UnifiedError::new(
        "RS-INT-001",
        ErrorCategory::Internal,
        message,
        ErrorSeverity::Critical,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_creation() {
        let err = UnifiedError::new(
            "RS-TEST-001",
            ErrorCategory::Validation,
            "Invalid input",
            ErrorSeverity::Medium,
        );

        assert_eq!(err.error_code, "RS-TEST-001");
        assert_eq!(err.category, ErrorCategory::Validation);
        assert_eq!(err.message, "Invalid input");
    }

    #[test]
    fn test_serialization() {
        let err = UnifiedError::new(
            "RS-TEST-001",
            ErrorCategory::Validation,
            "Invalid input",
            ErrorSeverity::Medium,
        )
        .with_correlation_id("test-123");

        let json = serde_json::to_string(&err).unwrap();
        assert!(json.contains("RS-TEST-001"));
    }
}
