---
name: policy-gate
description: Gate 2. Decides whether the proposed next step is allowed right now under the demo policy. Blocks prohibited actions, escalates unsafe cases, and downgrades any step whose preconditions are not met.
---

# policy-gate (Gate 2)

**Runs:** always, including after an earlier halt, so a blocked request is recorded even when the AI step failed. **Calls a model:** no.

## Input
- `state.assessment` (already validated), `state.requested_actions` (from events such as `ADDRESS_CHANGE_REQUEST`), `state.evidence_index`, `state.run`, `state.policy`.

## Output
- `state.gate`: `GateResult(status, action, reasons, blocked_actions, reassess_at)`.

## Check order
1. **Always-blocked.** Is any requested or proposed action in `policy.always_blocked`? → `BLOCKED`, action `HUMAN_REVIEW`, reason `blocked_action:<ACTION>`.
2. **Latest state.** Re-run Gate 1 (`load-case`). The state may have changed during the AI call.
3. **Escalation.** Any of these → `ESCALATED`, `HUMAN_REVIEW`:
   - `conflicting_evidence`: the assessment lists conflicting evidence.
   - `refusal_unverified`: the cause is `UNVERIFIED_REFUSAL`.
   - `no_reply_after_question`: the reply window passed with no answer.
4. **Preconditions for the proposed step.** If they fail, the step becomes `HUMAN_REVIEW` with the reason.

| Step | Allowed when | Fail reason |
|---|---|---|
| `CLARIFY` | Questions asked < `max_buyer_questions`, buyer contactable, `question_key` has an approved template. If already asked and the window is still open, it becomes `NO_ACTION` (waiting). | `question_limit_reached`, `buyer_not_contactable`, `question_not_approved` |
| `STANDARD_RETRY` | Confidence HIGH, cause in `retry_allowed_causes`, no active disruption, address complete | `retry_blocked:<detail>` |
| `HOLD` | An active disruption signal matches the case area. Sets `reassess_at = now + hold_reassess_minutes`. | `no_active_disruption` |
| `NO_ACTION` | A buyer question is pending and its window is open. Sets `reassess_at` to the window end. | `no_open_response_window` |
| `HUMAN_REVIEW` | Always allowed | (reason `handoff_proposed`) |

## Rules
- Steps are never upgraded, only kept or downgraded to `HUMAN_REVIEW`.
- These are prototype limits, not SPX rules.
