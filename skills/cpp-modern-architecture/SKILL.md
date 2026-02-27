---
name: cpp-modern-architecture
description: Enforce modern and secure C++ best practices
compatibility: opencode
---

## When to apply
Use this when generating/modifying C++ code.

## Rules
- Use RAII and smart pointers; avoid raw new/delete.
- Avoid reinterpret_cast and unsafe UB patterns.
- Validate all external inputs.
- No buffer overflows; safe indexing.
- Structured logging (e.g. JSON logs with correlation_id).
- Explicit error types with categories.
