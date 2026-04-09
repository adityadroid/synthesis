# 001: Email/Password Signup

## Phase
MVP (v0.1.0)

## Description
Implement user registration with email and password validation.

## Requirements
- Email format validation
- Password strength requirements (min 8 chars)
- Hash password before storage
- Create user record in database
- Return success/error response

## Acceptance Criteria
- [ ] User can register with valid email and password
- [ ] Invalid email format is rejected
- [ ] Weak passwords are rejected
- [ ] Duplicate email returns appropriate error
- [ ] Password is stored as hash, never plaintext

## Related Files
- `src/models/auth.py` - Pydantic schemas (signup request/response)
- `src/services/auth.py` - Signup logic
- `src/routes/auth.py` - POST /auth/signup endpoint
- `src/db.py` - Database connection

## Dependencies
- None (foundational)
