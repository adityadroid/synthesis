# 069: Invite Team Members

## Phase
Phase 3 (v2.0.0)

## Description
Invite users to workspace via email or link.

## Requirements
- Email invite flow
- Shareable invite link
- Pending invite management
- Role selection on invite

## Acceptance Criteria
- [ ] Can invite by email
- [ ] Can generate invite link
- [ ] Pending invites visible
- [ ] Can revoke invites

## Related Files
- `src/services/workspace.py` - Invite logic
- `src/routes/workspaces.py` - Invite endpoints
- `src/services/email.py` - Invite email

## Dependencies
- 066: Workspaces and Organizations
