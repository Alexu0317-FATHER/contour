---
name: setup
description: "Cold-start initialization: generate Core Profile, Domain State, Domain Log, and Extract Buffer files, inject CLAUDE.md monitoring instructions. Run once per user, or to reset."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob, Bash, AskUserQuestion"
---

# /contour:setup

Initialize the Contour AI infrastructure for this user. Creates all data files and injects the monitoring instruction into CLAUDE.md.

> **Run this once** after installing the plugin. Re-running will prompt before overwriting existing data.

---

## Reference Files

Before executing, read the following reference files:
- `references/core-profile-structure.md` — Core Profile format and initialization guide (Scenario A and B)
- `references/claude-md-injection.md` — CLAUDE.md injection template and placeholder substitution guide

**Interaction style:**
- For questions with predefined options: use the `AskUserQuestion` tool (enables arrow-key selection in the terminal).
- For open-ended text questions (username, domain name, Q1 background): ask as plain text — do not use `AskUserQuestion`.
- For all free-text inputs: if the user submits an empty or near-empty response (whitespace, single character), re-prompt once with a brief example of what's expected.
- If the user selects "Other" for any `AskUserQuestion`, immediately follow up: "Please describe:" and wait for their input. If they provide nothing, skip the item and proceed.

**Domain State and Domain Log file initial structures** — use the template matching the language selected in Step 1. Do not cross-reference sync skill files.

**Domain State file (English):**
```
# {User} — {Domain} Domain State

Last synced: (not yet synced)

## Cognitive State

| Knowledge Point | Partial | Mastered | Updated |
|-----------------|---------|----------|---------|

## Communication Rules

- (to be populated as preferences are expressed)
```

**Domain State file (Chinese):**
```
# {User} — {Domain} 认知状态

最后同步：（尚未同步）

## 认知状态

| 知识点 | 部分理解 | 已掌握 | 更新 |
|--------|----------|--------|------|

## 沟通规则

- （待积累沟通偏好后填入）
```

**Domain Log file (English):**
```
# {User} — {Domain} Domain Log

---

(Entries will be appended here by /contour:sync)
```

**Domain Log file (Chinese):**
```
# {User} — {Domain} 领域日志

---

（由 /contour:sync 追加记录）
```

---

## Pre-flight

Check whether the data directory already exists:
- If `~/.claude/contour/` (or `$AI_INFRA_DIR` if set) **exists and contains files** → ask (AskUserQuestion):
  > "Contour data already exists. Running setup will overwrite your Core Profile, Domain State, and Domain Log files. (extract-buffer.md will be preserved.) Continue?"
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

### Step 4 — Generate Core Profile

Ask (AskUserQuestion):
> "Do you have an existing document about yourself — a profile, bio, or description you've written for AI?"

Options: **Yes, I have a document** / **No, start from scratch**

**If Yes (Scenario A):**
Follow the Scenario A process in `references/core-profile-structure.md`.

**If No (Scenario B):**
Follow the Scenario B process in `references/core-profile-structure.md`. Ask the 4 questions defined there.

Write the finalized Core Profile to: `{AI_INFRA_DIR}/{user}-core.md`

---

### Step 5 — Domain name

Ask (plain text) in the selected language:

**If Chinese:**
> "Contour 要追踪哪个领域的认知状态？请用一个英文词作为文件名前缀。"
> "例如：coder（编程）、writer（写作）、researcher（研究）、designer（设计）"
> "也可以输入中文，我会帮你转成英文前缀并让你确认。"

**If English:**
> "Which domain should Contour track your cognitive state for? Use one word — this becomes the file prefix."
> "e.g., `coder`, `writer`, `researcher`, `designer`"

Validate: non-empty. If empty, re-prompt with the examples above.

If the user inputs Chinese, suggest an appropriate English prefix and confirm before proceeding.

Record as `{domain}`.

Create `{AI_INFRA_DIR}/{user}-{domain}.md` using the Domain State initial structure above.

---

### Step 6 — Generate Domain Log

Create `{AI_INFRA_DIR}/{user}-{domain}-log.md` using the Domain Log initial structure above.

---

### Step 7 — Create Extract Buffer

Create `{AI_INFRA_DIR}/extract-buffer.md` with:
```
# Extract Buffer

(Signals appended here by /contour:extract, cleared by /contour:sync)
```

If the file already exists **and has content**: warn the user and skip — do not overwrite.
> "extract-buffer.md already has content. Skipping to avoid data loss. Run /contour:sync first if you want to clear it."

---

### Step 8 — Write rules file and inject CLAUDE.md

Read `references/claude-md-injection.md` for full instructions. Two actions:

**8a — Write rules file**

Write `references/contour-monitoring-rules.md` verbatim to `~/.claude/rules/contour-monitoring.md`.
- Create `~/.claude/rules/` if it does not exist
- If the file already exists: overwrite (rules may have been updated)
- No placeholder substitution needed

**8b — Inject entry block into CLAUDE.md**

Target file: `~/.claude/CLAUDE.md`
- If the file does not exist: create it with just the entry block
- If the file exists:
  - Check whether a block starting with `<!-- Contour -->` and ending with `<!-- End Contour -->` already exists
  - If it exists: replace the entire block with the new entry block (do not duplicate)
  - If it does not exist: append the entry block at the end (do not overwrite existing content)

Substitute placeholders in the entry block:
- `{AI_INFRA_DIR}` → resolved absolute path from Step 2
- `{user}` → value from Step 3
- `{domain}` → value from Step 5

**8c — Add SessionStart hook to settings.json**

