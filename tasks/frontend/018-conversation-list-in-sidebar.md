# 018: Conversation List in Sidebar

## Phase
Phase 1 (v1.0.0)

## Description
Display all user conversations in sidebar UI.

## Requirements
- GET /conversations endpoint
- Return list sorted by last activity
- Include title, last message preview, timestamp
- Paginated response

## Acceptance Criteria
- [ ] Sidebar shows all user conversations
- [ ] Sorted by most recent activity
- [ ] Title and preview visible
- [ ] Efficient query with pagination

## Related Files
- `frontend/src/api/types.ts` - Conversation type
- `frontend/src/api/client.ts` - GET /conversations
- `frontend/src/components/Chat/Sidebar.tsx` - Conversation list
- `frontend/src/hooks/useConversations.ts` - TanStack Query hook

## Dependencies
- 017: Multiple Conversations
