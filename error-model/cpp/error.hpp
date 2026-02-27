#ifndef AE_OS_ERROR_HPP
#define AE_OS_ERROR_HPP

#include <string>
#include <optional>
#include <chrono>
#include <uuid/uuid.h>
#include <nlohmann/json.hpp>

namespace aeos {

/// Error category enumeration
enum class ErrorCategory {
    Validation,
    Authentication,
    Authorization,
    NotFound,
    Conflict,
    RateLimit,
    Dependency,
    Internal
};

/// Application layer where error occurred
enum class ErrorLayer {
    Presentation,
    Service,
    Data,
    Infrastructure
};

/// Error severity level
enum class ErrorSeverity {
    Critical,
    High,
    Medium,
    Low,
    Info
};

/// Convert ErrorCategory to string
inline std::string category_to_string(ErrorCategory cat) {
    switch (cat) {
        case ErrorCategory::Validation: return "validation";
        case ErrorCategory::Authentication: return "authentication";
        case ErrorCategory::Authorization: return "authorization";
        case ErrorCategory::NotFound: return "not_found";
        case ErrorCategory::Conflict: return "conflict";
        case ErrorCategory::RateLimit: return "rate_limit";
        case ErrorCategory::Dependency: return "dependency";
        case ErrorCategory::Internal: return "internal";
        default: return "unknown";
    }
}

/// Convert ErrorLayer to string
inline std::string layer_to_string(ErrorLayer layer) {
    switch (layer) {
        case ErrorLayer::Presentation: return "presentation";
        case ErrorLayer::Service: return "service";
        case ErrorLayer::Data: return "data";
        case ErrorLayer::Infrastructure: return "infrastructure";
        default: return "service";
    }
}

/// Convert ErrorSeverity to string
inline std::string severity_to_string(ErrorSeverity sev) {
    switch (sev) {
        case ErrorSeverity::Critical: return "critical";
        case ErrorSeverity::High: return "high";
        case ErrorSeverity::Medium: return "medium";
        case ErrorSeverity::Low: return "low";
        case ErrorSeverity::Info: return "info";
        default: return "medium";
    }
}

/// Unified error structure following AE-OS specification
class UnifiedError {
public:
    /// Language prefix + Category + Sequential number (e.g., "CPP-NULL-001")
    std::string error_code;
    
    /// Error category
    ErrorCategory category;
    
    /// Application layer
    ErrorLayer layer = ErrorLayer::Service;
    
    /// Severity level
    ErrorSeverity severity;
    
    /// User-safe message for external exposure
    std::string message;
    
    /// Internal technical root cause (not exposed externally)
    std::optional<std::string> root_cause;
    
    /// Stack trace or context information
    std::optional<std::string> stack_context;
    
    /// Suggested fix or remediation
    std::optional<std::string> fix;
    
    /// Request correlation ID for tracing
    std::string correlation_id;
    
    /// Additional structured metadata
    std::optional<nlohmann::json> details;
    
    /// ISO 8601 timestamp
    std::string timestamp;

    UnifiedError() {
        // Generate UUID for correlation_id
        uuid_t uuid;
        uuid_generate_random(uuid);
        char uuid_str[37];
        uuid_unparse_lower(uuid, uuid_str);
        correlation_id = uuid_str;
        
        // Set timestamp
        auto now = std::chrono::system_clock::now();
        auto now_time_t = std::chrono::system_clock::to_time_t(now);
        char timestamp_str[32];
        std::strftime(timestamp_str, sizeof(timestamp_str), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&now_time_t));
        timestamp = timestamp_str;
    }

