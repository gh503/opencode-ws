/**
 * TypeScript Error Model Package
 * 
 * Unified error modeling for AE-OS Enterprise Secure Edition
 */

export {
  ErrorCategory,
  ErrorLayer,
  ErrorSeverity,
  type ErrorCode,
  type IUnifiedError,
  type ISafeError,
  UnifiedError,
  createValidationError,
  createAuthenticationError,
  createAuthorizationError,
  createNotFoundError,
  createConflictError,
  createRateLimitError,
  createDependencyError,
  createInternalError,
  isUnifiedError,
  isSafeError,
} from './error';
