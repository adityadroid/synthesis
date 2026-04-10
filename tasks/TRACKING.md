# Task Tracking

## How to Update
- **Status**: `pending` → `in_progress` → `completed` | `cancelled`
- **Type**: `be` (backend only) | `fe` (frontend only) | `both` (requires coordination)
- Add comments in the Notes column for blockers, notes, or progress

---

## MVP (v0.1.0) - Foundation

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 001 | Email/Password Signup | both | completed | Implemented with bcrypt hashing |
| 002 | Email/Password Login | both | completed | JWT tokens on successful login |
| 003 | JWT Session Management | be | completed | Access + refresh token with expiry |
| 004 | Logout | both | completed | Client-side token cleanup |
| 005 | Protected Routes Middleware | be | completed | HTTPBearer + user validation |
| 006 | Send Message to LLM | be | completed | OpenAI integration (demo mode without API key) |
| 007 | Streaming Responses via SSE | both | completed | Server-Sent Events endpoint |
| 008 | Single Conversation Mode | both | completed | Auto-create conversation on first message |
| 009 | Message Display with Roles | fe | completed | User/assistant message components |

---

## Phase 1 (v1.0.0) - Essential Features

### Auth & User Management

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 010 | Password Reset Flow | both | pending | |
| 011 | Email Verification | both | pending | |
| 012 | User Profile Management | both | pending | |
| 013 | Change Password | both | pending | |
| 014 | Delete Account | both | pending | |
| 015 | OAuth: Google Sign-In | both | pending | |
| 016 | OAuth: GitHub Sign-In | both | pending | |

### Conversation Management

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 017 | Multiple Conversations | both | pending | |
| 018 | Conversation List in Sidebar | fe | pending | |
| 019 | Rename Conversation | both | pending | |
| 020 | Delete Conversation | both | pending | |
| 021 | Clear Conversation | both | pending | |
| 022 | Switch Between Conversations | fe | pending | |
| 023 | Auto-save Messages | be | pending | |
| 024 | Conversation Search | both | pending | |

### Multi-Model Support

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 025 | OpenAI Integration | be | pending | |
| 026 | Anthropic Integration | be | pending | |
| 027 | Model Selector Dropdown | fe | pending | |
| 028 | Per-Conversation Model Memory | both | pending | |
| 029 | Model Info Display in UI | fe | pending | |

### Chat Experience

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 030 | Markdown Rendering | fe | pending | |
| 031 | Code Syntax Highlighting | fe | pending | |
| 032 | Copy Message Button | fe | pending | |
| 033 | Copy Individual Code Blocks | fe | pending | |
| 034 | Message Timestamps | fe | pending | |
| 035 | Typing Indicator | fe | pending | |
| 036 | Retry Failed Messages | fe | pending | |
| 037 | Regenerate AI Response | fe | pending | |

---

## Phase 2 (v1.1.0) - Enhanced Experience

### Advanced Chat Features

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 038 | Edit User Messages | both | pending | |
| 039 | Message Reactions | fe | pending | |
| 040 | Conversation Export (Markdown) | both | pending | |
| 041 | Conversation Export (JSON) | both | pending | |
| 042 | Conversation Export (PDF) | both | pending | |
| 043 | Import Conversation | both | pending | |
| 044 | Shared Links | both | pending | |
| 045 | Keyboard Shortcuts | fe | pending | |

### Search & Navigation

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 046 | Global Message Search | both | pending | |
| 047 | Search Within Conversation | fe | pending | |
| 048 | Jump to Message | fe | pending | |
| 049 | Filter by Date | fe | pending | |
| 050 | Filter by Model | fe | pending | |

### Customization

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 051 | Light/Dark Theme | fe | pending | |
| 052 | Theme Settings (Accent Colors) | fe | pending | |
| 053 | Adjustable Font Size | fe | pending | |
| 054 | Token Counter | both | pending | |
| 055 | Cost Tracker | both | pending | |
| 056 | Usage Dashboard | both | pending | |

