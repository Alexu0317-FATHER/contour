---
name: uninstall
description: "Remove Contour monitoring injection from CLAUDE.md, optionally delete data files. Safe: never deletes non-Contour files."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob, Bash, AskUserQuestion"
---

# /contour:uninstall

Remove Contour from this system. Cleans up CLAUDE.md injection and optionally deletes data files.

> **Safe by design**: only removes content with Contour markers or Contour-prefixed filenames. Never touches files it didn't create.

---

## Step 1 — Confirm intent

Ask (AskUserQuestion):
> "This will remove Contour's monitoring injection from CLAUDE.md. Continue?"

Options: **Yes, uninstall** / **No, cancel**

If "No, cancel" → STOP.

---

## Step 2 — Remove CLAUDE.md injection and rules file

**2a — Remove CLAUDE.md entry block**

Target file: `~/.claude/CLAUDE.md`

1. Read the file
2. Find the block bounded by `<!-- Contour -->` and `<!-- End Contour -->` (inclusive of both marker lines)
3. If found: delete the entire block (and any blank line immediately preceding it)
4. If not found: note "No Contour injection found in CLAUDE.md" and continue
5. Write the updated file back

**2b — Delete rules file**

Target file: `~/.claude/rules/contour-monitoring.md`

- If found: delete it
- If not found: skip silently

---

## Step 3 — Ask about data files

Resolve the data directory: check `$AI_INFRA_DIR`, fall back to `~/.claude/contour/`.

Ask (AskUserQuestion):
> "Delete your Contour data files in {resolved_path}? This includes Core Profile, Domain State, Domain Log, and Extract Buffer. This cannot be undone."

Options: **Yes, delete data files** / **No, keep data files**

**If Yes:**
- List all files in the directory
- Delete only files matching these patterns:
  - `*-core.md`
  - `*-*.md` (Domain State and Domain Log files)
  - `extract-buffer.md`
- If the directory is now empty, remove it
- If the directory still contains other files (user-created), leave it in place

**If No:**
- Skip deletion, note the path so the user knows where files remain

---

## Step 4 — Report

```
Contour uninstall complete ({date}):

CLAUDE.md:     injection block removed (restart Claude Code to take effect)
Data files:    {deleted / kept at {path}}

Next step:
  claude plugin uninstall Alexu0317-FATHER/contour
```

Render the report in the user's language if detectable from the session; otherwise use English.

---

## Safety rules

- **Never delete** files that don't match the patterns above
- **Never delete** `~/.claude/CLAUDE.md` itself — only edit it
- If any file operation fails, report the failure and continue with remaining steps
- If `CLAUDE.md` does not exist, skip Step 2 silently
