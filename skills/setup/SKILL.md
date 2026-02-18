---
name: setup
description: "Cold-start initialization: generate D/B/C/A files, inject CLAUDE.md monitoring instructions. Run once per user, or to reset."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob, Bash, AskUserQuestion"
---

# /contour:setup

Initialize the Contour AI infrastructure for this user. Creates all data files and injects the monitoring instruction into CLAUDE.md.

> **Run this once** after installing the plugin. Re-running will prompt before overwriting existing data.

---

## Reference Files

Before executing, read the following reference files:
- `references/d-structure.md` — D file format and initialization guide (Scenario A and B)
- `references/claude-md-injection.md` — CLAUDE.md injection template and placeholder substitution guide

**Interaction style:**
- For questions with predefined options: use the `AskUserQuestion` tool (enables arrow-key selection in the terminal).
- For open-ended text questions (username, domain name, Q1 background): ask as plain text — do not use `AskUserQuestion`.
- For all free-text inputs: if the user submits an empty or near-empty response (whitespace, single character), re-prompt once with a brief example of what's expected.
- If the user selects "Other" for any `AskUserQuestion`, immediately follow up: "Please describe:" and wait for their input. If they provide nothing, skip the item and proceed.

**B and C file initial structures** (use directly — do not cross-reference sync skill files):

B file:
```
# {User} — {Domain} Cognitive State

Last synced: (not yet synced)

## Cognitive State

| Knowledge Point | Unknown | Partial | Mastered | Updated |
|-----------------|---------|---------|----------|---------|

## Communication Rules

- (to be populated as preferences are expressed)
```

C file:
```
# {User} — {Domain} Log

---

(Entries will be appended here by /contour:sync)
```

---

## Pre-flight

Check whether the data directory already exists:
- If `~/.claude/contour/` (or `$AI_INFRA_DIR` if set) **exists and contains files** → ask (AskUserQuestion):
  > "Contour data already exists. Running setup will overwrite your D, B, C files. (extract-buffer.md will be preserved.) Continue?"
  > Options: "Yes, overwrite" / "No, cancel"
  - If "No, cancel" → STOP
- If the directory **does not exist** → proceed directly to Step 1

---

## Step-by-Step Execution

### Step 1 — Language

Ask (AskUserQuestion):
> 请选择语言 / Choose language

Options: **中文** / **English**

Record the selection. All user-facing output from this point forward (including the rest of this setup, generated file content, and the final report) uses the selected language. Internal prompt logic remains English throughout.

---

### Step 2 — Data directory

Resolve the data directory path:
1. Check whether `$AI_INFRA_DIR` is set in the environment
2. If yes: use that path; if no: use `~/.claude/contour/`

Create the directory if it does not exist. Report the resolved path to the user.

---

### Step 3 — Username

Ask (plain text):
> "What name should Contour use for your files? (This becomes the `{user}` prefix, e.g., `alex-core.md`)"

Validate: non-empty. If empty, re-prompt once with example: "e.g., alex, jane, mike"

Record as `{user}`. Suggest lowercase, no spaces if the user provides something else.

---

### Step 4 — Generate D (Core Profile)

Ask (AskUserQuestion):
> "Do you have an existing document about yourself — a profile, bio, or description you've written for AI?"

Options: **Yes, I have a document** / **No, start from scratch**

**If Yes (Scenario A):**
Follow the Scenario A process in `references/d-structure.md`.

**If No (Scenario B):**
Follow the Scenario B process in `references/d-structure.md`. Ask the 4 questions defined there.

Write the finalized D file to: `{AI_INFRA_DIR}/{user}-core.md`

---

### Step 5 — Domain name

Ask (plain text):
> "Which domain should Contour track your cognitive state for? Use one word — this becomes the file prefix."
> "e.g., `coder`, `writer`, `researcher`, `designer`"

Validate: non-empty. If empty, re-prompt with the examples above.

Record as `{domain}`.

Create `{AI_INFRA_DIR}/{user}-{domain}.md` using the B file initial structure above.

---

### Step 6 — Generate C (Domain Log)

Create `{AI_INFRA_DIR}/{user}-{domain}-log.md` using the C file initial structure above.

---

### Step 7 — Create A (Extract Buffer)

Create `{AI_INFRA_DIR}/extract-buffer.md` with:
```
# Extract Buffer

(Signals appended here by /contour:extract, cleared by /contour:sync)
```

If the file already exists **and has content**: warn the user and skip — do not overwrite.
> "extract-buffer.md already has content. Skipping to avoid data loss. Run /contour:sync first if you want to clear it."

---

### Step 8 — Inject CLAUDE.md

Read `references/claude-md-injection.md` for the exact injection block and placeholder substitution rules.

Target file: `~/.claude/CLAUDE.md`
- If the file does not exist: create it with just the injection block
- If the file exists: append the injection block at the end (do not overwrite existing content)

Substitute placeholders:
- `{AI_INFRA_DIR}` → resolved absolute path from Step 2
- `{user}` → value from Step 3
- `{domain}` → value from Step 5

---

### Step 9 — Report

```
Contour setup complete ({date}):

Files created:
- D (Core Profile):    {AI_INFRA_DIR}/{user}-core.md
- B (Cognitive State): {AI_INFRA_DIR}/{user}-{domain}.md
- C (Domain Log):      {AI_INFRA_DIR}/{user}-{domain}-log.md
- A (Extract Buffer):  {AI_INFRA_DIR}/extract-buffer.md

CLAUDE.md updated:     ~/.claude/CLAUDE.md

⚠️  RESTART REQUIRED
The monitoring instruction won't take effect until you restart Claude Code.

Next steps:
1. Restart Claude Code now
2. Work normally — Contour tracks cognitive changes in the background
3. After a significant session, run /contour:extract to capture signals
4. When ready, run /contour:sync in a new session to update your files
```
