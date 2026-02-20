# Contour (知界)

Fine-grained cognitive state tracking for Claude Code.

Most AI tools treat you as either an expert or a beginner. Contour tracks exactly what you know, what you partially understand, and what you don't — per knowledge point, per domain — and keeps that state synchronized across sessions.

## How it works

Contour uses four local files per domain:

- **Core Profile** (`{user}-core.md`) — Your communication profile. Loaded globally, rarely changes.
- **Domain State** (`{user}-{domain}.md`) — Your cognitive state snapshot for a domain. Updated continuously.
- **Domain Log** (`{user}-{domain}-log.md`) — Append-only audit log. For your review only.
- **Extract Buffer** (`extract-buffer.md`) — Cross-session signal buffer.

Two update mechanisms run in parallel:

1. **Live monitoring** — Instructions injected into `CLAUDE.md` detect cognitive changes during work and update Domain State silently.
2. **Extract + sync** — `/contour:extract` scans a session for signals; `/contour:sync` distributes them to Domain State and Domain Log.

## Requirements

- [Claude Code](https://claude.ai/code)

## Installation

Run `/plugin` in Claude Code and enter:

```markdown
Alexu0317-FATHER/contour
```

Then initialize:

```markdown
/contour:setup
```

Restart Claude Code after setup completes to activate the live monitoring instruction.

## Commands

| Command | When to run | What it does |
|---------|-------------|--------------|
| `/contour:setup` | Once, after install | Initializes your Core Profile, Domain State, Domain Log, and Extract Buffer files and injects monitoring into `CLAUDE.md` |
| `/contour:extract` | End of a significant session | Scans the session for cognitive signals, writes to buffer |
| `/contour:sync` | In a new dedicated session | Reads buffer, updates Domain State and Domain Log, clears buffer |
| `/contour:uninstall` | When you want to remove Contour | Removes monitoring injection from `CLAUDE.md`, optionally deletes data files |

## Data files

Stored at `~/.claude/contour/` by default. Override with the `$AI_INFRA_DIR` environment variable.

All files are plain Markdown — readable, editable, and yours.

## Version

`v0.1.0` — Pre-release. In active testing.
