---
name: extract
description: "Scan the current session for cognition/thinking/preference signals and write to extract-buffer.md. Run in the target session (current or --resume'd). Manual invocation only."
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Glob"
---

# /extract

Scan the entire conversation of the current session, extract signals worth long-term recording, and append them to `$AI_INFRA_DIR/extract-buffer.md`.

> **Path configuration**: `$AI_INFRA_DIR` must be set before use. This is the directory where all AI infrastructure files are stored.
> - Default recommended path: `~/.claude/ai-infra/`
> - Set via environment variable, or replace this placeholder with your absolute path.

---

## Reference Files

Before executing, read the following reference files for format specifications:
- `references/signal-formats.md` — recording formats for all three signal types
- `references/extract-output.md` — A's write format, example output, and report template

---

## File References

| Label | File | Role | Access |
|-------|------|------|--------|
| A | `extract-buffer.md` | Temporary buffer: write extracted signals | Append |
| B | `{user}-coder.md` | Current cognitive state for the coder domain | Read only |
| C | `{user}-coder-log.md` | Append-only audit log for human review | (not accessed) |
| D | `{user}-core.md` | Personality-level traits, thinking patterns, core preferences | (not accessed) |

---

## Constraints

- **Read** the conversation content of the current session
- **Read** the corresponding domain B file (e.g., `{user}-coder.md`) for cognitive state comparison
- **Do not load** C (log) or D (core) files
- **Only write** to extract-buffer.md (append, do not overwrite existing content)
- **Do not judge** deduplication, do not make target file routing decisions — those are `/sync`'s responsibilities
- If the current session has no signals worth extracting, inform the user "No extractable signals in this session" and write nothing

---

## Signal Type Definitions

### [cognition] Cognitive Signals

Record changes or exposures in the user's cognitive state regarding a specific knowledge point. **Compare against B** to determine whether observed behavior represents a state change.

**Extraction conditions** (any one is sufficient):
- The user asked a question that exposed a lack of understanding of a concept/tool/process → `unknown`
- The user listened to AI's explanation and expressed initial understanding ("I see", "got it", "makes sense now") → `partial` (cognitive exposure, not mastery)
- The user indicated they already know something AI was explaining ("I know this", "skip the explanation", "no need to explain") → `mastered`
- The user demonstrated **behavioral mastery**: correctly used a concept/tool/process in a practical context (e.g., giving the instruction "submit this as a PR" when PR submission was previously marked as unknown/partial in B) → `mastered`
- The user asked a basic question about a knowledge point that is marked as `partial` or `mastered` in B → `unknown` (cognitive regression)

**Do not extract**:
- The user asked a purely operational question ("how do I spell this command") with no cognitive significance
- AI proactively explained a concept but the user had no reaction or interaction — cannot determine whether the user absorbed it
- Routine tool usage of concepts **not tracked in B** — no baseline to compare against
- The user used a concept that is already marked as `mastered` in B with no change — not a signal, just normal usage

Record each signal using the format defined in `signal-formats.md`.

### [thinking] Thinking Signals

Record patterns or changes in the user's thinking patterns, decision logic, and problem-solving approaches.

**Extraction conditions** (any one is sufficient):
- The user demonstrated a clear priority ranking when making a decision (e.g., chose a lower-cost but less feature-rich solution)
- The user's argumentation exhibited a reproducible thinking pattern (e.g., always asks "what's the worst case" first)
- The user demonstrated a shift in thinking pattern within the current session (e.g., initially used one approach, then switched to another)
- The user explicitly expressed a meta-cognitive statement about "how to think about problems" (e.g., "I think we should validate before expanding")

**Do not extract**:
- Pure emotional expressions ("this is so annoying") — unless it reveals a value judgment
- Routine task progression without decision points
- AI-led reasoning that the user passively followed

### [preference] Preference Signals

Record the user's explicit preference expressions regarding AI communication style, workflow, or tool usage.

**Extraction conditions** (any one is sufficient):
- The user explicitly asked AI to change communication style ("don't use metaphors", "just give the conclusion", "use Chinese")
- The user expressed satisfaction or dissatisfaction with a specific AI behavior ("this explanation is great", "stop auto-embellishing")
- The user demonstrated a work habit or workflow preference ("I prefer to get it working first, then optimize")

**Do not extract**:
- One-time instructions specific to the current task ("put this file in that directory") — not reusable across sessions
- General evaluations of AI capability ("you're very useful") — no actionable signal

---

## Execution Steps

1. Read the reference files listed above for format specifications
2. Read the corresponding domain B file to establish the user's current cognitive baseline
3. Review the entire conversation of the current session
4. Screen for each of the three signal types according to the definitions above, strictly following extraction and non-extraction conditions
5. If signals exist, append to extract-buffer.md following the write format in `extract-output.md`
6. Report extraction results to the user following the report template in `extract-output.md`
7. If no signals, inform the user and write nothing
