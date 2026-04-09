# 015: OAuth - Google Sign In

## Phase
Phase 1 (v1.0.0)

## Description
Add Google OAuth authentication option.

## Requirements
- OAuth 2.0 flow with Google
- Create/link account on first login
- Generate JWT on successful OAuth
- Store OAuth provider info

## Acceptance Criteria
- [ ] Redirect to Google OAuth
- [ ] Callback creates/links account
- [ ] JWT issued on success
- [ ] Existing email accounts can link Google

## Dependencies
- 002: Email/Password Login
