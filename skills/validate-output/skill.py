import re
import unicodedata

from runtime.models import PipelineState, min_level

RUNS_WHEN_HALTED = False


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


def confidence_cap(state: PipelineState) -> str:
    a, index = state.assessment, state.evidence_index
    supporting = [index[i] for i in a.supporting_evidence_ids]
    sources = {e.source for e in supporting}
    cap = "HIGH" if len(sources) >= 2 else "MEDIUM" if sources else "LOW"
    if a.conflicting_evidence_ids:
        cap = min_level(cap, "MEDIUM")
    required = state.policy["confirmation_required"].get(a.cause)
    if required and not any(e.type in required for e in supporting):
        cap = min_level(cap, "MEDIUM")
    return cap


def rejection_reason(state: PipelineState) -> str | None:
    a, index = state.assessment, state.evidence_index
    cited = set(a.supporting_evidence_ids) | set(a.conflicting_evidence_ids)
    if not cited <= index.keys():
        return "invalid_evidence_reference"
    for claim in a.claims:
        if claim.evidence_id not in cited:
            return "invalid_evidence_reference"
        if normalize(claim.quote) not in normalize(index[claim.evidence_id].text):
            return "unsupported_claim"
    if a.proposed_action == "CLARIFY" and not a.question_key:
        return "missing_question_key"
    texts = [a.explanation] + [c.text for c in a.claims]
    for pattern in state.policy["prohibited_patterns"]:
        if any(re.search(pattern, normalize(t)) for t in texts):
            return "prohibited_wording"
    return None


def run(state: PipelineState) -> PipelineState:
    reason = rejection_reason(state)
    if reason:
        state.validation_issues.append(reason)
        state.escalate(reason)
        return state

    cap = confidence_cap(state)
    claimed = state.assessment.confidence
    if min_level(claimed, cap) != claimed:
        state.assessment.confidence = cap
        state.validation_issues.append(f"confidence_capped:{claimed}->{cap}")
    return state
