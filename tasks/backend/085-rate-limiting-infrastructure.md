# 085: Rate Limiting Infrastructure

## Phase
All Phases

## Description
Implement rate limiting to prevent API abuse.

## Requirements
- Token bucket algorithm
- Per-user limits
- Per-IP limits
- 429 responses with retry info

## Acceptance Criteria
- [ ] Limits enforced correctly
- [ ] Returns 429 when exceeded
- [ ] Shows retry-after header
- [ ] Admin can view limits

## Related Files
- `src/services/rate_limit.py` - Rate limiting logic
- `src/main.py` - Middleware registration

## Dependencies
- 005: Protected Routes Middleware
