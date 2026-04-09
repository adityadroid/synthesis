# 013: Change Password

## Phase
Phase 1 (v1.0.0)

## Description
Allow users to update their password from settings.

## Requirements
- Require current password verification
- Validate new password strength
- Update password hash
- Invalidate existing sessions (optional)

## Acceptance Criteria
- [ ] Current password verified
- [ ] New password meets requirements
- [ ] Password updated successfully
- [ ] Error on incorrect current password

## Related Files
- `src/models/user.py` - Password change schema
- `src/services/auth.py` - Password update logic
- `src/routes/auth.py` - POST /auth/change-password endpoint

## Dependencies
- 001: Email/Password Signup
- 012: User Profile Management
