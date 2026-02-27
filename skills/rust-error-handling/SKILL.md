---
name: rust-error-handling
description: Enforce Rust error discipline and safety practices
compatibility: opencode
---

## When to apply
Use this when generating/modifying Rust code.

## Rules
- Do not use unwrap in production.
- Use Result<T, E> with custom error enums.
- Avoid panic for business paths.
- Structured logging via tracing with correlation_id.
