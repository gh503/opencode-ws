# Secure Coding Standards

This document defines mandatory secure coding practices for all AE-OS projects.

---

## 1. Input Validation

### Mandatory Rules

- [ ] Validate ALL external input at the first entry point
- [ ] Use schema-based validation (pydantic, zod, jsonschema)
- [ ] Reject invalid input immediately - fail fast
- [ ] Use allowlists (whitelists) over blocklists
- [ ] Validate type, length, format, and range
- [ ] Normalize input before validation (trim, lowercase)

### Code Examples

```python
# ✅ Correct: Schema-based validation
from pydantic import BaseModel, EmailStr, validator

class UserInput(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    age: int = Field(ge=0, le=150)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

# ❌ Wrong: String concatenation
user_input = f"SELECT * FROM users WHERE id = {user_id}"
```

---

## 2. Authentication

### Mandatory Rules

- [ ] Never hardcode credentials
- [ ] Use environment variables for secrets
- [ ] Implement account lockout (5 failed attempts = 15 min lock)
- [ ] Enforce password complexity (min 12 chars)
- [ ] Use secure password hashing (bcrypt, argon2)
- [ ] Implement MFA for sensitive operations
- [ ] Use secure session management

### Code Examples

```python
# ✅ Correct: Secure password handling
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ❌ Wrong: Hardcoded credentials
API_KEY = "sk-1234567890abcdef"  # NEVER
```

---

## 3. Authorization

### Mandatory Rules

- [ ] Implement RBAC (Role-Based Access Control)
- [ ] Deny by default - explicit permission required
- [ ] Check permissions before EVERY resource access
- [ ] Use least privilege principle
- [ ] Validate ownership for user-specific resources
- [ ] Log authorization failures

### Code Examples

```python
# ✅ Correct: Permission check
async def delete_document(doc_id: str, user: User) -> None:
    doc = await get_document(doc_id)
    
    if doc.owner_id != user.id and not user.has_permission('admin'):
        raise AuthorizationError("Not authorized")
    
    await doc.delete()

# ❌ Wrong: Missing authorization check
async def delete_document(doc_id: str) -> None:
    await Document.delete(doc_id)  # Anyone can delete!
```

---

## 4. SQL Injection Prevention

### Mandatory Rules

- [ ] NEVER concatenate strings in SQL queries
- [ ] Use parameterized queries / prepared statements
- [ ] Use ORM when available
- [ ] Validate input before query construction
- [ ] Use least privilege database users

### Code Examples

```python
# ✅ Correct: Parameterized query
async def get_user(user_id: int) -> User:
    return await db.execute(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )

# ❌ Wrong: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"  # DANGER!
```

---

## 5. Command Injection Prevention

### Mandatory Rules

- [ ] NEVER use `eval()` or `exec()` on user input
- [ ] Avoid shell commands when possible
- [ ] If shell required, use strict allowlists
- [ ] Sanitize all shell metacharacters
- [ ] Use libraries over system calls

### Code Examples

```python
# ✅ Correct: Library over shell
import shutil
shutil.copy(src, dst)  # Safe

# ❌ Wrong: os.system with user input
os.system(f"cp {src} {dst}")  # DANGER!
```

---

## 6. Secure Error Handling

### Mandatory Rules

- [ ] Use unified error model (see error-model/)
- [ ] Never expose stack traces to users
- [ ] Return generic messages to users
- [ ] Log full details internally
- [ ] Include correlation_id in all errors
- [ ] Map internal errors to safe external codes

### Code Examples

```python
# ✅ Correct: Structured error
raise InternalError(
    message="An error occurred",  # Safe for user
    root_cause=str(e),             # Internal only
    correlation_id=request_id
)

# ❌ Wrong: Exposing internals
raise Exception(f"Database error: {e}, trace: {traceback.format_exc()}")
```

---

## 7. Secure Logging

### Mandatory Rules

- [ ] Use structured JSON logging
- [ ] Never log secrets, passwords, or tokens
- [ ] Never log sensitive personal data
- [ ] Include correlation_id for tracing
- [ ] Use appropriate log levels
- [ ] Rotate logs regularly

### Code Examples

```python
# ✅ Correct: Structured logging
logger.info(
    "User login",
    extra={
        "user_id": user.id,
        "correlation_id": request_id,
        # Don't log: password, token, secret
    }
)

# ❌ Wrong: Logging secrets
logger.info(f"User {username} logged in with token {token}")  # DANGER!
```

---

## 8. Data Protection

### Mandatory Rules

- [ ] Encrypt sensitive data at rest
- [ ] Use TLS 1.3 for data in transit
- [ ] Never commit secrets to version control
- [ ] Use environment variables for secrets
- [ ] Implement proper key management
- [ ] Mask sensitive data in displays

### Code Examples

```python
# ✅ Correct: Environment variables
import os
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ConfigurationError("API_KEY not set")

# ❌ Wrong: Hardcoded secrets
API_KEY = "sk-1234567890"  # NEVER commit this!
```

---

## 9. Dependency Security

### Mandatory Rules

- [ ] Pin exact dependency versions
- [ ] Regularly update dependencies (monthly)
- [ ] Run vulnerability scanners
- [ ] Review dependency changes
- [ ] Use private registry for internal packages
- [ ] Generate SBOM (Software Bill of Materials)

---

## 10. File Upload Security

### Mandatory Rules

- [ ] Validate file type by magic bytes, not extension
- [ ] Limit file size (max 10MB)
- [ ] Store files outside web root
- [ ] Generate random filenames
- [ ] Scan uploads for malware
- [ ] Set proper file permissions (read-only)

---

## Security Checklist

Before deploying:

- [ ] All inputs validated
- [ ] No hardcoded secrets
- [ ] Error messages safe
- [ ] Logs sanitized
- [ ] Dependencies up to date
- [ ] No SQL injection vectors
- [ ] No command injection vectors
- [ ] Proper authentication
- [ ] Proper authorization
- [ ] TLS enabled
