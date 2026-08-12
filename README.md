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
| **What's here** | A skill draft at the repository root ([`SKILL.md`](SKILL.md), [`references/`](references/), [`assets/`](assets/), [`scripts/`](scripts/)) — protocol, references, templates and validation scripts |
| **What's not** | A working end-to-end implementation. The private instance repository now has an empty skeleton (2026-08-12), but **channel verification GH-01–06 has not been run on any endpoint**, and no unified assets exist |
| **Previous version** | Tag `v0.3.0-cognitive` and its [GitHub Release](https://github.com/Alexu0317-FATHER/contour/releases) — a different product (cognitive-state tracking) that ran for over a month. See [`docs/history/PIVOT.md`](docs/history/PIVOT.md) for what changed and why |

**Everything the old README described — `/contour:sync`, `/contour:extract`, the Stop hook, Domain State — belongs to that archived version and no longer exists in the working tree.**

## Where things live

| Path | What it is |
|---|---|
| [`docs/新知界需求.md`](docs/新知界需求.md) | The single requirements spec for the current version; only capabilities intended for the current implementation belong here |
| [`docs/roadmap/`](docs/roadmap/) | Confirmed future capabilities that are not part of the current version; each topic gets its own document until it is ready to enter the requirements or skill |
| [`SKILL.md`](SKILL.md) + [`references/`](references/) / [`assets/`](assets/) / [`scripts/`](scripts/) | The skill itself, at the repository root. Rules live here and nowhere else, because the skill is what gets distributed to each endpoint |
| [`docs/history/`](docs/history/) | Archived design drafts, cross-reviews, and the previous product's documentation |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed each iteration |

Your own profile, dumps and evidence do **not** live here. They belong in a separate private repository — this one is public code with a public release history, and personal material has no business in it.

## Installing on each endpoint

What gets installed is one file — `routing.md` (communication routing + memory attention policy). It is the only one that must be present on every turn; everything else is read on demand. **The distinction that matters is not "does this endpoint support skills" but "can this endpoint guarantee `routing.md` is in context before the model starts answering".**

| Endpoint | Method | Residency guarantee |
|---|---|---|
| **Claude Code** | `@<instance-repo>/routing.md` in `CLAUDE.md` | ✅ Expanded deterministically by the harness |
| **Codex** | Managed block in `AGENTS.md` holding the full text | ✅ Deterministic, but it is a **copy** — regenerate on every sync |
| **Claude.ai / ChatGPT** | Upload to Project Files / file library, put a one-line pointer in the instructions slot | ⚠️ **Test it immediately**: does the file enter context deterministically, or is it retrieved by relevance? If retrieval, downgrade |
| None of the above works | Paste a read-only projection into custom instructions, with a generation-date header | ⚠️ A copy; must be re-pasted by hand after each sync |

**Codex does not expand `@path`** — this is a measured result, not an assumption, which is why it uses a managed block rather than an import. Full per-endpoint instructions, the shared discipline for all three copy-based methods, and how "feeding" works are in [`references/load.md`](references/load.md).

**Installing the skill ≠ residency.** Skills are progressively disclosed: only the `description` is always present; the body loads once it matches a task. So installing the skill buys you "this endpoint can run the whole flow itself" — not "the routing table is there every turn". **You need both.**

## Getting started: one sentence is enough

Once installed there are no commands to memorise. Say "**sync Contour**" or "**what's Contour's status**" — the skill reads the instance repository first to work out which step you are on (cold start / new endpoint / catch-up / consolidation / dump / audit), then continues from there. You do not have to explain the context.

The first run asks which endpoints you use and which are your primary ones, then walks you through choosing an anchor and running a baseline dump on each. **The first unified profile requires baselines from at least two different endpoints** — with only one, what you get is not a cross-endpoint profile, it is that one endpoint repeating itself.

**Nothing happens before you say so.** If you merely complain that "this AI doesn't get me", the skill will at most explain itself and ask whether you want to sync — **it will not even read your private repository.** Reading, writing, committing and merging all require an explicit yes.

## Design commitments

- **One authoritative anchor; any capable endpoint may take a turn coordinating; a single publish is serialised.** Copies are fine; two authoritative anchors are not. Catch up before reading, and write conditionally.
- **Contour does not hold your memory, it refreshes it.** Native memory systems keep doing their job; Contour supplies better material and a portable attention policy.
- **Convergence is measured, not asserted.** Without behavioural testing there is no reason to believe endpoints are drifting together rather than apart.
- **Nothing happens without your say-so.** The skill being triggered is not permission to read your repository, let alone write to it.

## License

MIT — see [LICENSE](LICENSE).
