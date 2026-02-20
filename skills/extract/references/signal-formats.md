# Signal Recording Formats

Canonical formats for the three signal types. Used by `/extract` when writing to Extract Buffer, and by `/sync` when parsing Extract Buffer.

---

## [cognition] Cognitive Signal

```
[cognition] {brief description of the knowledge point}
  status: {partial | mastered}
  evidence: {specific behavior from the session, 1-2 sentences}
  reference: {if status was determined by comparing with Domain State, note Domain State's current record, e.g., "Domain State: partial" or "Domain State: not tracked"}
```

**Status definitions**:
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
