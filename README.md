# Contour (知界)

Fine-grained cognitive state tracking for Claude Code.

Most AI tools treat you as either an expert or a beginner. Contour tracks exactly what you know, what you partially understand, and what you don't — per knowledge point, per domain — and keeps that state synchronized across sessions.

## How it works

Contour uses four local files per domain:

- **D** (`{user}-core.md`) — Your communication profile. Loaded globally, rarely changes.
- **B** (`{user}-{domain}.md`) — Your cognitive state snapshot for a domain. Updated continuously.
- **C** (`{user}-{domain}-log.md`) — Append-only audit log. For your review only.
- **A** (`extract-buffer.md`) — Cross-session signal buffer.

Two update mechanisms run in parallel:
1. **Live monitoring** — Instructions injected into `CLAUDE.md` detect cognitive changes during work and update B silently.
2. **Extract + sync** — `/contour:extract` scans a session for signals; `/contour:sync` distributes them to B and C.

## Requirements

- [Claude Code](https://claude.ai/code)

## Installation

Run `/plugin` in Claude Code and enter:

```
Alexu0317-FATHER/contour
```

Then initialize:

```
/contour:setup
```

Restart Claude Code after setup completes to activate the live monitoring instruction.

## Commands

| Command | When to run | What it does |
|---------|-------------|--------------|
| `/contour:setup` | Once, after install | Initializes your D/B/C/A files and injects monitoring into `CLAUDE.md` |
| `/contour:extract` | End of a significant session | Scans the session for cognitive signals, writes to buffer |
| `/contour:sync` | In a new dedicated session | Reads buffer, updates B and C, clears buffer |

## Data files

Stored at `~/.claude/contour/` by default. Override with the `$AI_INFRA_DIR` environment variable.

All files are plain Markdown — readable, editable, and yours.

## Version

`v0.1.0` — Pre-release. In active testing.
