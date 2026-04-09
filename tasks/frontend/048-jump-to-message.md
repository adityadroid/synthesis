# 048: Jump to Message

## Phase
Phase 2 (v1.1.0)

## Description
Navigate directly to a specific message.

## Requirements
- Message index/ID navigation
- Auto-scroll to message
- Highlight destination
- URL with message anchor

## Acceptance Criteria
- [ ] Can jump to specific message
- [ ] Scrolls smoothly to message
- [ ] Message highlighted briefly
- [ ] URL reflects position

## Related Files
- `frontend/src/hooks/useChat.ts` - Jump to message function
- `frontend/src/components/Chat/MessageList.tsx` - Auto-scroll

## Dependencies
- 009: Message Display with Roles
