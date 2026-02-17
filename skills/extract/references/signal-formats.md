# Signal Recording Formats

Canonical formats for the three signal types. Used by `/extract` when writing to A, and by `/sync` when parsing A.

---

## [cognition] Cognitive Signal

```
[cognition] {brief description of the knowledge point}
  status: {unknown | partial | mastered}
  evidence: {specific behavior from the session, 1-2 sentences}
  reference: {if status was determined by comparing with B, note B's current record, e.g., "B: partial" or "B: not tracked"}
```

**Status definitions**:
- `unknown` — user asked a basic conceptual question, exposing lack of understanding
- `partial` — user expressed initial understanding after explanation ("I see", "got it"), but no behavioral proof of mastery
- `mastered` — user either stated they already know it, or demonstrated behavioral mastery (correctly used the concept in a practical context)

---

## [thinking] Thinking Signal

```
[thinking] {brief description of the thinking pattern or decision logic}
  evidence: {specific behavior from the session, 1-2 sentences}
```

---

## [preference] Preference Signal

```
[preference] {brief description of the preference}
  evidence: {specific behavior from the session, 1-2 sentences}
```
