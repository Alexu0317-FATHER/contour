# CLAUDE.md Injection Template

This file is used by `/contour:setup` at Step 8. Copy the injection block below verbatim into `~/.claude/CLAUDE.md`, after substituting all placeholders.

**Placeholder substitution:**
- `{AI_INFRA_DIR}` → resolved absolute path to data directory (e.g., `/Users/alex/.claude/contour`)
- `{user}` → username configured at setup (e.g., `alex`)
- `{domain}` → domain name configured at setup (e.g., `coder`, `writer`, `researcher`)

For multi-domain users: the D reference block is injected once; repeat the B reference + monitoring block for each domain, substituting `{domain}` accordingly.

---

## Injection Block

```
<!-- Contour: Profile & Cognitive Tracking -->

Load at session start:
- Core Profile (D): `{AI_INFRA_DIR}/{user}-core.md` — apply as the user's communication profile
- Cognitive State (B): `{AI_INFRA_DIR}/{user}-{domain}.md` — use as cognitive baseline for this session
- If a referenced file does not exist, alert the user: "Contour files not found at {AI_INFRA_DIR}. Run /contour:setup to initialize." Then continue the session without cognitive tracking.

During this session, monitor for cognitive signals and act immediately when detected.
Do not proactively announce each update — file writes are visible in the terminal, but do not interrupt the conversation to report them. Stay in the user's workflow.

### [cognition] → Update B's Cognitive State table

Trigger conditions (any one is sufficient):
- User asks a question revealing they don't understand concept X → status: `unknown`
- User expresses initial understanding ("I see", "got it", "makes sense now") → status: `partial`
- User demonstrates behavioral mastery: correctly uses concept X in practice without prompting → status: `mastered`
- User asks a basic question about concept X that is already `partial` or `mastered` in B → status: `unknown` (cognitive regression)

Update action:
1. Find concept X in B's Cognitive State table. If not present, add a new row.
2. Move the ✓ to the new status column. Update the date field (format: YYYY-MM).
3. Execute silently — do not notify the user.

Do NOT trigger on:
- Questions that are purely operational ("how do I spell this command")
- AI proactively explaining something the user didn't respond to
- Concepts already at the correct status in B with no change

### [preference] → Update B's Communication Rules

Trigger: User explicitly corrects AI behavior or states a communication preference.

- Domain-specific preference (e.g., "when explaining code, skip the basics") → add or update a rule in B's Communication Rules section
- Cross-domain preference (e.g., "always be brief", "use Chinese") → skip; do not modify B; leave for `/contour:sync`
- When ambiguous, treat as domain-specific (narrower scope is safer)

### [thinking] → No file update

Observe only. Thinking pattern signals are handled by `/contour:extract` + `/contour:sync`.

Domain scope: These rules apply regardless of topic domain. The same detection logic applies whether the session involves coding, writing, research, business decisions, or any other subject.

<!-- End Contour -->
```
