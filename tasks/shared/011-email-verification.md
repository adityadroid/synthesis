# 011: Email Verification

## Phase
Phase 1 (v1.0.0)

## Description
Verify user email on signup via confirmation link.

## Requirements
- Generate verification token
- Send verification email
- Mark email as verified on confirmation
- Block certain features until verified

## Acceptance Criteria
- [ ] Verification email sent on signup
- [ ] Valid token marks email verified
- [ ] Unverified users can login
- [ ] Token expires after 24 hours

## Related Files
- `src/models/user.py` - User schema with email_verified flag
- `src/services/auth.py` - Token generation/email sending
- `src/routes/auth.py` - GET /auth/verify endpoint

## Dependencies
- 001: Email/Password Signup
