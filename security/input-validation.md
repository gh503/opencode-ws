# Input Validation Standards

This document defines input validation requirements for AE-OS projects.

## Validation Principles

1. **Fail Fast**: Reject invalid input immediately
2. **Defense in Depth**: Validate at every layer
3. **Fail Securely**: Invalid input should not cause security issues
4. **Allowlists**: Use allowlists over blocklists

## Validation Layers

### Layer 1: Gateway Level

- Rate limiting
- Request size limits
- Content-Type validation
- Basic format checks

### Layer 2: Application Level

- Schema validation (pydantic, zod)
- Type checking
- Range validation
- Format validation (email, URL, etc.)

### Layer 3: Business Logic Level

- Business rule validation
- Cross-field validation
- Database constraint validation

## Validation Patterns

### String Validation

```python
# Length validation
username: str = Field(min_length=3, max_length=50)

# Pattern validation
phone: str = Field(pattern=r'^\+?[1-9]\d{1,14}$')

# Enum validation
status: Literal["active", "inactive", "pending"]
```

### Numeric Validation

```python
# Range validation
age: int = Field(ge=0, le=150)
price: float = Field(ge=0)

# Precision validation
amount: Decimal = Field(max_digits=10, decimal_places=2)
```

### Complex Validation

```python
from pydantic import BaseModel, validator

class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    age: int = Field(ge=13)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('must contain digit')
        return v
```

## Error Messages

All validation errors MUST return:

```json
{
  "error_code": "PY-VAL-001",
  "category": "validation",
  "message": "Invalid input",
  "details": {
    "field": "email",
    "reason": "invalid_format"
  }
}
```

## Testing

- Test valid inputs
- Test boundary conditions
- Test malformed inputs
- Test injection attempts
- Test maximum lengths
