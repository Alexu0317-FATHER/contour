# Contour Monitoring Rules

**Critical**: Before finishing EVERY response, execute the Self-Check Protocol below. Do not skip this step.
Do not proactively announce each update — file writes are visible in the terminal, but do not interrupt the conversation to report them. Stay in the user's workflow.

## Self-Check Protocol

After generating your response content but BEFORE ending your turn:

1. **Scan this conversation turn** — Review what the user said and how you responded
2. **Match against trigger patterns** (see sections below) — Determine if a cognitive signal was detected
3. **If signal detected** → Update Domain State immediately using Edit tool
4. **If no signal** → End normally, no file write needed

This check is mandatory every turn. It takes ~30 seconds of reasoning. Build it into your response generation workflow.

### [cognition] → Update Domain State table

**Trigger patterns** (if ANY match, a cognitive signal is detected):

1. **Clarity Signal** — User explicitly signals understanding after confusion:
   - Patterns: "I see", "got it", "makes sense now", "that makes sense", "ah, I understand now", "ok, I see how that works"
   - Meaning: User transitioned from not-understanding to partial understanding of concept X
   - Action: If X is in Domain State, move to `partial` status

2. **Mastery Signal** — User demonstrates hands-on competence without prompting:
   - Patterns: User correctly applies concept X in code/work, asks nuanced follow-ups, suggests improvements, debugs using that concept
   - Meaning: User went from partial to mastered
   - Action: If X is in Domain State with `partial` status, move to `mastered`

3. **Regression Signal** — User asks a basic/foundational question about something already marked `mastered`:
   - Patterns: "How do I X again?", "Wait, what was X?", basic question that contradicts prior demonstrated understanding
   - Meaning: Knowledge degradation or context reset (user forgot, or concept was fragile)
   - Action: Move X from `mastered` back to `partial`, flag in Domain Log

4. **New Concept Signal** — User mentions an unfamiliar technical/domain concept for the first time:
   - Patterns: User asks "What is X?", "How does X work?", "I don't understand X"
   - Meaning: Identified a concept not yet in Domain State
   - Action: Add new row to Domain State with status `partial` (initial exposure)

**Update action**:
1. Find concept X in Domain State table. If not present, add new row.
2. Update status and date: `| {concept} | {status} | 2026-02 |`
3. Use Edit tool to modify `{user}-{domain}.md` directly.
4. Execute silently — no explanations, no file read-back confirmations.

**Do NOT trigger on**:
- Purely operational questions ("How do I spell this command?")
- AI explaining concepts the user didn't ask about
- Concepts already at the correct status (no change = no update)
- Rhetorical understanding markers ("That's wild", "cool", "interesting" — these are engagement, not understanding)

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
