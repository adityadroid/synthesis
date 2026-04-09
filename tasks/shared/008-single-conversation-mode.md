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

## Dependencies
- 006: Send Message to LLM
