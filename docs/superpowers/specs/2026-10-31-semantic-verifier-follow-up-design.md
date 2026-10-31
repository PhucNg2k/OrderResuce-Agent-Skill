# Semantic verifier follow-up design

## Goal

Keep the semantic verifier responsible for checking whether proposed buyer facts are supported, while the harness policy remains responsible for the final action. When verification leaves a buyer-resolvable prerequisite uncertain and a clarification round remains, ask one targeted follow-up instead of ending the run immediately in review.

## Behavior

- Retry permission still requires verifier support for current intent, receiving availability, and COD readiness when applicable.
- Address and refusal remain safety checks. A new `NOT_PRESENT` verifier verdict means no address-change request or refusal appears in the complete supplied conversation; it does not claim an address value or intent fact. It is valid only for address/refusal checks whose proposed state is neutral.
- If a retry prerequisite is unsupported or uncertain, the harness never permits `STANDARD_REATTEMPT` from that assessment.
- If only buyer-resolvable prerequisite facts are uncertain, another round is allowed, and contact remains appropriate, a dedicated VoltAgent question-generation call may produce one approved-topic question. The original assessment and verifier result remain unchanged and are separately recorded in history.
- No question is generated for lifecycle, disruption, address change, direct refusal, or other operational facts. Without a suitable buyer question or remaining budget, final action is `ESCALATE_REVIEW`.
- Relative schedule language is interpreted against the current assessment timestamp. The deterministic deadline precheck is rerun for assessments, buyer replies, manual retries, and no-reply finalization; an expired deadline cannot be restored by buyer intent.
- Each generated question is bounded to 240 characters and counts toward the existing two-question total. It uses the existing three-assessment maximum; question generation is an additional model call and does not create an assessment turn.

## Persistence and audit

Keep the assessor output, candidate policy, verifier result, and verifier override immutable in the assessment history. Store the generated question and its model metadata in separate follow-up fields on that history record and normal interaction record. Finalization selects the newest assessed result and the matching effective policy; it does not rewrite the assessment to say it proposed clarification.

## Failure handling

Question-generation errors, malformed output, invalid question keys, overlong text, or no useful buyer question fail closed to human review. They never permit a retry or fabricate a question.

## Verification

Use deterministic assessor, verifier, and question-generator stubs to cover a verifier-uncertain reply with a remaining round, a successful supported retry, exhausted question budget, and question-generation failure. Live provider verification is unavailable because the plan's 12-request cap is exhausted.
