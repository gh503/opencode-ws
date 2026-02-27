---
name: python-quality
description: Enforce enterprise Python backend quality and safety standards
compatibility: opencode
---

## When to apply
Use this when generating/modifying Python backend code.

## Rules
- Use explicit type hints.
- Avoid dynamic global state.
- No eval/exec on external input.
- Schema-based validation (pydantic or similar).
- Structured logging with correlation IDs.
- Custom exceptions for error categories; no bare Exception.
