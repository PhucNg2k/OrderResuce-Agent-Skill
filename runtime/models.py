"""Shared types for the Order Rescue pipeline.

Everything here is demo data. `synthetic` defaults to True on every input record.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Cause = Literal[
    "TEMPORARY_ABSENCE",
    "UNKNOWN_CONTACT_PROBLEM",
    "UNCLEAR_LOCATION",
    "DISRUPTION",
    "UNVERIFIED_REFUSAL",
    "UNKNOWN",
]
Level = Literal["LOW", "MEDIUM", "HIGH"]
Potential = Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
Action = Literal["CLARIFY", "STANDARD_RETRY", "HOLD", "HUMAN_REVIEW", "NO_ACTION"]
QuestionKey = Literal["CONFIRM_INTENT", "CLARIFY_LANDMARK"]

LEVEL_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def min_level(a: str, b: str) -> str:
    return a if LEVEL_ORDER[a] <= LEVEL_ORDER[b] else b


# ---------- Inputs (fixtures + events) ----------

class Evidence(BaseModel):
    id: str
    type: str
    source: str
    observed_at: datetime
    text: str
    data: dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True


class Event(BaseModel):
    event_id: str
    type: str
    occurred_at: datetime
    source: str = "presenter"
    label: Optional[str] = None  # button text for the presenter, never sent to the model
    payload: dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True


class CaseFacts(BaseModel):
    failure_status: str
    failed_at: datetime
    attempts_used: int
    return_state: Literal["NONE", "STARTED", "UNKNOWN"] = "NONE"
    delivered: bool = False
    deadline: Optional[datetime] = None
    service_area: str
    payment: str
    actor_role: str
    policy_version: str
    address_complete: Optional[bool] = None
    buyer_contactable: bool = True


class CaseFile(BaseModel):
    case_id: str
    title: str  # presenter-only, never sent to the model
    synthetic: bool = True
    start_time: datetime
    facts: CaseFacts
    evidence: list[Evidence]
    prepared_events: list[Event] = Field(default_factory=list)


# ---------- Model output ----------

class Claim(BaseModel):
    text: str
    evidence_id: str
    quote: str


class Assessment(BaseModel):
    cause: Cause
    supporting_evidence_ids: list[str]
    conflicting_evidence_ids: list[str]
    confidence: Level
    rescue_potential: Potential
    missing_information: list[str]
    question_key: Optional[QuestionKey]
    proposed_action: Action
    claims: list[Claim]
    explanation: str


# ---------- Pipeline state ----------

class RunState(BaseModel):
    """Mutable per-run case state. Only the simulator mutates it."""
    run_id: str
    case: CaseFile
    facts: CaseFacts
    now: datetime
    applied_events: list[Event] = Field(default_factory=list)
    questions_asked: int = 0
    question_key: Optional[str] = None
    question_deadline: Optional[datetime] = None
    replied_after_question: bool = False
    timeout_fired: bool = False


class GateResult(BaseModel):
    status: Literal["ALLOWED", "BLOCKED", "ESCALATED", "CLOSED"]
    action: str  # an Action or "CLOSE"
    reasons: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    reassess_at: Optional[datetime] = None


class Decision(BaseModel):
    decision_id: str
    run_id: str
    case_id: str
    trigger: str
    decided_at: datetime
    status: str
    action: str
    cause: Optional[str] = None
    confidence: Optional[str] = None
    rescue_potential: Optional[str] = None
    evidence_ids: list[str] = Field(default_factory=list)
    question_key: Optional[str] = None
    question_text: Optional[str] = None
    reasons: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    message_vi: str
    next_owner: str
    reassess_at: Optional[datetime] = None
    model_info: dict[str, Any] = Field(default_factory=dict)
    model_explanation: Optional[str] = None  # stored for audit, not shown on the card
    policy_version: str
    labels: list[str] = Field(default_factory=list)
    skills_run: list[str] = Field(default_factory=list)
    validation_issues: list[str] = Field(default_factory=list)


class PipelineState(BaseModel):
    """What flows through the skills for one assessment."""
    run: RunState
    policy: dict[str, Any]
    mode: Literal["REPLAY", "LIVE_AI"] = "REPLAY"
    trigger: str  # "START" or the event id that caused this assessment
    replay_key: str
    replay_store: dict[str, Any] = Field(default_factory=dict)
    requested_actions: list[str] = Field(default_factory=list)

    snapshot: Optional[dict[str, Any]] = None
    evidence_index: dict[str, Evidence] = Field(default_factory=dict)
    assessment: Optional[Assessment] = None
    model_info: dict[str, Any] = Field(default_factory=dict)
    validation_issues: list[str] = Field(default_factory=list)
    gate: Optional[GateResult] = None
    decision: Optional[Decision] = None

    halted: bool = False
    trace: list[str] = Field(default_factory=list)

    def escalate(self, reason: str, status: str = "ESCALATED", action: str = "HUMAN_REVIEW") -> None:
        """Stop the AI path and hand the case to operations with a reason."""
        if self.gate is None:
            self.gate = GateResult(status=status, action=action, reasons=[reason])
        else:
            self.gate.status, self.gate.action = status, action
            self.gate.reasons.append(reason)
        self.halted = True