Target file: `~/.claude/settings.json`

This hook injects Core Profile and Domain State content into Claude's context at every session start, ensuring deterministic loading instead of relying on passive instruction text.

1. Read `~/.claude/settings.json` (if the file does not exist, start with `{}`)
2. Parse the JSON content
3. Locate or create the `hooks.SessionStart` array
4. Check if a Contour SessionStart hook already exists (look for a command string containing the resolved `{AI_INFRA_DIR}` path):
   - If found: replace it with the new entry (idempotent re-run)
   - If not found: append the new entry to the array
5. The hook entry to add (substitute all placeholders with resolved values from Steps 2, 3, 5):

```json
{
  "matcher": "startup|resume",
  "hooks": [
    {
      "type": "command",
      "command": "cat {AI_INFRA_DIR}/{user}-core.md && echo '---' && cat {AI_INFRA_DIR}/{user}-{domain}.md"
    }
  ]
}
```

6. Write the merged result back to `~/.claude/settings.json`

Important: preserve all existing content in settings.json — only add to or replace within the `SessionStart` array. Do not touch other hooks or settings keys.

---

**8d — Install cognitive monitor hook**

This hook classifies every conversation turn for cognitive signals and automatically updates Domain State — no manual `/extract` or `/sync` needed.

**Step 1: Install hook script**

Copy `hooks/cognitive-monitor.ts` from the plugin directory to `{AI_INFRA_DIR}/hooks/cognitive-monitor.ts`.
- Create `{AI_INFRA_DIR}/hooks/` if it does not exist
- If the file already exists: overwrite (script may have been updated)

**Step 2: Detect Git Bash path (Windows only)**

On Windows, the `claude` CLI requires a Git Bash path. Detect it:

```bash
# Try common locations
for path in \
  "C:\\Program Files\\Git\\bin\\bash.exe" \
  "C:\\Program Files (x86)\\Git\\bin\\bash.exe" \
  "D:\\Program Files\\Git\\bin\\bash.exe" \
  "D:\\Program Files (x86)\\Git\\bin\\bash.exe"; do
  [ -f "$path" ] && echo "$path" && break
done
```

Record as `{GIT_BASH_PATH}`. On macOS/Linux, leave empty.

**Step 3: Detect bun path**

```bash
which bun 2>/dev/null || echo "$HOME/.bun/bin/bun"
```

Record as `{BUN_PATH}`. If bun is not installed, warn the user:
> ⚠️ bun is not installed. The cognitive monitor requires bun to run. Install it from https://bun.sh before proceeding.

**Step 4: Register Stop hook in settings.json**

1. Read `~/.claude/settings.json`
2. Locate or create the `hooks.Stop` array
3. Check if a Contour Stop hook already exists (look for `cognitive-monitor.ts` in the command string):
   - If found: replace it (idempotent re-run)
   - If not found: append
4. The hook entry to add:

**On macOS/Linux:**
```json
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "{BUN_PATH} run {AI_INFRA_DIR}/hooks/cognitive-monitor.ts {AI_INFRA_DIR}/{user}-{domain}.md"
    }
  ]
}
```

**On Windows** (include Git Bash path as third argument, use Windows backslash paths):
```json
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "{BUN_PATH} run {AI_INFRA_DIR}/hooks/cognitive-monitor.ts {AI_INFRA_DIR}/{user}-{domain}.md '{GIT_BASH_PATH}'"
    }
  ]
}
```

5. Write merged result back to `~/.claude/settings.json`

Important: preserve all existing content — only add to or replace within the `Stop` array.

---

### Step 9 — Report

Render the report in the selected language.

**English:**
```
Contour setup complete ({date}):

Files created:
- Core Profile:    {AI_INFRA_DIR}/{user}-core.md
- Domain State:    {AI_INFRA_DIR}/{user}-{domain}.md
- Domain Log:      {AI_INFRA_DIR}/{user}-{domain}-log.md
- Extract Buffer:  {AI_INFRA_DIR}/extract-buffer.md

CLAUDE.md updated:    ~/.claude/CLAUDE.md
settings.json updated: ~/.claude/settings.json (SessionStart + Stop hooks added)
Cognitive monitor:    {AI_INFRA_DIR}/hooks/cognitive-monitor.ts

⚠️  RESTART REQUIRED
The monitoring instruction won't take effect until you restart Claude Code.

Next steps:
1. Restart Claude Code now
2. Work normally — Contour automatically tracks cognitive changes after every response
3. (Optional) Run /contour:extract + /contour:sync if you want to capture signals from past sessions
```

**Chinese:**
```
Contour 设置完成（{date}）：

已创建文件：
- Core Profile：   {AI_INFRA_DIR}/{user}-core.md
- Domain State：   {AI_INFRA_DIR}/{user}-{domain}.md
- Domain Log：     {AI_INFRA_DIR}/{user}-{domain}-log.md
- Extract Buffer： {AI_INFRA_DIR}/extract-buffer.md

CLAUDE.md 已更新：      ~/.claude/CLAUDE.md
settings.json 已更新：  ~/.claude/settings.json（已添加 SessionStart + Stop hook）
认知监测脚本：          {AI_INFRA_DIR}/hooks/cognitive-monitor.ts

⚠️  需要重启
监控指令在重启 Claude Code 后才会生效。

后续步骤：
1. 现在重启 Claude Code
2. 正常工作——Contour 在每轮对话结束后自动追踪认知变化
3. （可选）如需捕捉过往 session 的信号，可运行 /contour:extract + /contour:sync
```
