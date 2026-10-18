from runtime.models import Evidence, Event, PipelineState

RUNS_WHEN_HALTED = False

DERIVED = {
    "BUYER_REPLY": ("BUYER_REPLY", "buyer"),
    "ADDRESS_CHANGE_REQUEST": ("BUYER_REPLY", "buyer"),
    "DISRUPTION_RESOLVED": ("DISRUPTION_UPDATE", "disruption_feed"),
    "NO_REPLY_TIMEOUT": ("CONTACT_LOG", "contact_system"),
}

FACT_FIELDS = [
    "failure_status", "failed_at", "attempts_used", "return_state", "deadline",
    "service_area", "payment", "address_complete", "buyer_contactable",
]


def evidence_from_event(event: Event) -> Evidence | None:
    if event.type not in DERIVED:
        return None
    ev_type, source = DERIVED[event.type]
    return Evidence(
        id=f"EV-{event.event_id}",
        type=ev_type,
        source=source,
        observed_at=event.occurred_at,
        text=event.payload.get("text", ""),
        data={k: v for k, v in event.payload.items() if k != "text"},
    )


def run(state: PipelineState) -> PipelineState:
    run_state = state.run
    items = [e for e in run_state.case.evidence if e.observed_at <= run_state.now]
    items += [ev for ev in map(evidence_from_event, run_state.applied_events) if ev]

    state.evidence_index = {e.id: e for e in items}
    facts = run_state.facts.model_dump(mode="json")
    state.snapshot = {
        "case_id": run_state.case.case_id,
        "now": run_state.now.isoformat(),
        "policy_version": state.policy["policy_version"],
        "max_attempts": state.policy["max_attempts"],
        "facts": {k: facts[k] for k in FACT_FIELDS},
        "evidence": [e.model_dump(mode="json") for e in items],
        "question_state": {
            "questions_asked": run_state.questions_asked,
            "max_questions": state.policy["max_buyer_questions"],
            "question_key": run_state.question_key,
            "reply_deadline": run_state.question_deadline.isoformat() if run_state.question_deadline else None,
        },
    }
    return state
