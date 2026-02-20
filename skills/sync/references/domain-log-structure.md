# Domain Log File Structure

Defines the structure of domain audit log files (e.g., `{user}-coder-log.md`). Domain Log is append-only and never read by /sync.

---

## Entry Formats

Entries are grouped under `/sync` execution date headers.

### [cognition] Entry

```markdown
[cognition] {knowledge point}: {old status} → {new status}
  evidence: {from the signal}
  source: {workspace} | {topic}
```

- First appearance: `new → {status}`
- Upgrade: `{old status} → {new status}`
- Regression: `{old status} → {new status} (regression)`

### [thinking] Entry

```markdown
[thinking] {description}
  evidence: {from the signal}
  source: {workspace} | {topic}
```

### [core-candidate] Entry

Appended when a thinking pattern is not represented in Core Profile, contradicts Core Profile, or when a preference is cross-domain:

```markdown
[core-candidate] {description} — may warrant core.md update if pattern persists
```

```markdown
[core-candidate] contradicts Core Profile: "{existing entry}" — new signal: {description}
```

---

## Example

```markdown
## 2026-02-16 /sync

[cognition] PR submission process: partial → mastered
  evidence: user instructed "submit this as a PR to the main branch"
  source: Life_with_AI | Discussion of git workflow and AI infrastructure design

[cognition] environment variable separation: mastered → partial (regression)
  evidence: user asked "why do we need to separate env variables?"
  source: Content_Creator | Configuring video auto-publish script

[thinking] validate core logic before considering expansion
  evidence: when discussing cross-platform adaptation, insisted "don't expand until the core is validated"
  source: Life_with_AI | Discussion of git workflow and AI infrastructure design

[core-candidate] validate core logic before considering expansion — may warrant core.md update if pattern persists
```
