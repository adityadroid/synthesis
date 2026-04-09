# 067: Shared Conversations

## Phase
Phase 3 (v2.0.0)

## Description
Share conversations within team workspace.

## Requirements
- Share to workspace
- Access control per conversation
- Team conversation list
- Activity indicators

## Acceptance Criteria
- [ ] Can share within workspace
- [ ] Team members see shared chats
- [ ] Owner controls access
- [ ] Notification on share

## Related Files
- `src/services/conversation.py` - Share logic
- `src/routes/conversations.py` - POST /conversations/:id/share endpoint

## Dependencies
- 066: Workspaces and Organizations
