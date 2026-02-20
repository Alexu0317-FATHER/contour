# Contour (知界)

English | [中文](README.zh.md)

Fine-grained cognitive state tracking for Claude Code.

Most AI tools treat you as either an expert or a beginner. Contour tracks exactly what you know, what you partially understand, and what you don't — per knowledge point, per domain — and keeps that state synchronized across sessions.

## Prerequisites

- Node.js environment installed
- Ability to run `npx` commands
- [Claude Code](https://claude.ai/code) installed and configured

## Installation

### Quick Install (Recommended)

```bash
npx skills add Alexu0317-FATHER/contour
```

### Register as Plugin Marketplace

Run the following command in Claude Code:

```bash
/plugin marketplace add Alexu0317-FATHER/contour
```

### Install Skills

**Option 1: Via Browse UI**
1. Run `/plugin` in Claude Code
2. Select `Browse and install plugins`
3. Select `contour`
4. Select the plugin(s) you want to install
5. Select `Install now`

**Option 2: Direct Install**
```bash
/plugin install contour@Alexu0317-FATHER/contour
```

## Update Skills

To update Contour to the latest version:

1. Run `/plugin` in Claude Code
2. Switch to `Marketplaces` tab (use arrow keys or Tab)
3. Select `contour`
4. Choose `Update marketplace`

You can also Enable auto-update to get the latest versions automatically.

## How it works

Contour uses four local files per domain:

- **Core Profile** (`{user}-core.md`) — Your communication profile. Loaded globally, rarely changes.
- **Domain State** (`{user}-{domain}.md`) — Your cognitive state snapshot for a domain. Updated continuously.
- **Domain Log** (`{user}-{domain}-log.md`) — Append-only audit log. For your review only.
- **Extract Buffer** (`extract-buffer.md`) — Cross-session signal buffer.

Two update mechanisms run in parallel:

1. **Live monitoring** — Instructions injected into `CLAUDE.md` detect cognitive changes during work and update Domain State silently.
2. **Extract + sync** — `/contour:extract` scans a session for signals; `/contour:sync` distributes them to Domain State and Domain Log.

## Available Commands

| Command | When to run | What it does |
|---------|-------------|--------------|
| `/contour:setup` | Once, after install | Initializes your Core Profile, Domain State, Domain Log, and Extract Buffer files and injects monitoring into `CLAUDE.md` |
| `/contour:extract` | End of a significant session | Scans the session for cognitive signals, writes to buffer |
| `/contour:sync` | In a new dedicated session | Reads buffer, updates Domain State and Domain Log, clears buffer |
| `/contour:uninstall` | When you want to remove Contour | Removes monitoring injection from `CLAUDE.md`, optionally deletes data files |

### /contour:setup

Initializes the Contour environment for your workspace.

```bash
/contour:setup
```

**What it does:**
- Creates the necessary data files (`Core Profile`, `Domain State`, etc.) in your local directory.
- Injects the live monitoring instructions into your workspace's `CLAUDE.md` file.
- **Note:** Restart Claude Code after setup completes to activate the live monitoring instruction.

### /contour:extract

Extracts cognitive signals from your current session.

```bash
/contour:extract
```

**When to use:**
Run this at the end of a significant working session where you've learned new concepts or demonstrated mastery of existing ones. It scans the conversation history and writes detected signals to the `Extract Buffer`.

### /contour:sync

Synchronizes extracted signals into your permanent cognitive state.

```bash
/contour:sync
```

**When to use:**
Run this in a new, dedicated session (to avoid context pollution). It reads the `Extract Buffer`, updates your `Domain State` and `Domain Log`, and then clears the buffer.

### /contour:uninstall

Removes Contour from your workspace.

```bash
/contour:uninstall
```

**What it does:**
- Removes the Contour monitoring instructions from your `CLAUDE.md`.
- Optionally prompts you to delete the local data files.

## Environment Configuration & Data Files

Stored at `~/.claude/contour/` by default. 

You can override the default storage location by setting the `$AI_INFRA_DIR` environment variable in your system or `.env` file:

```bash
export AI_INFRA_DIR="/path/to/your/custom/dir"
```

All files are plain Markdown — readable, editable, and yours.

## Customization

Because Contour stores your cognitive state in plain Markdown files, you can manually edit them at any time. 

- Want to force Claude to treat you as an expert in a specific domain? Open your `{user}-{domain}.md` file and manually update the status of concepts to `mastered`.
- Want to adjust your communication preferences? Edit your `{user}-core.md` file.

Contour will respect your manual edits during the next session.

## Disclaimer

- **File Modification:** The `/contour:setup` command will modify the `CLAUDE.md` file in your current workspace to inject monitoring instructions.
- **Data Privacy:** All cognitive state tracking happens locally on your machine. No data is sent to external servers by Contour itself (though Claude Code sends prompts to Anthropic's API as usual).

## Version

`v0.2.1` — Pre-release. In active testing.

## License

MIT
