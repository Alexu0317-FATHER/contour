# Changelog

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
