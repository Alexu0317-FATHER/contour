# Domain State File Structure

Defines the structure of domain cognitive state files (e.g., `{user}-coder.md`).

---

## Table Format

**English:**

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

**Chinese:**

```markdown
## 认知状态

| 知识点 | 不了解 | 部分理解 | 已掌握 | 更新 |
|--------|--------|----------|--------|------|
| PR 提交流程 |   |          | ✓      | 2026-02 |
| git rebase vs merge | | ✓  |        | 2026-02 |
| 环境变量分离 | ✓ |          |        | 2026-01 |

## 沟通规则

- 使用术语，但首次出现时补充一句说明
- 假设具备系统思维，不假设具备代码细节
- 直接说"不行"，不说"当然可以"
```

Both formats are valid. Match the language of the existing file when updating rows.

---

## Update Rules

- **Status upgrade** (e.g., unknown → partial): move the ✓ to the higher column, update the date
- **Status regression** (e.g., mastered → unknown): move the ✓ to the lower column, update the date
- **New entry**: add a row with ✓ in the appropriate column and current date
- **Cleanup**: items marked `mastered` for more than 30 days with no further status changes can be removed from Domain State (they're preserved in Domain Log)
- **Preferences**: domain-specific preferences go in the Communication Rules section as bullet points
