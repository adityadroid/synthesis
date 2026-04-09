# 008: Single Conversation Mode

## Phase
MVP (v0.1.0)

## Description
Implement single active chat thread per session.

## Requirements
- Create default conversation on first message
- Link all messages to single conversation
- Return conversation_id in responses

## Acceptance Criteria
- [ ] First message creates conversation
- [ ] Subsequent messages append to same conversation
- [ ] Conversation persists across requests

## Related Files
- `src/models/conversation.py` - Conversation schema
- `src/services/conversation.py` - Create/get conversation logic
- `src/routes/chat.py` - Conversation handling in chat endpoint

## Dependencies
- 006: Send Message to LLM
