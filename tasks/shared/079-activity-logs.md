# 079: Activity Logs

## Phase
Phase 3 (v2.0.0)

## Description
Audit trail of all user and system actions.

## Requirements
- Log all significant actions
- Searchable log viewer
- Export logs
- Retention policy

## Acceptance Criteria
- [ ] All actions logged
- [ ] Admin can view logs
- [ ] Filter by user/action
- [ ] Export capability

## Related Files
- `src/services/logging.py` - Activity logging
- `src/routes/admin.py` - Log viewing endpoints

## Dependencies
- 066: Workspaces and Organizations
