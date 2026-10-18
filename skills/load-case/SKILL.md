---
name: load-case
description: Gate 1. Checks the latest case state against the demo policy before any AI call, and closes or escalates cases that can no longer be assessed.
---

# load-case (Gate 1)

**Runs:** first, on every assessment. **Calls a model:** no.

## Input
- `state.run.facts`: latest case facts (return state, attempts, deadline, delivered).
- `state.policy`: demo policy (`max_attempts`, `policy_version`).
- `state.run.now`: virtual clock.

## Output
Either leaves the state untouched (case continues), or calls `state.escalate(...)`:

| Condition | Result | Reason code |
|---|---|---|
| Case already delivered | `CLOSED` / `CLOSE` | `already_delivered` |
| Case policy version differs from loaded policy | `ESCALATED` / `HUMAN_REVIEW` | `policy_version_mismatch` |
| Return already started or unknown | `ESCALATED` / `HUMAN_REVIEW` | `return_in_progress` / `return_state_unknown` |
| Deadline missing | `ESCALATED` / `HUMAN_REVIEW` | `deadline_unknown` |
| Deadline passed (virtual clock) | `ESCALATED` / `HUMAN_REVIEW` | `deadline_expired` |
| No attempts left | `ESCALATED` / `HUMAN_REVIEW` | `attempts_exhausted` |

## Rules
- Missing values stay unknown. Never guess a missing deadline or return state.
- Buyer intent can never override an expired deadline or a return in progress.
