/**
 * TypeScript error model implementation following AE-OS unified error schema
 */

// Error category enumeration
export enum ErrorCategory {
  Validation = 'validation',
  Authentication = 'authentication',
  Authorization = 'authorization',
  NotFound = 'not_found',
  Conflict = 'conflict',
  RateLimit = 'rate_limit',
  Dependency = 'dependency',
  Internal = 'internal',
}

// Application layer where error occurred
export enum ErrorLayer {
  Presentation = 'presentation',
  Service = 'service',
  Data = 'data',
  Infrastructure = 'infrastructure',
}

// Error severity level
export enum ErrorSeverity {
  Critical = 'critical',
  High = 'high',
  Medium = 'medium',
  Low = 'low',
  Info = 'info',
}

// Error code type - enforces pattern: LANG-CATEGORY-XXX
export type ErrorCode =
  // Validation
  | 'TS-VAL-001' | 'TS-VAL-002' | 'TS-VAL-003'
  // Authentication
  | 'TS-AUTH-001' | 'TS-AUTH-002' | 'TS-AUTH-003'
  // Authorization
  | 'TS-AUTHZ-001' | 'TS-AUTHZ-002' | 'TS-AUTHZ-003'
  // Not Found
  | 'TS-NOTF-001' | 'TS-NOTF-002' | 'TS-NOTF-003'
  // Conflict
  | 'TS-CONF-001' | 'TS-CONF-002' | 'TS-CONF-003'
  // Rate Limit
  | 'TS-RATE-001' | 'TS-RATE-002' | 'TS-RATE-003'
  // Dependency
  | 'TS-DEP-001' | 'TS-DEP-002' | 'TS-DEP-003'
  // Internal
  | 'TS-INT-001' | 'TS-INT-002' | 'TS-INT-003'
  // Custom codes can extend this type
  | string;

// Unified error interface following AE-OS specification
export interface IUnifiedError {
  error_code: ErrorCode;
  category: ErrorCategory;
  layer?: ErrorLayer;
  severity: ErrorSeverity;
  message: string;
  root_cause?: string;
  stack_context?: string;
  fix?: string;
  correlation_id: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// Safe error interface for external API responses
export interface ISafeError {
  error_code: ErrorCode;
  category: ErrorCategory;
  message: string;
  correlation_id: string;
  details?: Record<string, unknown>;
}

// UnifiedError class implementation
export class UnifiedError extends Error implements IUnifiedError {
  public error_code: ErrorCode;
  public category: ErrorCategory;
  public layer: ErrorLayer;
  public severity: ErrorSeverity;
  public root_cause?: string;
  public stack_context?: string;
  public fix?: string;
  public correlation_id: string;
  public details?: Record<string, unknown>;
  public timestamp: string;

  constructor(
    errorCode: ErrorCode,
    category: ErrorCategory,
    message: string,
    severity: ErrorSeverity = ErrorSeverity.High,
    options?: {
      layer?: ErrorLayer;
      root_cause?: string;
      stack_context?: string;
      fix?: string;
      correlation_id?: string;
      details?: Record<string, unknown>;
    }
  ) {
    super(message);
    this.name = 'UnifiedError';
    this.error_code = errorCode;
    this.category = category;
    this.layer = options?.layer ?? ErrorLayer.Service;
    this.severity = severity;
    this.root_cause = options?.root_cause;
    this.stack_context = options?.stack_context;
    this.fix = options?.fix;
    this.correlation_id = options?.correlation_id ?? crypto.randomUUID();
    this.details = options?.details;
    this.timestamp = new Date().toISOString();
  }

  /**
   * Convert to plain object for logging (includes all fields)
   */
  toLogObject(): IUnifiedError {
    return {
      error_code: this.error_code,
      category: this.category,
      layer: this.layer,
      severity: this.severity,
      message: this.message,
      root_cause: this.root_cause,
      stack_context: this.stack_context,
      fix: this.fix,
      correlation_id: this.correlation_id,
      details: this.details,
      timestamp: this.timestamp,
    };
  }

  /**
   * Convert to JSON string for logging
   */
  toJSON(): string {
    return JSON.stringify(this.toLogObject(), null, 2);
  }

  /**
   * Convert to safe object for API response (excludes internal details)
   */
  toSafeObject(): ISafeError {
    return {
      error_code: this.error_code,
      category: this.category,
      message: this.message,
      correlation_id: this.correlation_id,
      details: this.details,
    };
  }

  /**
   * Get HTTP status code mapping
   */
  toHttpStatus(): number {
    switch (this.category) {
      case ErrorCategory.Validation:
        return 400;
      case ErrorCategory.Authentication:
        return 401;
      case ErrorCategory.Authorization:
        return 403;
      case ErrorCategory.NotFound:
        return 404;
      case ErrorCategory.Conflict:
        return 409;
      case ErrorCategory.RateLimit:
        return 429;
      case ErrorCategory.Dependency:
        return 503;
      case ErrorCategory.Internal:
      default:
        return 500;
    }
  }
}

// Convenience constructors for common error types

export function createValidationError(
  message: string,
  errorCode: ErrorCode = 'TS-VAL-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Validation, message, ErrorSeverity.Medium, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createAuthenticationError(
  message = 'Authentication failed',
  errorCode: ErrorCode = 'TS-AUTH-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Authentication, message, ErrorSeverity.High, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createAuthorizationError(
  message = 'Access denied',
  errorCode: ErrorCode = 'TS-AUTHZ-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Authorization, message, ErrorSeverity.High, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createNotFoundError(
  message = 'Resource not found',
  errorCode: ErrorCode = 'TS-NOTF-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.NotFound, message, ErrorSeverity.Medium, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createConflictError(
  message = 'Resource conflict',
  errorCode: ErrorCode = 'TS-CONF-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Conflict, message, ErrorSeverity.Medium, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createRateLimitError(
  message = 'Rate limit exceeded',
  errorCode: ErrorCode = 'TS-RATE-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.RateLimit, message, ErrorSeverity.Medium, {
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createDependencyError(
  message = 'External service unavailable',
  errorCode: ErrorCode = 'TS-DEP-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details' | 'root_cause'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Dependency, message, ErrorSeverity.High, {
    root_cause: options?.root_cause,
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

export function createInternalError(
  message = 'Internal server error',
  errorCode: ErrorCode = 'TS-INT-001',
  options?: Partial<Pick<IUnifiedError, 'correlation_id' | 'details' | 'root_cause' | 'fix'>>
): UnifiedError {
  return new UnifiedError(errorCode, ErrorCategory.Internal, message, ErrorSeverity.Critical, {
    root_cause: options?.root_cause,
    fix: options?.fix,
    correlation_id: options?.correlation_id,
    details: options?.details,
  });
}

// Type guards

export function isUnifiedError(error: unknown): error is UnifiedError {
  return error instanceof UnifiedError;
}

export function isSafeError(error: unknown): error is ISafeError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'error_code' in error &&
    'category' in error &&
    'message' in error &&
    'correlation_id' in error
  );
}
