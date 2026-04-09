# 020: Delete Conversation

## Phase
Phase 1 (v1.0.0)

## Description
Permanently remove a conversation and all its messages.

## Requirements
- DELETE /conversations/:id endpoint
- Remove conversation and all messages
- Return confirmation
- Only owner can delete

## Acceptance Criteria
- [ ] Conversation deleted from sidebar
- [ ] All messages removed
- [ ] Cannot recover after deletion
- [ ] Returns 404 if not found

## Related Files
- `src/services/conversation.py` - Delete logic
- `src/routes/conversations.py` - DELETE /conversations/:id endpoint

## Dependencies
- 017: Multiple Conversations
