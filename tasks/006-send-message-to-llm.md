# 006: Send Message to LLM

## Phase
MVP (v0.1.0)

## Description
Implement message sending to LLM provider with context.

## Requirements
- Accept message content and conversation_id
- Build context from conversation history
- Send to configured LLM provider
- Store user message in database
- Return LLM response

## Acceptance Criteria
- [ ] Message stored with user role
- [ ] Context includes previous messages
- [ ] LLM response is stored
- [ ] Error handling for API failures

## Dependencies
- 005: Protected Routes Middleware
