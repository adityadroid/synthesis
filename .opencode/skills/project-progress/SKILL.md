# Project Progress Skill

Displays intuitive project progress by parsing the task tracking board.

## Purpose
Show current project status in a visual, intuitive way without reading raw markdown tables.

## When to Use
- Any time you want to check project status
- When starting a new work session
- When reviewing progress with stakeholders

---

## How It Works

1. **Read** `tasks/TRACKING.md`
2. **Parse** task status by phase section
3. **Calculate** completion per phase
4. **Render** visual progress display

---

## Reading the Tracking File

Find these sections in TRACKING.md:

| Section | Contains |
|---------|----------|
| MVP (v0.1.0) | Tasks 001-009 |
| Phase 1 (v1.0.0) | Tasks 010-040 |
| Phase 2 (v1.1.0) | Tasks 041-066 |
| Phase 3 (v2.0.0) | Tasks 067-084 |
| Technical Features | Tasks 085-101 |

---

## Parsing Rules

For each phase section:
1. Count rows with `completed` → done count
2. Count rows with `in_progress` → in progress count  
3. Count rows with `pending` → remaining count
4. Calculate percentage: `(completed / total) * 100`

---

## Output Format

```text
╔════════════════════════════════════════════╗
║       PROJECT PROGRESS OVERVIEW           ║
╠════════════════════════════════════════════╣
║  MVP (v0.1.0) - Foundation                ║
║  ████████████████████░░░░  9/9  100% ✅   ║
║                                          ║
║  Phase 1 (v1.0.0) - Essential Features    ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░  0/31  0% ⏳    ║
║                                          ║
║  Phase 2 (v1.1.0) - Enhanced Experience   ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░  0/26  0% ⏳    ║
║                                          ║
║  Phase 3 (v2.0.0) - Advanced Features     ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░  0/19  0% ⏳    ║
║                                          ║
║  Technical Features                      ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░  0/17  0% ⏳    ║
╠════════════════════════════════════════════╣
║  Total: 9/102 completed (8.8%)           ║
╚══════════════════════════════════════════╝
```

---

## Quick Reference

| Icon | Meaning |
|------|---------|
| ✅ | Phase complete |
| ⏳ | Phase in progress |
| 🔄 | Some tasks in progress |

### Status Legend

| Status | Count | Description |
|--------|-------|-------------|
| completed | X | Done |
| in_progress | X | Currently working |
| pending | X | Not started |
| cancelled | X | Won't do |