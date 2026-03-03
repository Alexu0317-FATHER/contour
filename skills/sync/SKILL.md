---
name: sync
description: "Read extract-buffer.md, distribute signals to Domain State, surface thinking patterns and core candidates in report, then clear buffer. Must run in a NEW dedicated session."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob"
---

# /sync

Read `$AI_INFRA_DIR/extract-buffer.md`, distribute each signal to the appropriate target files, then clear the buffer.

> **Path configuration**: `$AI_INFRA_DIR` must be set before use. This is the directory where all Contour data files are stored.
> - Default recommended path: `~/.claude/contour/`
> - Set via environment variable, or replace this placeholder with your absolute path.

---

## Reference Files

Before executing, read the following reference files for format specifications:
- `references/domain-state-structure.md` — Domain State table format and update rules

---

## File References

| File | Term | Role | Access |
|------|------|------|--------|
| `extract-buffer.md` | Extract Buffer | Temporary buffer: read then clear | Read + Clear |
| `{user}-{domain}.md` | Domain State | Current cognitive state for the domain | Read + Write |
| `{user}-core.md` | Core Profile | Personality-level traits, thinking patterns, core preferences | Read only (never write) |

> **MVP scope:** Single domain only. The routing principle below applies regardless: route signals by content domain, not by the `source` field (source indicates where the signal was captured, not its domain).
>
> *Multi-domain support (additional Domain State file pairs) is a Phase 2 extension.*

---

## Constraints

- **Only read** Extract Buffer, Domain State, Core Profile
- **Never write to** Core Profile — /sync does not modify core.md. If a signal may warrant a Core Profile update, surface it as a `[core-candidate]` in the sync report for the user to decide immediately.
- **Do not re-scan** conversation history — all signals come from Extract Buffer
- **Do not invent** signals not present in Extract Buffer
- **Preserve** all existing content in Domain State — only append or update specific entries

---

## Pre-flight Check

Before processing, verify the state of Extract Buffer:

- **Extract Buffer file does not exist** → Inform the user: "extract-buffer.md not found. Check your path configuration." Stop.
- **Extract Buffer file exists but is empty** → Inform the user: "Buffer is empty, nothing to sync." Stop.
- **Extract Buffer file exists with content** → Proceed.

---

## Step-by-Step Execution

### Step 1: Read Files

Read the reference files listed above. Read Extract Buffer in full. Read Domain State in full. Read Core Profile in full (for deduplication and comparison only — never write to Core Profile).

### Step 2: Process Each Signal

For every signal in Extract Buffer, determine its type and execute the corresponding routing rule.

#### [cognition] → Domain State

1. **Check Domain State for an existing entry on the same knowledge point.**
   - Same knowledge point = same concept/tool/process, regardless of wording differences (e.g., "git rebase vs merge" and "difference between rebase and merge" are the same)
   - If an existing entry has **the same cognitive status**, this signal is a duplicate → skip Domain State update, record as duplicate in report
   - If an existing entry has **a lower cognitive status** (e.g., partial → mastered), move the ✓ in Domain State to the higher column per `domain-state-structure.md`, update the date
   - If an existing entry has **a higher cognitive status** (e.g., mastered → partial), this is a **cognitive regression** → move the ✓ in Domain State to the lower column, update the date
   - If **no existing entry**, add a new row to Domain State

#### [thinking] → Sync report only

1. **Include in the sync report** under "Thinking patterns observed" — do not write to any file.

2. **Check Core Profile for relevance**:
   - If this thinking pattern is **not represented in Core Profile** and appears to be a persistent trait → surface as `[core-candidate]` in the sync report
   - If this thinking pattern is **already captured in Core Profile** → note as "already tracked" in report
   - If this thinking pattern **contradicts** something in Core Profile → surface as `[core-candidate]` in report with a contradiction note

#### [preference] → Domain State and/or [core-candidate]

1. **Determine scope**:
   - If the preference is **domain-specific** (e.g., "when explaining code, use terminology") → target Domain State's communication rules section
   - If the preference is **cross-domain** (e.g., "don't use metaphors", "be direct") → do not write to Core Profile; instead surface as `[core-candidate]` in the sync report
   - If ambiguous, default to Domain State (narrower scope is safer)

2. **For Domain State-targeted preferences, check for existing similar preferences in Domain State**:
   - If a semantically equivalent preference already exists → skip (duplicate)
   - If the new preference **contradicts** an existing one → replace the old one with the new one
   - If no existing equivalent → add to Domain State

### Step 3: Clean Up Domain State

After all signals are processed:

- If Domain State has grown noticeably, review for entries that can be compressed or consolidated
- Items marked `mastered` for more than 30 days with no further status changes can be removed from Domain State
- Report to the user if any cleanup was performed

### Step 4: Clear Extract Buffer

After all signals have been distributed successfully, clear the content of Extract Buffer (keep the file, empty its content).

### Step 5: Report

```
Sync complete ({date}):
- Processed: {n} signals from {m} extract blocks
- Domain State updated: {list of changes, or "no changes"}
- Thinking patterns observed: {list of summaries, or "none"}
- Core Profile candidates (your decision needed): {list, or "none"}
- Duplicates skipped: {number}
- Buffer cleared
```

For each `[core-candidate]` surfaced, ask the user directly:
> "This pattern/preference isn't in your Core Profile yet: [{description}]. Add it? (yes / no / edit)"  
> If yes → instruct user to manually add to their `{user}-core.md`. Do not write it yourself.

After reporting, remind the user:
> This session is now complete. Do not run `/contour:extract` in this session — the sync conversation would produce echo signals.

---

## Deduplication Rules

Deduplication is **semantic, not lexical**. Two entries refer to the same thing if:

1. They describe the **same concept, tool, or process** (e.g., "environment variables" and "env vars" and ".env files" are the same if they refer to the same knowledge point)
2. They describe the **same thinking pattern** (e.g., "validate before expanding" and "don't expand until the core is proven" are the same pattern)
3. They describe the **same preference** (e.g., "use terminology" and "don't dumb down technical terms" express the same preference)

When in doubt, **keep both entries** — false deduplication (losing a real signal) is worse than mild redundancy (which can be cleaned up manually).

---

## Edge Cases

- **Multiple extract blocks in Extract Buffer**: Process them chronologically. Later signals may override earlier ones for the same knowledge point.
- **Signals from different workspaces**: Route by content domain, not by source workspace. A coding cognition signal captured in `Content_Creator` still goes to the coder domain files.
- **Conflicting signals in the same sync**: If two signals in Extract Buffer contradict each other (e.g., one says "partial", another says "mastered" for the same knowledge point), use the **later** one (it reflects more recent state).
- **Missing target files**: If Domain State doesn't exist yet, create it with the appropriate structure per the reference files before writing.
