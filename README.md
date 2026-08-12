# Contour (知界)

English | [中文](README.zh.md)

**Cross-endpoint memory coordination for people who use several AI assistants at once.**

If you use Claude Code, Codex, Claude.ai, Claude Desktop and ChatGPT, each one holds a different, partial memory of you. Switching endpoints means explaining yourself again — your memory has become a platform switching cost. And none of them carries a portable definition of *how you want to be talked to*.

Contour addresses that. It does **not** replace any platform's native memory. It keeps one source of truth you own, feeds each endpoint's native memory from it, and puts a portable routing table into every endpoint's always-on context so behaviour converges over time.

---

## Status: in development, not installable yet

This repository is **mid-rebuild**. There is no release you can install today.

| | |
|---|---|
| **What's here** | A skill draft under [`skills/contour/`](skills/contour/) — protocol, references, templates and validation scripts |
| **What's not** | A working end-to-end implementation. The private instance repository now has an empty skeleton (2026-08-12), but **channel verification GH-01–06 has not been run on any endpoint**, and no unified assets exist |
| **Previous version** | Tag `v0.3.0-cognitive` and its [GitHub Release](https://github.com/Alexu0317-FATHER/contour/releases) — a different product (cognitive-state tracking) that ran for over a month. See [`docs/history/PIVOT.md`](docs/history/PIVOT.md) for what changed and why |

**Everything the old README described — `/contour:sync`, `/contour:extract`, the Stop hook, Domain State — belongs to that archived version and no longer exists in the working tree.**

## Where your data lives

**Not in this repository.** Contour walks you through creating **your own private repository**, and your profile, dumps and evidence live there — this repo is public code, and personal material has no business in it.

That private repository is yours, not Contour's: you can open it at any time and read every conclusion, where it came from, and which endpoint contributed it when.

## Installing

### 1. Install the skill (you do this — one command)

```bash
git clone https://github.com/Alexu0317-FATHER/contour ~/.claude/skills/contour
```

Claude Code inside VS Code reads the same directory, so **one install covers both**.

> ⚠️ `master` still holds the archived previous product; the new skill lives on the `chore/clear-legacy-tree` branch. Until that merges, add `-b chore/clear-legacy-tree`.

**Other endpoints**: how to install the skill package on Codex, Claude.ai, ChatGPT and Zed is `[unverified]` — it will be filled in once each is actually tested. Another product's setup steps do not get written from memory.

### 2. Say one sentence (you do this)

Once installed, say "**initialise Contour**" anywhere.

The skill asks which endpoints you use and which are primary, then walks you through creating a private instance repository and running a baseline dump on each. **The first unified profile requires baselines from at least two different endpoints** — with only one, what you get is not a cross-endpoint profile, it is that one endpoint repeating itself.

After that, "**sync Contour**" or "**what's Contour's status**" is all you need. The skill reads the instance repository to work out which step you are on (catch-up / consolidation / dump / audit). **No context to explain, no commands to memorise.**

### 3. Config files are written by the skill (not by you)

**You never hand-edit a `CLAUDE.md` or `AGENTS.md`.** The skill:

- writes an import line pointing at your source of truth into **global** `~/.claude/CLAUDE.md`
- writes a marked block into **global** `~/.codex/AGENTS.md` (Codex does not expand `@path` — a measured result — so that side gets the full text)
- refreshes both after every sync

**It never touches the `CLAUDE.md` / `AGENTS.md` inside your projects.** Those may be committed to git, shared with colleagues, and carry the project's own conventions — no personal-profile tool has any business editing them.

### The one step that stays manual: uploading a file to web endpoints

Claude.ai and ChatGPT offer **no official API** for updating their project files (third-party sync tools run on session cookies and fail silently when those expire, so the skill does not recommend them). After each sync the skill generates a dated `routing.md` and tells you it's ready; you drag it into Project Files / the file library.

There is no way around this step, but it is **infrequent** — that file changes on the order of months. **Day-to-day dumping and reading go through connectors; you carry nothing.**

### Nothing happens before you say so

If you merely complain that "this AI doesn't get me", the skill will at most explain itself and ask whether you want to sync — **it will not even read your private repository.** Reading, writing, committing and merging all require an explicit yes.

Which loading mechanism each endpoint actually uses, why, and how copies are kept from going stale: [`skills/contour/references/load.md`](skills/contour/references/load.md).

## Design commitments

- **One authoritative anchor; any capable endpoint may take a turn coordinating; a single publish is serialised.** Copies are fine; two authoritative anchors are not. Catch up before reading, and write conditionally.
- **Contour does not hold your memory, it refreshes it.** Native memory systems keep doing their job; Contour supplies better material and a portable attention policy.
- **Convergence is measured, not asserted.** Without behavioural testing there is no reason to believe endpoints are drifting together rather than apart.
- **Nothing happens without your say-so.** The skill being triggered is not permission to read your repository, let alone write to it.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Working on Contour itself, or wondering why a design decision went the way it did? Start from [`docs/新知界需求.md`](docs/新知界需求.md).</sub>
