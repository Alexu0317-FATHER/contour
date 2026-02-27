# Changelog

## [0.2.5] — 2026-02-27

### Added
- **Stop hook — cognitive-monitor.ts**: Active cognitive monitoring now runs as a system-level Stop hook after every assistant response. A bun TypeScript script reads the conversation transcript, calls `claude -p --model haiku` for semantic signal classification, and writes directly to Domain State when a signal is detected. No LLM self-check involved — execution is deterministic.
- **Anti-recursion mechanism**: Hook sets `CONTOUR_MONITOR_ACTIVE=1` in the environment before calling the inner claude process. Inner Stop hook detects this variable and exits immediately, preventing infinite recursion.
- **Windows support**: Git Bash path passed as third CLI argument; `CLAUDECODE` env var unset to allow nested claude invocation.
- **setup Step 8d**: `/contour:setup` now installs `cognitive-monitor.ts` to `{AI_INFRA_DIR}/hooks/` and registers the Stop hook in `~/.claude/settings.json` (idempotent).
- **uninstall updated**: `/contour:uninstall` now removes the Stop hook from `settings.json` and deletes the hook script.

### Changed
- **Daily workflow simplified**: `/contour:extract` and `/contour:sync` are now optional fallback tools. The Stop hook handles real-time monitoring automatically.
- **Runtime dependency**: `bun` is now required for the cognitive monitor hook. Users without bun installed will see a warning during setup.

### Rationale
Pre-response prompt instruction (0.2.4) improved signal detection timing but remained unreliable — the model still controlled execution. Moving to a Stop hook eliminates LLM compliance as a variable entirely: the hook fires unconditionally after every response, and classification is handled by a separate Haiku call rather than the responding model's self-assessment.

---

## [0.2.4] — 2026-02-26

### Changed
- **Monitoring mechanism restructured from post-response to pre-response**: Replaced Self-Check Protocol (review output after responding) with Pre-Response Signal Check (classify input before responding). Signal detection now happens as the **first step** of each turn — if a cognitive signal is detected, the Edit tool call to update Domain State fires **before** any response text is generated. This eliminates the structural failure mode where LLMs consistently skip post-response meta-tasks.
- **CLAUDE.md injection block updated**: "CRITICAL INSTRUCTION" section rewritten to match pre-response framing — model is instructed to classify input and act first, not self-check after.

### Rationale
Post-response Self-Check Protocol (introduced in 0.2.2) never triggered successfully in practice. Root cause: LLMs naturally end their turn after completing the primary task (answering the user). A post-response epilogue requiring tool calls is structurally unreliable — the model's "attention" has already moved to turn completion. Pre-response classification exploits the moment when tool-calling intent is strongest (turn planning phase), making signal detection a precondition rather than an afterthought.

---

## [0.2.3] — 2026-02-24

### Changed
- **Monitoring trigger upgraded**: Inquiry Signal is now the primary cognition trigger. Conceptual questions ("What is X?", "How does X work?") fire immediately when answered — no longer waiting for user acknowledgment ("明白了"). Clarity Signal demoted to secondary fallback.
- **setup Step 8c added**: `/contour:setup` now writes a `SessionStart` hook to `~/.claude/settings.json`, ensuring Core Profile and Domain State are loaded deterministically at every session start via system-level hook rather than passive CLAUDE.md instruction.
- **uninstall updated**: `/contour:uninstall` now removes the Contour `SessionStart` hook from `settings.json` as part of cleanup.

### Improved
- README (EN/ZH): Added beginner-friendly guide for customizing storage location via `$AI_INFRA_DIR`, with step-by-step instructions for macOS/Linux and Windows.

---

## [0.2.2] — 2026-02-23

### Changed
- **Main monitoring mechanism overhaul**: Transformed passive "monitor during session" framing into explicit **Self-Check Protocol** executed before every response completion. Model now treats cognitive signal detection as a mandatory per-turn step, not optional background task.
- **Trigger pattern definitions expanded** with concrete examples in `contour-monitoring-rules.md`:
  * Clarity Signal: Explicit understanding markers ("I see", "got it", "makes sense now", etc.)
  * Mastery Signal: Hands-on competence demonstration (correct application, nuanced follow-ups, debugging with concept)
  * Regression Signal: Basic question on previously mastered concept ("How do I X again?", "Wait, what was X?")
  * New Concept Signal: First mention of unfamiliar technical term (user asks "What is X?", "How does X work?")
- **CLAUDE.md injection strengthened**: Added "CRITICAL INSTRUCTION" section with explicit per-response directive. Changed framing from "refer to rules file" to "you MUST execute this before finishing" — hardened with CRITICAL/mandatory language.

### Rationale
Previous monitoring rules relied on passive framing unsuited to LLM execution model. LLMs operate request-response, not event-loop. Per-turn self-check protocol bridges this gap by making signal detection an explicit, non-optional step in response generation workflow.

---

## [0.2.1] — 2026-02-20

### Fixed
- `/extract` now refuses to run in a Contour-operational session (e.g., after `/sync` or `/setup`) to prevent echo signal contamination.
- `/extract` report output constrained: factual buffer status observations are allowed, but AI must not describe Contour's internal mechanisms or imply that extract/sync can modify Core Profile.
- `/sync` report now includes a post-completion reminder not to run `/extract` in the same session.

---

## [0.2.0] — 2026-02-20

### Added
- `/contour:uninstall` skill — removes CLAUDE.md injection, deletes rules file, and optionally deletes data files. Safe by design: never touches non-Contour files.
- Bilingual support for Domain State and Domain Log — setup now generates files in the user's selected language (Chinese or English) based on Step 1 selection.
- `contour-monitoring-rules.md` — dedicated rules file written to `~/.claude/rules/` during setup, separating monitoring logic from CLAUDE.md entry block.

### Changed
- **CLAUDE.md three-layer restructure**: injection block is now a short entry point (~8 lines); full monitoring rules moved to `~/.claude/rules/contour-monitoring.md`. Rules can be updated without re-running setup.
- **Terminology unified** across all skill files: A/B/C/D internal shorthands replaced with Extract Buffer / Domain State / Domain Log / Core Profile.
- **Idempotent injection**: setup now checks for existing `<!-- Contour --> ... <!-- End Contour -->` block before writing — re-running setup replaces the block instead of appending a duplicate.
- Step 5 (domain name prompt) now renders in the user's selected language, fixing a language-switch bug when Chinese was selected in Step 1.
- Setup Step 9 report now renders in the user's selected language.
- README Commands table updated to include `/contour:uninstall`.

### Renamed
- `skills/sync/references/b-structure.md` → `domain-state-structure.md`
- `skills/sync/references/c-structure.md` → `domain-log-structure.md`
- `skills/setup/references/d-structure.md` → `core-profile-structure.md`

---

## [0.1.0] — 2026-02-19

Initial pre-release. Core skills operational: `/contour:setup`, `/contour:extract`, `/contour:sync`.
