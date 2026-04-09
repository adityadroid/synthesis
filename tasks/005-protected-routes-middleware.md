# 005: Protected Routes Middleware

## Phase
MVP (v0.1.0)

## Description
Add authentication middleware to protect API endpoints.

## Requirements
- Extract JWT from Authorization header
- Validate token signature and expiry
- Attach user context to request
- Return 401 for invalid/missing token

## Acceptance Criteria
- [ ] Protected endpoints reject unauthenticated requests
- [ ] Valid token allows access
- [ ] User context available in handlers
- [ ] 401 returned with appropriate message

## Dependencies
- 003: JWT Session Management
