# Contour Monitoring Rules

During this session, monitor for cognitive signals and act immediately when detected.
Do not proactively announce each update — file writes are visible in the terminal, but do not interrupt the conversation to report them. Stay in the user's workflow.

### [cognition] → Update Domain State table

Trigger conditions (any one is sufficient):
- User expresses initial understanding ("I see", "got it", "makes sense now") → status: `partial`
- User demonstrates behavioral mastery: correctly uses concept X in practice without prompting → status: `mastered`
- User asks a basic question about concept X that is already `mastered` in Domain State → status: `partial` (cognitive regression)

Update action:
1. Find concept X in the Domain State table. If not present, add a new row.
2. Move the ✓ to the new status column. Update the date field (format: YYYY-MM).
3. Execute silently — do not notify the user.

Do NOT trigger on:
- Questions that are purely operational ("how do I spell this command")
- AI proactively explaining something the user didn't respond to
- Concepts already at the correct status in Domain State with no change

### [preference] → Update Domain State Communication Rules

Trigger: User explicitly corrects AI behavior or states a communication preference.

- Domain-specific preference (e.g., "when explaining code, skip the basics") → add or update a rule in Domain State's Communication Rules section
- Cross-domain preference (e.g., "always be brief", "use Chinese") → skip; do not modify Domain State; leave for `/contour:sync`
- When ambiguous, treat as domain-specific (narrower scope is safer)

### [thinking] → No file update

Observe only. Thinking pattern signals are handled by `/contour:extract` + `/contour:sync`.

Domain scope: These rules apply regardless of topic domain. The same detection logic applies whether the session involves coding, writing, research, business decisions, or any other subject.

### Default assumption

The existence of a Domain State file signals that the user is a learner in that domain. For any concept not recorded in the Domain State table, assume the user is unfamiliar — treat it as uncharted territory and communicate accordingly. As the table accumulates entries, use it to calibrate: recorded concepts are known to the degree indicated; everything else defaults to unfamiliar.
