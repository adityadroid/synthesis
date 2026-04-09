# 095: Content Moderation

## Phase
All Phases

## Description
Filter inappropriate content in messages.

## Requirements
- Content filtering API
- Configurable filter levels
- User reports
- Admin review queue

## Acceptance Criteria
- [ ] Inappropriate content flagged
- [ ] User warned/blocked
- [ ] Reports reviewed
- [ ] Filter level configurable

## Related Files
- `src/services/moderation.py` - Content filtering
- `src/routes/chat.py` - Moderation middleware

## Dependencies
- 006: Send Message to LLM
