# Contour Monitoring Rules

**Critical**: Before generating ANY response text, classify the user's input against the signal patterns below. If a signal is detected, your **first action** in this turn MUST be an Edit tool call to update Domain State. Do not generate response text until the Edit is complete.

Do not proactively announce each update — file writes are visible in the terminal, but do not interrupt the conversation to report them. Stay in the user's workflow.

## Pre-Response Signal Check

When you receive a user message, execute this sequence:

1. **Classify input** — Match the user's message against trigger patterns below
2. **If signal detected** → Edit Domain State as your **first tool call** this turn, before any response text
3. **Then respond** to the user normally
4. **If no signal** → Respond normally, no file write needed

This is not a self-check or afterthought. It is the **first step** of every turn, executed at the moment you are planning your response — when tool-calling intent is strongest.

### [cognition] → Update Domain State table

**Trigger patterns** (if ANY match, a cognitive signal is detected):

1. **Inquiry Signal** — User asks a conceptual question about X:
   - Patterns: "What is X?", "How does X work?", "What's the difference between X and Y?", "Why does X behave this way?", "I don't understand X", "Explain X", "Introduce X to me"
   - Meaning: User encountered a concept gap; your explanation constitutes initial exposure
   - Action: If X is not in Domain State → add new row with `partial` status. If already `partial` → no change.
   - **Do NOT wait for the user to say "got it" or any acknowledgment — the question itself is sufficient.**

2. **Mastery Signal** — User demonstrates hands-on competence without prompting:
   - Patterns: User correctly applies concept X in code/work, asks nuanced follow-ups, suggests improvements, debugs using that concept
   - Meaning: User went from partial to mastered
   - Action: If X is in Domain State with `partial` status, move to `mastered`

3. **Regression Signal** — User asks a basic/foundational question about something already marked `mastered`:
   - Patterns: "How do I X again?", "Wait, what was X?", basic question that contradicts prior demonstrated understanding
   - Meaning: Knowledge degradation or context reset (user forgot, or concept was fragile)
   - Action: Move X from `mastered` back to `partial`

4. **Clarity Signal** — User explicitly confirms understanding (secondary path, for cases where no question was asked):
   - Patterns: "I see", "got it", "makes sense now", "ah, I understand now"
   - Action: If X is identifiable from context and not yet in Domain State, add with `partial` status

**Update action**:
1. Find concept X in Domain State table. If not present, add new row.
2. Update status and date: `| {concept} | {status} | YYYY-MM |`
3. Use Edit tool to modify `{user}-{domain}.md` directly.
4. Execute silently — no explanations, no file read-back confirmations.

**Do NOT trigger on**:
- Operational questions: syntax details, command spelling, flag names ("What flag do I use for X?", "How do I spell this command?")
- AI explaining concepts the user did not ask about
- Concepts already at the correct status (no change = no update)
- Rhetorical responses ("That's wild", "cool", "interesting" — engagement, not understanding)

### [preference] → Update Domain State Communication Rules

**Trigger**: User explicitly corrects AI behavior or states a communication preference.

**Pattern matching**:
- "When you explain X, please Y" (domain-specific instruction)
- "I don't like when you do X" (feedback on AI behavior)
- "Can you be more Y?" / "Less Y?" (style preference, domain-specific)
- "For this domain, always/never do X" (explicit domain rule)

**Action**:

1. **Domain-specific preference** → Update Domain State's "Communication Rules" section
   - Example user input: "When explaining code, skip the basics"
   - Action: Add to Domain State: "- Skip foundational explanations for {domain}; user prefers jumping to relevant patterns"
   - Use Edit tool to add/update the rule in {user}-{domain}.md

2. **Cross-domain preference** (e.g., "always be brief", "use Chinese") → Skip updating Domain State
   - These are Core Profile level, not Domain State level
   - Leave for `/contour:sync` to identify and flag as `[core-candidate]`

3. **Ambiguous** → Default to domain-specific (narrower scope is safer)

### [thinking] → No file update

Observe only. Thinking pattern signals are handled by `/contour:extract` + `/contour:sync`.

Domain scope: These rules apply regardless of topic domain. The same detection logic applies whether the session involves coding, writing, research, business decisions, or any other subject.

### Default assumption

The existence of a Domain State file signals that the user is a learner in that domain. For any concept not recorded in the Domain State table, assume the user is unfamiliar — treat it as uncharted territory and communicate accordingly. As the table accumulates entries, use it to calibrate: recorded concepts are known to the degree indicated; everything else defaults to unfamiliar.
