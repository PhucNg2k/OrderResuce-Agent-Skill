---
name: compose-recommendation
description: Turns the gate result into the decision card shown to operations, using only approved Vietnamese templates. The model's own explanation is kept for audit but never shown as the final wording.
---

# compose-recommendation

**Runs:** always. **Calls a model:** no.

## Input
- `state.gate`, `state.assessment` (may be missing if the AI step failed), `state.policy.question_templates`.

## Output
- `state.decision`: a `Decision` (see `runtime/models.py`).

## Wording rules
- The card text comes from the templates in `skill.py` (`HEADLINES`, `REASONS`, `CAUSES`) and `policy.question_templates`.
- The model's `explanation` is stored in `decision.model_explanation` for audit only. It is never shown on the card, so the model cannot put blame or promises in front of operations.
- Every decision carries the labels **Dữ liệu giả lập · Luật minh họa · Kết quả mô phỏng**, plus the mode (`REPLAY` or `LIVE_AI`).

## Next owner
| Action | `next_owner` |
|---|---|
| `CLARIFY`, `NO_ACTION` | `buyer_reply_pending` |
| `HOLD` | `system_reassess` |
| `STANDARD_RETRY`, `HUMAN_REVIEW` | `operations` |
| `CLOSE` | `none` |
