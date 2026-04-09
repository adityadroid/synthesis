# 030: Markdown Rendering

## Phase
Phase 1 (v1.0.0)

## Description
Render markdown content in messages (code blocks, lists, headers).

## Requirements
- Support CommonMark spec
- Render headers (h1-h6)
- Render lists (ordered/unordered)
- Render links and emphasis
- Sanitize HTML for security

## Acceptance Criteria
- [ ] Markdown renders correctly
- [ ] No XSS vulnerabilities
- [ ] Consistent with standard renderers
- [ ] Code blocks render with language

## Dependencies
- 009: Message Display with Roles
