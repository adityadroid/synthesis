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

## Dependencies
- 001: Email/Password Signup
