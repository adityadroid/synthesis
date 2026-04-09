# 068: User Roles - Admin, Member, Viewer

## Phase
Phase 3 (v2.0.0)

## Description
Implement role-based access control in workspaces.

## Requirements
- Admin: full control
- Member: read/write conversations
- Viewer: read-only access
- Role assignment by admin

## Acceptance Criteria
- [ ] Three distinct roles
- [ ] Permissions enforced
- [ ] Admins can change roles
- [ ] UI reflects permissions

## Related Files
- `src/models/workspace.py` - Role enum and permissions
- `src/services/auth.py` - Role-based access checks
- `src/routes/workspaces.py` - Role management endpoints

## Dependencies
- 066: Workspaces and Organizations
