# Contour (知界)

English | [中文](README.zh.md)

Contour helps people who use several AI assistants organize and synchronize personal memory, reducing the need to introduce themselves again when switching tools.

It collects the memory each endpoint can currently provide, preserves sources, reconciles duplicates, complementary information, and conflicts, then supplies relevant results to the endpoints. The goal is a gradually shared understanding of your background and communication preferences.

## Development status

The current version is in development. A complete installable release is not available yet. [`skills/contour/`](skills/contour/) contains the skill draft, reference rules, templates, and validation scripts. The following describes the intended experience.

The earlier cognitive-state tracking product remains at the `v0.3.0-cognitive` tag and [Release](https://github.com/Alexu0317-FATHER/contour/releases). See [PIVOT](docs/history/PIVOT.md) for the change in direction.

## Getting started after release

Enable Contour in your AI tool and say:

> Help me start using Contour.

You can bring existing personal material or start without a prepared profile. Contour uses known information, asks only for necessary missing details, and helps configure the archive and collect memory from your endpoints. An existing Contour archive is reused.

Say “sync Contour” to organize new memory, or “what's Contour's status?” to see completed and pending work. You can also explicitly select Contour through the platform's skill entry point.

## Your information and results

Your archive stays in the location recorded in your configuration, under your control, rather than in distributed skill files or templates. The release documentation will describe its connection method. Contour explains any missing connection or permission.

At the end of each run, you can see what was organized, which endpoints received or read the update, and what remains pending. If the platform's native memory state cannot be confirmed, the report says so.

Important conclusions retain their sources. Unresolved conflicts are presented for your decision. You can correct, withdraw, or move your information.

## License

MIT — see [LICENSE](LICENSE).

---

See the [product requirements](docs/新知界需求.md) for development goals and acceptance criteria.
