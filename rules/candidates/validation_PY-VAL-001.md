# validation_PY-VAL-001

## Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | candidate |
| Confidence Score | 0.50 |
| Impact Score | 5 |
| False Positive Rate | 0% |
| Created | 2026-02-27 |
| Last Triggered | N/A |

---

## Trigger Condition

**Category**: `validation`  
**Error Code**: `PY-VAL-001`

This rule triggers when an error with code `PY-VAL-001` occurs in the `validation` category.

---

## Root Cause

User provided malformed email address

---

## Mandatory Enforcement

1. All input must be validated against defined schemas before processing
2. Use schema validation libraries (e.g., pydantic, zod, jsonschema)
3. Reject invalid input early with clear error messages
4. Log validation failures for pattern analysis

**Specific Fix**: Validate email format using regex or email library

---

## Applies To

- All user input endpoints
- API request payloads
- File uploads
- Configuration files

---

## Verification Method

1. Unit tests for error handling paths
2. Integration tests with error scenarios
3. Chaos testing for failure injection
4. Error log monitoring and alerting
5. Code review checklist for error handling

---

## Sample Error Messages

- Invalid email format

---

## Related Errors

- TS-VAL-*, PY-VAL-* series

---

## Notes

- Generated from 5 error occurrences
- Threshold: 5 occurrences
- Review required before promoting to global rules
