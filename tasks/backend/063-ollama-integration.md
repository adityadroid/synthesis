# 063: Ollama Integration

## Phase
Phase 2 (v1.1.0)

## Description
Connect to local Ollama for self-hosted models.

## Requirements
- Ollama API client
- Auto-detect local models
- Streaming support
- Connection status indicator

## Acceptance Criteria
- [ ] Connects to local Ollama
- [ ] Lists available models
- [ ] Streams responses
- [ ] Shows connection status

## Related Files
- `src/services/llm.py` - Ollama client implementation
- `src/config.py` - OLLAMA_BASE_URL

## Dependencies
- 025: OpenAI Integration
