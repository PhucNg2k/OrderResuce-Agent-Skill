"""Presenter-side simulator: loads fixtures, applies events, moves the virtual clock.

It supplies facts and events. The pipeline decides what to recommend.
"""
from __future__ import annotations

import json
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional

from runtime.models import CaseFile, Decision, Event, PipelineState, RunState
from runtime.pipeline import run_pipeline

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class Simulator:
    def __init__(self, mode: str = "REPLAY", policy_version: str = "demo-v1",
                 replay_overrides: Optional[dict[str, dict]] = None):
        self.mode = mode
        self.policy = read_json(FIXTURES / "policies" / f"{policy_version}.json")
        self.replay_overrides = replay_overrides or {}
        self.runs: dict[str, RunState] = {}
        self.decisions: dict[str, list[Decision]] = {}

    # ---------- presenter controls ----------

    def list_cases(self) -> list[dict]:
        cases = [CaseFile.model_validate(read_json(p)) for p in sorted((FIXTURES / "scenarios").glob("*.json"))]
        return [{"case_id": c.case_id, "title": c.title,
                 "events": [{"event_id": e.event_id, "type": e.type} for e in c.prepared_events]} for c in cases]

    def start(self, case_id: str, case: Optional[CaseFile] = None) -> tuple[RunState, Decision]:
        """Select (or reset) a case: new run ID, clock at case start, first assessment."""
        case = case or CaseFile.model_validate(read_json(FIXTURES / "scenarios" / f"{case_id.lower()}.json"))
        run = RunState(run_id=f"{case.case_id}-{uuid.uuid4().hex[:6]}", case=case,
                       facts=case.facts.model_copy(deep=True), now=case.start_time)
        self.runs[run.run_id] = run
        self.decisions[run.run_id] = []
        return run, self._assess(run, trigger="START")

    def apply_event(self, run_id: str, event_id: str) -> Optional[Decision]:
        """Apply a prepared event (buyer reply, disruption resolved, ...). Duplicates are ignored."""
        run = self.runs[run_id]
        event = next((e for e in run.case.prepared_events if e.event_id == event_id), None)
        if event is None:
            raise KeyError(f"{event_id} is not a prepared event of {run.case.case_id}")
        return self._apply(run, event)

    def advance(self, run_id: str, minutes: int) -> list[Decision]:
        """Move the virtual clock. May fire a reply timeout or a deadline event."""
        run = self.runs[run_id]
        run.now += timedelta(minutes=minutes)
        out = []
        if (run.questions_asked and not run.replied_after_question and not run.timeout_fired
                and run.question_deadline and run.now >= run.question_deadline):
            out.append(self._apply(run, Event(
                event_id=f"{run.case.case_id}-TIMEOUT", type="NO_REPLY_TIMEOUT",
                occurred_at=run.question_deadline, source="virtual_clock",
                payload={"text": "Không có phản hồi trong thời hạn chờ (giả lập)."})))
        if run.facts.deadline and run.now >= run.facts.deadline:
            out.append(self._apply(run, Event(
                event_id=f"{run.case.case_id}-DEADLINE", type="DEADLINE_REACHED",
                occurred_at=run.facts.deadline, source="virtual_clock")))
        return [d for d in out if d]

    def history(self, run_id: str) -> list[Decision]:
        return self.decisions[run_id]

    # ---------- internals ----------

    def _apply(self, run: RunState, event: Event) -> Optional[Decision]:
        if any(e.event_id == event.event_id for e in run.applied_events):
            return None
        run.now = max(run.now, event.occurred_at)
        if event.type == "RETURN_STARTED":
            run.facts.return_state = "STARTED"
        if event.type in ("BUYER_REPLY", "ADDRESS_CHANGE_REQUEST") and run.questions_asked:
            run.replied_after_question = True
        if event.type == "NO_REPLY_TIMEOUT":
            run.timeout_fired = True
        run.applied_events.append(event)
        requested = [event.payload["requested_action"]] if "requested_action" in event.payload else []
        return self._assess(run, trigger=event.event_id, requested=requested)

    def _assess(self, run: RunState, trigger: str, requested: Optional[list[str]] = None) -> Decision:
        case_id = run.case.case_id
        replay_path = FIXTURES / "replay" / f"{case_id.lower()}.json"
        if case_id in self.replay_overrides:
            replay = self.replay_overrides[case_id]
        else:
            replay = read_json(replay_path) if replay_path.exists() else {}
        state = PipelineState(
            run=run, policy=self.policy, mode=self.mode, trigger=trigger,
            replay_key="+".join(["START"] + [e.event_id for e in run.applied_events]),
            replay_store=replay, requested_actions=requested or [],
        )
        decision = run_pipeline(state).decision
        if decision.action == "CLARIFY":
            run.questions_asked += 1
            run.question_key = decision.question_key
            run.question_deadline = run.now + timedelta(minutes=self.policy["response_window_minutes"])
            run.replied_after_question = False
        self.decisions[run.run_id].append(decision)
        return decision
