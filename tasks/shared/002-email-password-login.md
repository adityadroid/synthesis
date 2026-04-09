# 002: Email/Password Login

## Phase
MVP (v0.1.0)

## Description
Implement secure user authentication with email and password.

## Requirements
- Verify credentials against stored hash
- Generate JWT access token on success
- Return user info with token
- Handle invalid credentials gracefully

## Acceptance Criteria
- [ ] Valid credentials return JWT token
- [ ] Invalid email returns 404
- [ ] Invalid password returns 401
- [ ] Token contains user_id and expiration

## Related Files
- `src/models/auth.py` - Pydantic schemas (login request/response)
- `src/services/auth.py` - Login logic
- `src/routes/auth.py` - POST /auth/login endpoint
- `src/db.py` - Database connection

## Dependencies
- 001: Email/Password Signup