    UnifiedError(
        const std::string& code,
        ErrorCategory cat,
        const std::string& msg,
        ErrorSeverity sev
    ) : error_code(code), category(cat), severity(sev), message(msg) {
        // Generate UUID for correlation_id
        uuid_t uuid;
        uuid_generate_random(uuid);
        char uuid_str[37];
        uuid_unparse_lower(uuid, uuid_str);
        correlation_id = uuid_str;
        
        // Set timestamp
        auto now = std::chrono::system_clock::now();
        auto now_time_t = std::chrono::system_clock::to_time_t(now);
        char timestamp_str[32];
        std::strftime(timestamp_str, sizeof(timestamp_str), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&now_time_t));
        timestamp = timestamp_str;
    }

    /// Convert to JSON string
    std::string to_json() const {
        return to_json_object().dump(2);
    }

    /// Convert to JSON object for logging (includes all fields)
    nlohmann::json to_json_object() const {
        nlohmann::json j;
        j["error_code"] = error_code;
        j["category"] = category_to_string(category);
        j["layer"] = layer_to_string(layer);
        j["severity"] = severity_to_string(severity);
        j["message"] = message;
        
        if (root_cause.has_value()) {
            j["root_cause"] = root_cause.value();
        }
        if (stack_context.has_value()) {
            j["stack_context"] = stack_context.value();
        }
        if (fix.has_value()) {
            j["fix"] = fix.value();
        }
        
        j["correlation_id"] = correlation_id;
        
        if (details.has_value()) {
            j["details"] = details.value();
        }
        
        j["timestamp"] = timestamp;
        return j;
    }

    /// Convert to JSON object for API response (excludes internal details)
    nlohmann::json to_safe_json_object() const {
        nlohmann::json j;
        j["error_code"] = error_code;
        j["category"] = category_to_string(category);
        j["message"] = message;
        j["correlation_id"] = correlation_id;
        
        if (details.has_value()) {
            j["details"] = details.value();
        }
        
        return j;
    }

    /// Set layer
    UnifiedError& with_layer(ErrorLayer l) {
        layer = l;
        return *this;
    }

    /// Set root cause (internal only)
    UnifiedError& with_root_cause(const std::string& cause) {
        root_cause = cause;
        return *this;
    }

    /// Set stack context (internal only)
    UnifiedError& with_stack_context(const std::string& context) {
        stack_context = context;
        return *this;
    }

    /// Set fix suggestion (internal only)
    UnifiedError& with_fix(const std::string& f) {
        fix = f;
        return *this;
    }

    /// Set correlation ID
    UnifiedError& with_correlation_id(const std::string& id) {
        correlation_id = id;
        return *this;
    }

    /// Set details
    UnifiedError& with_details(const nlohmann::json& d) {
        details = d;
        return *this;
    }

    /// Error message
    const char* what() const noexcept {
        return message.c_str();
    }
};

// Convenience functions for creating errors

inline UnifiedError make_validation_error(const std::string& message) {
    return UnifiedError("CPP-VAL-001", ErrorCategory::Validation, message, ErrorSeverity::Medium);
}

inline UnifiedError make_authentication_error(const std::string& message = "Authentication failed") {
    return UnifiedError("CPP-AUTH-001", ErrorCategory::Authentication, message, ErrorSeverity::High);
}

inline UnifiedError make_authorization_error(const std::string& message = "Access denied") {
    return UnifiedError("CPP-AUTHZ-001", ErrorCategory::Authorization, message, ErrorSeverity::High);
}

inline UnifiedError make_not_found_error(const std::string& message = "Resource not found") {
    return UnifiedError("CPP-NOTF-001", ErrorCategory::NotFound, message, ErrorSeverity::Medium);
}

inline UnifiedError make_conflict_error(const std::string& message = "Resource conflict") {
    return UnifiedError("CPP-CONF-001", ErrorCategory::Conflict, message, ErrorSeverity::Medium);
}

inline UnifiedError make_rate_limit_error(const std::string& message = "Rate limit exceeded") {
    return UnifiedError("CPP-RATE-001", ErrorCategory::RateLimit, message, ErrorSeverity::Medium);
}

inline UnifiedError make_dependency_error(const std::string& message = "External service unavailable") {
    return UnifiedError("CPP-DEP-001", ErrorCategory::Dependency, message, ErrorSeverity::High);
}

inline UnifiedError make_internal_error(const std::string& message = "Internal server error") {
    return UnifiedError("CPP-INT-001", ErrorCategory::Internal, message, ErrorSeverity::Critical);
}

} // namespace aeos

#endif // AE_OS_ERROR_HPP
