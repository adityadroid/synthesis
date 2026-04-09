# 097: Encrypted LLM API Key Storage

## Phase
All Phases

## Description
Securely store user-provided LLM API keys.

## Requirements
- Encryption at rest
- User-provided keys only
- Audit access
- Key rotation support

## Acceptance Criteria
- [ ] Keys encrypted
- [ ] Only user can access
- [ ] Access logged
- [ ] Can rotate keys

## Related Files
- `src/services/crypto.py` - Key encryption
- `src/config.py` - Encryption key

## Dependencies
- 025: OpenAI Integration
