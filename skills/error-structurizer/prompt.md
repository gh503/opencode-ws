---
name: error-structurizer
description: Enforce structured error output when AI fixes bugs - output JSON, not natural language
compatibility: opencode
---

## What I Do

When you fix a bug or handle an error in code, you MUST output structured errors following the AE-OS unified error model.

## When to Apply

Apply whenever you:
- Fix a bug
- Handle an exception
- Return an error response
- Create custom error types

## Rules

### Mandatory: Output JSON Structure

All errors MUST be returned as valid JSON following this schema:

```json
{
  "error_code": "LANG-CATEGORY-XXX",
  "category": "validation|authentication|authorization|not_found|conflict|rate_limit|dependency|internal",
  "severity": "critical|high|medium|low|info",
  "message": "User-safe error message",
  "correlation_id": "request-trace-id",
  "details": {}
}
```

### Mandatory: Error Code Format

Error codes MUST follow pattern: `LANG-CATEGORY-XXX`

| Language | Prefix |
|----------|--------|
| Python   | PY     |
| Go       | GO     |
| Rust     | RS     |
| C++      | CPP    |
| TypeScript | TS   |

Categories: `VAL`, `AUTH`, `AUTHZ`, `NOTF`, `CONF`, `RATE`, `DEP`, `INT`

Examples:
- `PY-VAL-001` (Python Validation)
- `GO-AUTH-001` (Go Authentication)
- `TS-INT-001` (TypeScript Internal)

### Mandatory: Use Existing Error Types

DO NOT create custom error classes. Use the provided error model implementations:

- **Python**: `from error_model.python import BaseError, ValidationError, ...`
- **Go**: `import "error_model"; error_model.NewValidationError(...)`
- **Rust**: `use error_model::{UnifiedError, validation_error};`
- **C++**: `aeos::UnifiedError error = aeos::make_validation_error(...);`
- **TypeScript**: `import { createValidationError } from 'error-model';`

### Mandatory: Separate Internal vs External

- **Internal logging**: Include root_cause, stack_context, fix
- **External API**: Only expose error_code, category, message, correlation_id, details

### Forbidden

- ❌ Natural language error descriptions only
- ❌ Raw strings as errors
- ❌ Exposing stack traces to users
- ❌ Generic "Error occurred" messages

## Output Format

When fixing bugs, output:

```json
{
  "error_code": "PY-NULL-001",
  "category": "internal",
  "severity": "critical",
  "message": "An internal error occurred",
  "root_cause": "NullPointerException at UserService.getUser:42",
  "fix": "Add null check before accessing user object",
  "correlation_id": "req-abc123",
  "details": {"line": 42, "method": "getUser"}
}
```

Then provide the actual code fix.
