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
| **What's not** | A working end-to-end implementation. The GitHub instance repository, channel verification and endpoint probes have not been run yet |
| **Previous version** | Tag `v0.3.0-cognitive` and its [GitHub Release](https://github.com/Alexu0317-FATHER/contour/releases) — a different product (cognitive-state tracking) that ran for over a month. See [`docs/history/PIVOT.md`](docs/history/PIVOT.md) for what changed and why |

**Everything the old README described — `/contour:sync`, `/contour:extract`, the Stop hook, Domain State — belongs to that archived version and no longer exists in the working tree.**

## Where things live

| Path | What it is |
|---|---|
| [`docs/新知界需求.md`](docs/新知界需求.md) | The requirements document — the single live spec |
| [`skills/contour/`](skills/contour/) | The skill itself. Rules live here and nowhere else, because the skill is what gets distributed to each endpoint |
| [`docs/history/`](docs/history/) | Archived design drafts, cross-reviews, and the previous product's documentation |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed each iteration |

Your own profile, dumps and evidence do **not** live here. They belong in a separate private repository — this one is public code with a public release history, and personal material has no business in it.

## Design commitments

- **One write authority, catch up before reading, conditional writes.** Copies are fine; two write authorities are not.
- **Contour does not hold your memory, it refreshes it.** Native memory systems keep doing their job; Contour supplies better material and a portable attention policy.
- **Convergence is measured, not asserted.** Without behavioural testing there is no reason to believe endpoints are drifting together rather than apart.
- **Nothing happens without your say-so.** The skill being triggered is not permission to read your repository, let alone write to it.

## License

MIT — see [LICENSE](LICENSE).
