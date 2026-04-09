# 010: Password Reset Flow

## Phase
Phase 1 (v1.0.0)

## Description
Implement email-based password recovery.

## Requirements
- Generate reset token with expiry
- Send email with reset link
- Validate token on reset attempt
- Update password hash

## Acceptance Criteria
- [ ] Reset email sent to registered address
- [ ] Invalid/expired token rejected
- [ ] Password updated successfully
- [ ] Token single-use

## Related Files
- `src/models/auth.py` - Password reset schemas
- `src/services/auth.py` - Reset token generation/validation
- `src/routes/auth.py` - POST /auth/reset endpoints

## Dependencies
- 001: Email/Password Signup
