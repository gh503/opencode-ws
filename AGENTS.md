# AE-OS Enterprise Secure Rules v2.0

All generated code must meet enterprise-grade security,
reliability, and consistency requirements.

---

## 1. Security-First Principle

- Never trust external input.
- Validate and sanitize all boundary data.
- Apply least privilege in access control.
- Explicit data ownership and lifecycle management.
- Avoid insecure defaults.

Security directives are mandatory, not optional.

---

## 2. Threat & Risk Modeling

Before implementation, always provide:

1. Identified threat surface
2. Trust boundary analysis
3. Authentication/Authorization model
4. Defined failure scenarios
5. Observability plan

Always start responses with a threat modeling summary when code is involved.

---

## 3. Unified Error Modeling (All Languages)

All services/modules must use structured errors:

Error {
  error_code: string
  category: string
  message: string
  correlation_id: string
  details: optional structured metadata
}

Categories:
- ValidationError
- AuthenticationError
- AuthorizationError
- NotFoundError
- ConflictError
- RateLimitError
- DependencyError
- InternalError

- No raw strings as errors.
- Always log safe message and internal context separately.

---

## 4. Error Exposure Policy

- Do not expose internal error details externally.
- Map internal errors to stable public error codes.
- Avoid stack trace leaks.

---

## 5. Structured Logging

Logs must be structured and include:

- timestamp
- log level
- service_name
- correlation_id
- request_id

Sensitive data is never logged.  
Secrets must not appear in logs.

---

## 6. Input Validation

- Validate at boundary interfaces.
- Schema-based validation preferred.
- Reject invalid input early.
- Avoid implicit coercion.

---

## 7. Secrets & Credentials

- Hard-coding secrets is forbidden.
- Use environment-injected credentials.
- Never log secrets or credentials.

---

## 8. Concurrency & Determinism

- Avoid data races and undefined behavior.
- Explicit synchronization.
- Document thread safety guarantees.
- Avoid nondeterministic side effects.

---

## 9. Performance Discipline

- Measure before optimizing.
- Avoid premature micro-optimizations.
- Prefetch/caching documented with governance.

---

## 10. Response Format Protocol

Every multifaceted response must include:

1. Threat model summary
2. Unified error model definition
3. Architecture overview
4. Implementation
5. Testing strategy
6. Risk assessment
