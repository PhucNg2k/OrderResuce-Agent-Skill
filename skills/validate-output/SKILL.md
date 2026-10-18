---
name: validate-output
description: Checks the AI assessment against the evidence and the team's confidence rules. Rejects invented references, unsupported quotes and prohibited wording; caps confidence the evidence cannot justify.
---

# validate-output

**Runs:** after `assess-case`. **Calls a model:** no.

## Input
- `state.assessment`, `state.evidence_index`, `state.policy`.

## Output
- Rejects the output (`HUMAN_REVIEW`) or passes it on.
- May lower `state.assessment.confidence`. Every change is recorded in `state.validation_issues`.

## Rejected (case goes to operations)

| Check | Reason code |
|---|---|
| A supporting or conflicting ID is not in the snapshot | `invalid_evidence_reference` |
| A claim cites an ID it did not list as supporting or conflicting | `invalid_evidence_reference` |
| A claim's `quote` is not in the cited evidence text | `unsupported_claim` |
| `CLARIFY` without a `question_key` | `missing_question_key` |
| Explanation or claim matches `policy.prohibited_patterns` (blame, promises) | `prohibited_wording` |

## Confidence cap (code decides the ceiling, the model cannot exceed it)
1. Count distinct `source` values in supporting evidence: 2 or more → HIGH, 1 → MEDIUM, 0 → LOW.
2. Any conflicting evidence → at most MEDIUM.
3. `policy.confirmation_required[cause]` lists evidence types; if none is in the supporting set → at most MEDIUM. Example: a temporary absence needs a `BUYER_REPLY`, so buyer history alone cannot reach HIGH.

If the model claimed more than the cap, confidence is lowered and `confidence_capped:<FROM>-><TO>` is recorded.
