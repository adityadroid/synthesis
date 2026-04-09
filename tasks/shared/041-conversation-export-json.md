# 041: Conversation Export - JSON

## Phase
Phase 2 (v1.1.0)

## Description
Export conversations as JSON for backup/import.

## Requirements
- JSON format with full metadata
- Include messages, timestamps, model info
- Schema version for compatibility
- Download as .json file

## Acceptance Criteria
- [ ] Export generates valid JSON
- [ ] All metadata preserved
- [ ] Can be re-imported
- [ ] Schema documented

## Related Files
- `src/services/conversation.py` - Export logic
- `src/routes/conversations.py` - GET /conversations/:id/export endpoint

## Dependencies
- 040: Conversation Export - Markdown
