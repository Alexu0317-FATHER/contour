# Extract Output Specification

Defines how `/extract` writes to the Extract Buffer (extract-buffer.md) and reports results to the user.

---

## Write Format

Append to the end of the Extract Buffer:

```markdown
---
## Extract {YYYY-MM-DD HH:MM}
topic: {brief one-sentence summary of the session's main topic}
source: {current workspace directory name}

{all extracted signals, separated by blank lines}
```

> **Workspace detection**: Use the current working directory name (the directory where Claude Code was launched) as the `source` value.

---

## Example Output

```markdown
---
## Extract 2026-02-16 14:30
topic: Discussion of git workflow and AI infrastructure design
source: Life_with_AI

[cognition] difference between git rebase and git merge
  status: partial
  evidence: the user could state that both are used for merging, but had unclear understanding of rebase risk scenarios
  reference: Domain State: not tracked

[cognition] PR submission process
  status: mastered
  evidence: the user instructed "submit this as a PR to the main branch" — correctly used the concept in a practical context
  reference: Domain State: partial

[cognition] environment variable separation
  status: partial
  evidence: the user asked "why do we need to separate env variables?" — basic question suggesting regression
  reference: Domain State: mastered (cognitive regression)

[thinking] validate core logic before considering expansion
  evidence: when discussing whether to do cross-platform adaptation first, the user insisted "don't expand until the core is validated"

[preference] use terminology when explaining technical concepts but attach one sentence of context
  evidence: the user said "use the terms directly, but tell me what it does the first time it appears"
```

---

## Report Format

After extraction, report to the user:

```
Extract complete ({date}):
- Topic: {session topic}
- Source: {workspace}
- Signals: {n} cognition, {m} thinking, {k} preference
- Written to extract-buffer.md
```
