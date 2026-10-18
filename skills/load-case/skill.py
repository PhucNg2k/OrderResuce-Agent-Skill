from runtime.models import PipelineState

RUNS_WHEN_HALTED = False


def run(state: PipelineState) -> PipelineState:
    facts, policy, now = state.run.facts, state.policy, state.run.now

    if facts.delivered:
        state.escalate("already_delivered", status="CLOSED", action="CLOSE")
    elif facts.policy_version != policy["policy_version"]:
        state.escalate("policy_version_mismatch")
    elif facts.return_state == "STARTED":
        state.escalate("return_in_progress")
    elif facts.return_state == "UNKNOWN":
        state.escalate("return_state_unknown")
    elif facts.deadline is None:
        state.escalate("deadline_unknown")
    elif now >= facts.deadline:
        state.escalate("deadline_expired")
    elif facts.attempts_used >= policy["max_attempts"]:
        state.escalate("attempts_exhausted")
    return state
