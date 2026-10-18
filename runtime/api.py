"""HTTP API for the demo UI (optional extra: `uv sync --extra api`).

    uvicorn runtime.api:app --reload
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from runtime.pipeline import PIPELINE, load_skill
from runtime.simulator import Simulator

UI_FILE = Path(__file__).parent / "static" / "index.html"

app = FastAPI(title="Order Rescue prototype", description="Synthetic data · Demo policy · Simulated outcome")
sim = Simulator(mode=os.getenv("ORDER_RESCUE_MODE", "REPLAY"))


class StartBody(BaseModel):
    case_id: str


class EventBody(BaseModel):
    event_id: str


class AdvanceBody(BaseModel):
    minutes: int


def run_view(run_id: str) -> dict:
    run = sim.runs[run_id]
    to_evidence = load_skill("build-evidence").evidence_from_event
    applied = {e.event_id for e in run.applied_events}
    evidence = [e for e in run.case.evidence if e.observed_at <= run.now]
    evidence += [ev for ev in map(to_evidence, run.applied_events) if ev]
    return {
        "run_id": run_id,
        "case_id": run.case.case_id,
        "title": run.case.title,
        "mode": sim.mode,
        "now": run.now,
        "facts": run.facts,
        "question": {"asked": run.questions_asked, "key": run.question_key,
                     "deadline": run.question_deadline, "replied": run.replied_after_question},
        "evidence": evidence,
        "events": [{"event_id": e.event_id, "label": e.label or e.type, "type": e.type,
                    "applied": e.event_id in applied} for e in run.case.prepared_events],
        "applied_events": [e.event_id for e in run.applied_events],
        "pipeline": PIPELINE,
        "history": sim.history(run_id),
    }


@app.get("/", response_class=HTMLResponse)
def ui():
    return UI_FILE.read_text(encoding="utf-8")


@app.get("/cases")
def list_cases():
    return sim.list_cases()


@app.post("/runs")
def start_run(body: StartBody):
    try:
        run, _ = sim.start(body.case_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Unknown case {body.case_id}")
    return run_view(run.run_id)


@app.post("/runs/{run_id}/events")
def apply_event(run_id: str, body: EventBody):
    if run_id not in sim.runs:
        raise HTTPException(404, "Unknown run")
    try:
        sim.apply_event(run_id, body.event_id)
    except KeyError as exc:
        raise HTTPException(400, str(exc))
    return run_view(run_id)


@app.post("/runs/{run_id}/advance")
def advance(run_id: str, body: AdvanceBody):
    if run_id not in sim.runs:
        raise HTTPException(404, "Unknown run")
    sim.advance(run_id, body.minutes)
    return run_view(run_id)


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in sim.runs:
        raise HTTPException(404, "Unknown run")
    return run_view(run_id)
