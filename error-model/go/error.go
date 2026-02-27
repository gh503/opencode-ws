package error_model

import (
	"encoding/json"
	"time"
)

// ErrorCategory represents unified error categories
type ErrorCategory string

const (
	CategoryValidation ErrorCategory = "validation"
	CategoryAuth       ErrorCategory = "authentication"
	CategoryAuthz      ErrorCategory = "authorization"
	CategoryNotFound   ErrorCategory = "not_found"
	CategoryConflict   ErrorCategory = "conflict"
	CategoryRateLimit  ErrorCategory = "rate_limit"
	CategoryDependency ErrorCategory = "dependency"
	CategoryInternal   ErrorCategory = "internal"
)

// ErrorLayer represents application layer
type ErrorLayer string

const (
	LayerPresentation   ErrorLayer = "presentation"
	LayerService        ErrorLayer = "service"
	LayerData           ErrorLayer = "data"
	LayerInfrastructure ErrorLayer = "infrastructure"
)

// ErrorSeverity represents error severity level
type ErrorSeverity string

const (
	SeverityCritical ErrorSeverity = "critical"
	SeverityHigh     ErrorSeverity = "high"
	SeverityMedium   ErrorSeverity = "medium"
	SeverityLow      ErrorSeverity = "low"
	SeverityInfo     ErrorSeverity = "info"
)

// UnifiedError represents the AE-OS unified error structure
type UnifiedError struct {
	ErrorCode     string                 `json:"error_code"`
	Category      ErrorCategory          `json:"category"`
	Layer         ErrorLayer             `json:"layer,omitempty"`
	Severity      ErrorSeverity          `json:"severity"`
	Message       string                 `json:"message"`
	RootCause     string                 `json:"root_cause,omitempty"`
	StackContext  string                 `json:"stack_context,omitempty"`
	Fix           string                 `json:"fix,omitempty"`
	CorrelationID string                 `json:"correlation_id"`
	Details       map[string]interface{} `json:"details,omitempty"`
	Timestamp     string                 `json:"timestamp"`
}

// Error implements the error interface
func (e *UnifiedError) Error() string {
	return e.Message
}

// ToJSON serializes the error to JSON string
func (e *UnifiedError) ToJSON() (string, error) {
	if e.Timestamp == "" {
		e.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}
	data, err := json.Marshal(e)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// ToMap converts error to map for logging
func (e *UnifiedError) ToMap() map[string]interface{} {
	if e.Timestamp == "" {
		e.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}
	return map[string]interface{}{
		"error_code":     e.ErrorCode,
		"category":       e.Category,
		"layer":          e.Layer,
		"severity":       e.Severity,
		"message":        e.Message,
		"root_cause":     e.RootCause,
		"stack_context":  e.StackContext,
		"fix":            e.Fix,
		"correlation_id": e.CorrelationID,
		"details":        e.Details,
		"timestamp":      e.Timestamp,
	}
}

// ToSafeMap returns map for external API (excludes internal details)
func (e *UnifiedError) ToSafeMap() map[string]interface{} {
	return map[string]interface{}{
		"error_code":     e.ErrorCode,
		"category":       e.Category,
		"message":        e.Message,
		"correlation_id": e.CorrelationID,
		"details":        e.Details,
	}
}

// MarshalJSON implements custom JSON marshaling
func (e UnifiedError) MarshalJSON() ([]byte, error) {
	if e.Timestamp == "" {
		e.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}
	// Alias to avoid infinite recursion
	type Alias UnifiedError
	return json.Marshal(&struct {
		Alias
	}{
		Alias: Alias(e),
	})
}

// NewUnifiedError creates a new unified error
func NewUnifiedError(
	errorCode string,
	category ErrorCategory,
	message string,
	severity ErrorSeverity,
	opts ...ErrorOption,
) *UnifiedError {
	err := &UnifiedError{
		ErrorCode:     errorCode,
		Category:      category,
		Severity:      severity,
		Message:       message,
		Layer:         LayerService,
		CorrelationID: "",
		Details:       make(map[string]interface{}),
		Timestamp:     time.Now().UTC().Format(time.RFC3339),
	}

	for _, opt := range opts {
		opt(err)
	}

	return err
}

// ErrorOption functional option for error creation
type ErrorOption func(*UnifiedError)

// WithLayer sets the error layer
func WithLayer(layer ErrorLayer) ErrorOption {
	return func(e *UnifiedError) {
		e.Layer = layer
	}
}

// WithRootCause sets the root cause
func WithRootCause(rootCause string) ErrorOption {
	return func(e *UnifiedError) {
		e.RootCause = rootCause
	}
}

// WithStackContext sets the stack context
func WithStackContext(stack string) ErrorOption {
	return func(e *UnifiedError) {
		e.StackContext = stack
	}
}

// WithFix sets the fix suggestion
func WithFix(fix string) ErrorOption {
	return func(e *UnifiedError) {
		e.Fix = fix
	}
}

// WithCorrelationID sets the correlation ID
func WithCorrelationID(corrID string) ErrorOption {
	return func(e *UnifiedError) {
		e.CorrelationID = corrID
	}
}

// WithDetails sets additional details
func WithDetails(details map[string]interface{}) ErrorOption {
	return func(e *UnifiedError) {
		e.Details = details
	}
}

// Pre-defined error constructors

// NewValidationError creates a validation error
func NewValidationError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-VAL-001", CategoryValidation, message, SeverityMedium, opts...)
}

// NewAuthenticationError creates an authentication error
func NewAuthenticationError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-AUTH-001", CategoryAuth, message, SeverityHigh, opts...)
}

// NewAuthorizationError creates an authorization error
func NewAuthorizationError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-AUTHZ-001", CategoryAuthz, message, SeverityHigh, opts...)
}

// NewNotFoundError creates a not found error
func NewNotFoundError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-NOTF-001", CategoryNotFound, message, SeverityMedium, opts...)
}

// NewConflictError creates a conflict error
func NewConflictError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-CONF-001", CategoryConflict, message, SeverityMedium, opts...)
}

// NewRateLimitError creates a rate limit error
func NewRateLimitError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-RATE-001", CategoryRateLimit, message, SeverityMedium, opts...)
}

// NewDependencyError creates a dependency error
func NewDependencyError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-DEP-001", CategoryDependency, message, SeverityHigh, opts...)
}

// NewInternalError creates an internal error
func NewInternalError(message string, opts ...ErrorOption) *UnifiedError {
	return NewUnifiedError("GO-INT-001", CategoryInternal, message, SeverityCritical, opts...)
}
