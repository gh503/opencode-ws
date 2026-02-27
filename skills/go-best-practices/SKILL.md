---
name: go-best-practices
description: Enforce enterprise Go code structure and safety
compatibility: opencode
---

## When to apply
Use this when generating/modifying Go code.

## Rules
- Check and handle all errors explicitly.
- Use context for cancellation/timeouts.
- Structured logs with fields (service, correlation_id).
- Validation with schema definitions.
