# Core Profile Structure & Initialization Guide

Defines the format of `{user}-core.md` (the Core Profile file) and the initialization process for both setup scenarios.

---

## Core Profile Format

```markdown
# {User} — Core Profile

Last reviewed: YYYY-MM

## Communication Style
- [How the user prefers AI to structure responses: length, tone, format]
- [Language preference]
- [What to skip vs. always explain]

## Thinking Patterns
- [Characteristic decision-making approaches]
- [Mental models the user defaults to]
- [How the user handles uncertainty or tradeoffs]

## What AI Can Assume
- [Domains/concepts where the user has deep familiarity — AI can use without explanation]
- [Background context that affects how to frame responses]

## Core Preferences
- [Strong preferences or aversions about AI behavior]
- [Values that affect how the user wants disagreements handled]
```

**Target length:** 20–50 lines. Lean toward shorter.

**Inclusion criteria:** Only include traits that directly affect how AI should communicate or interact with this user. Every line should answer: "Does knowing this change how I should respond?"

**Exclusion criteria (must filter out):**

- Job titles, career history, project descriptions
- Skills or expertise that don't affect communication style
- Personality traits not relevant to AI interaction
- One-time context or situational information
- Anything that could go in a Domain State file (domain-specific knowledge state) instead

---

## Scenario A: User Has an Existing Document

Use when the user provides a pre-existing profile document.

### Step-by-step

1. **Ask the user to provide the file path or paste the content.**

2. **Read the provided document in full.**

3. **Filter pass:** For each item in the document, evaluate against the inclusion criteria above.
   - Career/professional content → discard
   - Communication style signals → keep
   - Thinking patterns → keep if persistent and cross-domain
   - Domain expertise → only keep if it means "AI can skip explaining X entirely"

4. **Extract and restructure** into the Core Profile format. Rewrite for clarity and concision; do not copy verbatim if the original format doesn't fit.

5. **Present the draft Core Profile to the user** and ask (AskUserQuestion):
   > "Does this capture how you want me to interact with you?"
   >
   > Options: "Looks good" / "I want to add something" / "Remove or adjust something"

6. If the user wants to add or adjust: collect input, update the draft, re-confirm.

7. **Finalize** once confirmed.

---

## Scenario B: User Has No Existing Document

Use when the user has no pre-existing profile. Ask the following questions one at a time; do not proceed to the next until the current answer is received.

For questions with predefined options, use `AskUserQuestion`. For Q1 (open-ended), ask as plain text.

### Questions

**Q1 — Background & domain assumptions**

Ask as plain text (free-form response):

> "What should I assume you already know? What can we treat as shared ground — things you won't need me to explain from scratch?
>
> Take a moment to think about what feels obvious to you vs. what requires background. You can be specific or general.
>
> *(Examples: "software engineering basics and common dev tools", "I know product thinking and UX, but not code", "general business operations, no tech background — explain when needed", "I've done some vibe coding but I'm not a trained developer")*"

If the user submits an empty response, re-prompt once.

---

**Q2 — Communication style**

Use `AskUserQuestion` (multiSelect: true):

> "How do you prefer I communicate?"

Options:

- Direct and brief — skip context, just the answer
- Detailed explanations — I want to understand the "why"
- Examples over abstractions — show, don't tell
- Think with me — explore together, not lecture
- Always give the conclusion first, then reasoning
- Other (I'll describe)

---

**Q3 — Thinking style**

Use `AskUserQuestion` (multiSelect: true):

> "When solving a problem or making a decision, what's your natural approach?"

Options:

- Validate the core before expanding — prove it works small before going big
- Think in systems — understand the whole picture before the parts
- Bias toward action — build and learn, adjust as you go
- Risk-first — always ask "what's the worst case" before committing
- Other (I'll describe)

---

**Q4 — AI behavior preferences**

Use `AskUserQuestion` (multiSelect: true):

> "Are there things AI does that you love or strongly dislike?"

Options:

- Push back directly when I'm wrong — don't soften it
- Don't auto-add caveats and disclaimers to everything
- Don't embellish or rewrite my words without being asked
- Ask clarifying questions instead of assuming
- Give me options, let me decide
- Other (I'll describe)

---

### After collecting answers

1. Synthesize the answers into the Core Profile format.
2. Present the draft and confirm with the user (same AskUserQuestion pattern as Scenario A step 5).
3. If the user wants to add or adjust: collect input, update the draft, re-confirm.
4. Finalize once confirmed.

---

## Notes

- Core Profile is initialized once and rarely updated. Resist adding things that belong in Domain State (cognitive state) or are session-specific.
- If the user skips a question, leave that dimension out of Core Profile — a minimal Core Profile is better than a padded one.
- After initialization, tell the user: "You can update this file manually at any time. Aim to review it every 6–12 months."