### AI Configuration

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 057 | Custom System Prompt | both | pending | |
| 058 | Temperature Slider | fe | pending | |
| 059 | Max Tokens Setting | fe | pending | |
| 060 | Top-p Setting | fe | pending | |
| 061 | Presence Penalty | fe | pending | |
| 062 | Save AI Configuration Presets | both | pending | |

### Local Model Support

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 063 | Ollama Integration | be | pending | |
| 064 | LM Studio Integration | be | pending | |
| 065 | Custom API Endpoint | both | pending | |

---

## Phase 3 (v2.0.0) - Advanced Features

### Collaboration

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 066 | Workspaces and Organizations | both | pending | |
| 067 | Shared Conversations | both | pending | |
| 068 | User Roles (Admin/Member/Viewer) | both | pending | |
| 069 | Invite Team Members | both | pending | |

### Advanced AI Features

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 070 | Image Uploads (Vision Support) | both | pending | |
| 071 | File Attachments | both | pending | |
| 072 | Voice Input (Speech-to-Text) | both | pending | |
| 073 | Conversation Templates | both | pending | |
| 074 | Prompt Library | both | pending | |
| 075 | Function Calling (Tool Use) | both | pending | |
| 076 | Web Search Integration | both | pending | |

### Analytics & Admin

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 077 | Usage Analytics Dashboard | both | pending | |
| 078 | Cost Reports | both | pending | |
| 079 | Activity Logs | be | pending | |
| 080 | Rate Limit Management | be | pending | |
| 081 | API Key Management | both | pending | |

### Enterprise Features

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 082 | SSO/SAML Support | both | pending | |
| 083 | Data Retention Policies | be | pending | |
| 084 | Custom Model Support | both | pending | |

---

## Technical Features (All Phases)

### Performance & Reliability

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 085 | Rate Limiting Infrastructure | be | pending | |
| 086 | Request Caching (Redis) | be | pending | |
| 087 | Database Connection Pooling | be | pending | |
| 088 | Error Handling & Graceful Degradation | be | pending | |
| 089 | Retry Logic | be | pending | |
| 090 | Fallback Provider Switching | be | pending | |
| 091 | Health Check Endpoints | be | pending | |

### Security

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 092 | Input Sanitization | be | pending | |
| 093 | SQL Injection Prevention | be | pending | |
| 094 | CORS Configuration | be | pending | |
| 095 | Content Moderation | be | pending | |
| 096 | Secure WebSocket (WSS) | be | pending | |
| 097 | Encrypted LLM API Key Storage | be | pending | |

### Observability

| # | Task | Type | Status | Notes |
|---|------|------|--------|-------|
| 098 | Structured Logging | be | pending | |
| 099 | OpenTelemetry Integration | be | pending | |
| 100 | Prometheus Metrics | be | pending | |
| 101 | Sentry Error Reporting | be | pending | |

---

## Testing Standards

### Backend Tests

| Level | Coverage Target | Tools |
|-------|----------------|-------|
| Unit | Business logic in services | pytest, pytest-asyncio |
| API | All API endpoints | httpx, pytest |
| E2E | Critical flows only | pytest |

### Frontend Tests

| Level | Coverage Target | Tools |
|-------|----------------|-------|
| Unit | Components, hooks, utils | Vitest, React Testing Library |
| Integration | Key user flows | Vitest + MSW |
| E2E | Happy path | Playwright |

---

## Summary

| Category | Total | BE | FE | Both |
|----------|-------|----|----|------|
| MVP | 9 | 2 | 2 | 5 |
| Phase 1 | 31 | 4 | 15 | 12 |
| Phase 2 | 26 | 0 | 11 | 15 |
| Phase 3 | 19 | 3 | 0 | 16 |
| Technical | 17 | 17 | 0 | 0 |
| **Total** | **102** | **26** | **28** | **48** |

| Status | Count |
|--------|-------|
| pending | 93 |
| in_progress | 0 |
| completed | 9 |
| cancelled | 0 |