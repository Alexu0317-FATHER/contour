---
name: sync
description: "Read extract-buffer.md, distribute signals to domain B/C files, deduplicate, then clear buffer. Must run in a NEW dedicated session."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob"
---

# /sync

Read `$AI_INFRA_DIR/extract-buffer.md`, distribute each signal to the appropriate target files, then clear the buffer.

> **Path configuration**: `$AI_INFRA_DIR` must be set before use. This is the directory where all AI infrastructure files are stored.
> - Default recommended path: `~/.claude/contour/`
> - Set via environment variable, or replace this placeholder with your absolute path.

---

## Reference Files

Before executing, read the following reference files for format specifications:
- `references/b-structure.md` — B file table format and update rules
- `references/c-structure.md` — C file entry format and examples

---

## File References

| Label | File | Role | Access |
|-------|------|------|--------|
| A | `extract-buffer.md` | Temporary buffer: read then clear | Read + Clear |
| B | `{user}-coder.md` | Current cognitive state for the coder domain | Read + Write |
| C | `{user}-coder-log.md` | Append-only audit log for human review | Append only (never read) |
| D | `{user}-core.md` | Personality-level traits, thinking patterns, core preferences | Read only (never write) |

> **MVP scope:** Single domain only. The routing principle below applies regardless: route signals by content domain, not by the `source` field (source indicates where the signal was captured, not its domain).
>
> *Multi-domain support (additional B/C file pairs) is a Phase 2 extension.*

---

## Constraints

- **Only read** A, B, D
- **Only append to** C — never read C. C is an append-only audit log for human review. Reading it would introduce unnecessary token cost and context noise with no benefit to signal processing.
- **Never write to** D — /sync does not modify core.md. If a signal may warrant a D update, log a `[core-candidate]` entry to C for the user to review manually.
- **Do not re-scan** conversation history — all signals come from A
- **Do not invent** signals not present in A
- **Preserve** all existing content in B — only append or update specific entries

---

## Pre-flight Check

Before processing, verify the state of A:

- **A file does not exist** → Inform the user: "extract-buffer.md not found. Check your path configuration." Stop.
- **A file exists but is empty** → Inform the user: "Buffer is empty, nothing to sync." Stop.
- **A file exists with content** → Proceed.

---

## Step-by-Step Execution

### Step 1: Read Files

Read the reference files listed above. Read A in full. Read B in full. Read D in full (for deduplication and comparison only — never write to D).

Do **not** read C.

### Step 2: Process Each Signal

For every signal in A, determine its type and execute the corresponding routing rule. Carry forward the `topic` and `source` fields from each extract block in A for writing to C.

#### [cognition] → B + C

1. **Check B for an existing entry on the same knowledge point.**
   - Same knowledge point = same concept/tool/process, regardless of wording differences (e.g., "git rebase vs merge" and "difference between rebase and merge" are the same)
   - If an existing entry has **the same cognitive status**, this signal is a duplicate → skip B update, still log to C
   - If an existing entry has **a lower cognitive status** (e.g., unknown → partial, partial → mastered), move the ✓ in B to the higher column per `b-structure.md`, update the date → log the upgrade to C
   - If an existing entry has **a higher cognitive status** (e.g., mastered → unknown), this is a **cognitive regression** → move the ✓ in B to the lower column, update the date → log the regression to C
   - If **no existing entry**, add a new row to B → log to C

2. **Append to C** using the cognition entry format in `c-structure.md`.

#### [thinking] → C + maybe [core-candidate]

1. **Always append to C** using the thinking entry format in `c-structure.md`.

2. **Check D for relevance**:
   - If this thinking pattern is **not represented in D** and appears to be a persistent trait → also append a `[core-candidate]` to C
   - If this thinking pattern is **already captured in D** → no further action
   - If this thinking pattern **contradicts** something in D → also append a `[core-candidate]` to C with a contradiction note

#### [preference] → B and/or [core-candidate]

1. **Determine scope**:
   - If the preference is **domain-specific** (e.g., "when explaining code, use terminology") → target B's communication rules section
   - If the preference is **cross-domain** (e.g., "don't use metaphors", "be direct") → do not write to D; instead append a `[core-candidate]` to C
   - If ambiguous, default to B (narrower scope is safer)

2. **For B-targeted preferences, check for existing similar preferences in B**:
   - If a semantically equivalent preference already exists → skip (duplicate)
   - If the new preference **contradicts** an existing one → replace the old one with the new one, log the change to C
   - If no existing equivalent → add to B

### Step 3: Clean Up B

After all signals are processed:

- If B has grown noticeably, review for entries that can be compressed or consolidated
- Items marked `mastered` for more than 30 days with no further status changes can be removed from B (they're preserved in C)
- Report to the user if any cleanup was performed

### Step 4: Clear A

After all signals have been distributed successfully, clear the content of A (keep the file, empty its content).

### Step 5: Report

```
Sync complete ({date}):
- Processed: {n} signals from {m} extract blocks
- B updated: {list of changes, or "no changes"}
- C appended: {number of entries}
- Core candidates logged: {number, or "none"}
- Duplicates skipped: {number}
- Buffer cleared
```

---

## Deduplication Rules

Deduplication is **semantic, not lexical**. Two entries refer to the same thing if:

1. They describe the **same concept, tool, or process** (e.g., "environment variables" and "env vars" and ".env files" are the same if they refer to the same knowledge point)
2. They describe the **same thinking pattern** (e.g., "validate before expanding" and "don't expand until the core is proven" are the same pattern)
3. They describe the **same preference** (e.g., "use terminology" and "don't dumb down technical terms" express the same preference)

When in doubt, **keep both entries** — false deduplication (losing a real signal) is worse than mild redundancy (which can be cleaned up manually).

---

## Edge Cases

- **Multiple extract blocks in A**: Process them chronologically. Later signals may override earlier ones for the same knowledge point.
- **Signals from different workspaces**: Route by content domain, not by source workspace. A coding cognition signal captured in `Content_Creator` still goes to the coder domain files. The `source` field is recorded in C for traceability, not for routing.
- **Conflicting signals in the same sync**: If two signals in A contradict each other (e.g., one says "unknown", another says "mastered" for the same knowledge point), use the **later** one (it reflects more recent state).
- **Missing target files**: If a domain file (B/C) doesn't exist yet, create it with the appropriate structure per the reference files before writing.
