---
name: enterprise-logging-standard
description: Enforce structured and secure logging protocols
compatibility: opencode
---

## When to apply
Use across all systems.

## Rules
- Structured logs (JSON) with:
  - timestamp
  - level
  - service_name
  - correlation_id
  - request_id
- No sensitive information logged.
