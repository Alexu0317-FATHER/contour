# CLAUDE.md Injection Template

This file is used by `/contour:setup` at Step 8. It defines two things to write:
1. A short entry block injected into `~/.claude/CLAUDE.md`
2. A rules file written to `~/.claude/rules/contour-monitoring.md`

**Placeholder substitution (entry block only):**
- `{AI_INFRA_DIR}` → resolved absolute path to data directory (e.g., `/Users/alex/.claude/contour`)
- `{user}` → username configured at setup (e.g., `alex`)
- `{domain}` → domain name configured at setup (e.g., `coder`, `writer`, `researcher`)

The rules file (`contour-monitoring-rules.md`) has no placeholders — copy verbatim.

For multi-domain users: inject one entry block per domain (substituting `{domain}`), but write the rules file only once.

---

## Entry Block (inject into CLAUDE.md)

```
<!-- Contour -->

## Contour Cognitive Tracking System

**Load at session start:**
- Core Profile: `{AI_INFRA_DIR}/{user}-core.md` — apply as the user's communication profile
- Domain State: `{AI_INFRA_DIR}/{user}-{domain}.md` — use as cognitive baseline for this session
- If a referenced file does not exist, alert the user: "Contour files not found at {AI_INFRA_DIR}. Run /contour:setup to initialize." Then continue the session without cognitive tracking.

**Monitoring rules: `~/.claude/rules/contour-monitoring.md`**

**CRITICAL INSTRUCTION — Execute Before Every Response Completes:**

After generating your response content, you MUST execute the Self-Check Protocol in `~/.claude/rules/contour-monitoring.md`:
1. Review this conversation turn for cognitive signals (patterns defined in the rules file)
2. If a signal matches, use Edit to update Domain State immediately — before finishing your turn
3. Do not announce the update; file modifications will be visible in terminal, stay in user's workflow
4. If no signal detected, end normally

This self-check is not optional. Build it into every response generation cycle.

<!-- End Contour -->
```

---

## Rules File (write to `~/.claude/rules/contour-monitoring.md`)

See `references/contour-monitoring-rules.md` for the exact content to write.

Idempotent: if the file already exists, overwrite it (rules may have been updated).
