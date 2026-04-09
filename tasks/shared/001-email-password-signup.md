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
- `src/aichat/domain/entities/user.py`
- `src/aichat/application/use_cases/auth/signup.py`
- `src/aichat/infrastructure/repositories/user_repository.py`
- `src/aichat/presentation/api/v1/auth.py`

## Dependencies
- None (foundational)
