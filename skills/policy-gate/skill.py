from datetime import timedelta

from runtime.models import GateResult, PipelineState
from runtime.pipeline import load_skill

RUNS_WHEN_HALTED = True


def active_disruption(state: PipelineState) -> bool:
    items = state.evidence_index.values()
    area = state.run.facts.service_area
    resolved = {e.data.get("signal_id") for e in items
                if e.type == "DISRUPTION_UPDATE" and e.data.get("status") == "RESOLVED"}
    return any(e.type == "DISRUPTION_SIGNAL" and e.data.get("area") == area
               and e.data.get("status") == "ACTIVE" and e.id not in resolved for e in items)


def waiting_for_reply(state: PipelineState) -> bool:
    r = state.run
    return (r.questions_asked > 0 and not r.replied_after_question
            and r.question_deadline is not None and r.now < r.question_deadline)


def check_preconditions(state: PipelineState) -> GateResult:
    a, policy, r = state.assessment, state.policy, state.run
    action = a.proposed_action
    review = lambda *reasons: GateResult(status="ESCALATED", action="HUMAN_REVIEW", reasons=list(reasons))

    if action == "CLARIFY":
        if r.questions_asked >= policy["max_buyer_questions"]:
            if waiting_for_reply(state):
                return GateResult(status="ALLOWED", action="NO_ACTION", reasons=["waiting_for_reply"],
                                  reassess_at=r.question_deadline)
            return review("question_limit_reached")
        if not r.facts.buyer_contactable:
            return review("buyer_not_contactable")
        if a.question_key not in policy["question_templates"]:
            return review("question_not_approved")
        return GateResult(status="ALLOWED", action="CLARIFY")

    if action == "STANDARD_RETRY":
        failures = []
        if a.confidence != "HIGH":
            failures.append("confidence_not_high")
        if a.cause not in policy["retry_allowed_causes"]:
            failures.append("cause_not_retryable")
        if active_disruption(state):
            failures.append("disruption_active")
        if r.facts.address_complete is not True:
            failures.append("location_unclear")
        if failures:
            return review(*(f"retry_blocked:{f}" for f in failures))
        return GateResult(status="ALLOWED", action="STANDARD_RETRY")

    if action == "HOLD":
        if not active_disruption(state):
            return review("no_active_disruption")
        return GateResult(status="ALLOWED", action="HOLD",
                          reassess_at=r.now + timedelta(minutes=policy["hold_reassess_minutes"]))

    if action == "NO_ACTION":
        if not waiting_for_reply(state):
            return review("no_open_response_window")
        return GateResult(status="ALLOWED", action="NO_ACTION", reasons=["waiting_for_reply"],
                          reassess_at=r.question_deadline)

    return review("handoff_proposed")


def run(state: PipelineState) -> PipelineState:
    policy = state.policy
    proposed = [state.assessment.proposed_action] if state.assessment else []
    blocked = [x for x in state.requested_actions + proposed if x in policy["always_blocked"]]

    # 1. Always-blocked actions. Recorded even when an earlier step already halted.
    if blocked:
        reasons = [f"blocked_action:{x}" for x in blocked]
        if state.gate is None:
            state.gate = GateResult(status="BLOCKED", action="HUMAN_REVIEW", reasons=reasons)
        else:
            state.gate.reasons += reasons
            if state.gate.status != "CLOSED":
                state.gate.status, state.gate.action = "BLOCKED", "HUMAN_REVIEW"
        state.gate.blocked_actions = blocked
        state.halted = True
        return state
    if state.halted:
        return state

    # 2. Latest state, same checks as Gate 1.
    load_skill("load-case").run(state)
    if state.halted:
        return state

    # 3. Escalation conditions.
    a, r = state.assessment, state.run
    reasons = []
    if a.conflicting_evidence_ids:
        reasons.append("conflicting_evidence")
    if a.cause == "UNVERIFIED_REFUSAL":
        reasons.append("refusal_unverified")
    if r.timeout_fired and not r.replied_after_question:
        reasons.append("no_reply_after_question")
    if reasons:
        state.gate = GateResult(status="ESCALATED", action="HUMAN_REVIEW", reasons=reasons)
        return state

    # 4. Preconditions for the proposed step.
    state.gate = check_preconditions(state)
    return state
