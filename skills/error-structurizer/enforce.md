# Error Structurizer - Enforcement Rules

## Enforcement Checklist

Before completing any bug fix, verify:

- [ ] Error has valid `error_code` (format: `LANG-CATEGORY-XXX`)
- [ ] Error has valid `category` from allowed values
- [ ] Error has valid `severity` level
- [ ] Error has user-safe `message` (no internal details)
- [ ] Error has `correlation_id` for tracing
- [ ] Internal details (root_cause, stack_context, fix) logged separately
- [ ] Error follows language-specific implementation pattern
- [ ] JSON output is valid and parseable

## Validation Rules

### Error Code Validation

```python
# Python validation example
import re

ERROR_CODE_PATTERN = re.compile(r'^[A-Z]{2,3}-[A-Z]+-\d{3}$')

def validate_error_code(code: str) -> bool:
    return bool(ERROR_CODE_PATTERN.match(code))
```

### Category Validation

Allowed categories:
- `validation` - Input validation failures
- `authentication` - Auth failures
- `authorization` - Permission denied
- `not_found` - Resource not found
- `conflict` - State conflict
- `rate_limit` - Rate exceeded
- `dependency` - External service failure
- `internal` - Internal server error

### Severity Validation

Allowed severities:
- `critical` - System down, data loss risk
- `high` - Major functionality broken
- `medium` - Feature degraded
- `low` - Minor issue, workarounds available
- `info` - Informational

## Common Violations

### ❌ Wrong: Natural Language Only

```
Error: Something went wrong while processing your request.
```

### ✅ Correct: Structured JSON

```json
{
  "error_code": "PY-VAL-001",
  "category": "validation",
  "severity": "medium",
  "message": "Invalid email format",
  "correlation_id": "req-xyz123"
}
```

### ❌ Wrong: Exposing Internal Details

```json
{
  "error_code": "PY-INT-001",
  "message": "NullPointerException at UserService.getUser:42 - stack trace: ...",
  ...
}
```

### ✅ Correct: Safe for Users, Full for Logs

```json
// External API response
{
  "error_code": "PY-INT-001",
  "message": "An internal error occurred",
  "correlation_id": "req-abc123"
}

// Internal log (separate)
{
  "error_code": "PY-INT-001",
  "root_cause": "NullPointerException at UserService.getUser:42",
  "fix": "Add null check",
  "correlation_id": "req-abc123"
}
```

## Integration

### Code Review Checklist

1. All error returns follow structured format
2. Error codes are meaningful and consistent
3. No sensitive data in error messages
4. Correlation IDs present for tracing
5. Appropriate HTTP status codes returned

### Testing

- Validate error structure in unit tests
- Test error serialization/deserialization
- Verify error code uniqueness
- Test error logging (internal vs external)
