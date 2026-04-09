# 017: Multiple Conversations

## Phase
Phase 1 (v1.0.0)

## Description
Enable users to create and manage unlimited chat threads.

## Requirements
- Create new conversation endpoint
- Associate messages with conversation
- Each conversation has independent history
- Conversations belong to user

## Acceptance Criteria
- [ ] Can create new conversation
- [ ] Messages grouped by conversation
- [ ] Conversations are user-scoped
- [ ] Default conversation created if none

## Related Files
- `src/models/conversation.py` - Conversation schema
- `src/services/conversation.py` - Create conversation logic
- `src/routes/conversations.py` - POST /conversations endpoint

## Dependencies
- 008: Single Conversation Mode
