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

## Dependencies
- 001: Email/Password Signup
