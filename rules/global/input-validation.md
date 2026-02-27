# Global Rule: Input Validation Enforcement

## Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | global |
| Confidence Score | 0.95 |
| Impact Score | 8 |
| False Positive Rate | 2% |
| Created | 2026-02-01 |
| Last Triggered | 2026-02-28 |

---

## Trigger Condition

**Category**: `validation`  
**Error Code**: `*-VAL-001`

This rule triggers when any validation error occurs.

---

## Root Cause

Most validation errors occur due to:
1. Missing input sanitization
2. Lack of schema-based validation
3. No clear error messages

---

## Mandatory Enforcement

1. All user input must be validated against defined schemas
2. Use validation libraries (pydantic/zod/jsonschema)
3. Reject invalid input early with clear messages
4. Log validation failures for pattern analysis
5. Return structured errors (see error-structurizer skill)

---

## Applies To

- All API endpoints accepting user input
- Form submissions
- File uploads
- Configuration file parsing

---

## Verification Method

- Unit tests for all validation paths
- Integration tests with invalid inputs
- Code review checklist for validation
- Error log monitoring

---

## Notes

- This is a core global rule
- All other validation rules inherit from this
