---
name: enterprise-error-model
description: Enforce structured error modeling across languages
compatibility: opencode
---

## When to apply
Apply to all services and libraries.

## Rules
- Error object must contain:
  - error_code
  - category
  - safe message
  - correlation_id
  - structured details
- Map internal errors to API responses safely.
