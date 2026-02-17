# B File Structure

Defines the structure of domain cognitive state files (e.g., `{user}-coder.md`).

---

## Table Format

```markdown
## Cognitive State

| Knowledge Point | Unknown | Partial | Mastered | Updated |
|-----------------|---------|---------|----------|---------|
| PR submission   |         |         | ✓        | 2026-02 |
| git rebase vs merge |     | ✓       |          | 2026-02 |
| env variable separation | ✓ |       |          | 2026-01 |

## Communication Rules

- Use terminology, but explain context on first appearance
- Assume systems-thinking ability, don't assume code-level details
- Say "no" directly, don't say "of course"
```

---

## Update Rules

- **Status upgrade** (e.g., unknown → partial): move the ✓ to the higher column, update the date
- **Status regression** (e.g., mastered → unknown): move the ✓ to the lower column, update the date
- **New entry**: add a row with ✓ in the appropriate column and current date
- **Cleanup**: items marked `mastered` for more than 30 days with no further status changes can be removed from B (they're preserved in C)
- **Preferences**: domain-specific preferences go in the Communication Rules section as bullet points
