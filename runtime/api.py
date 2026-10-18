"""HTTP API for the demo UI (optional extra: `uv sync --extra api`).

    uvicorn runtime.api:app --reload
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from runtime.simulator import Simulator

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
    return {
        "run_id": run_id,
        "case_id": run.case.case_id,
        "now": run.now,
        "applied_events": [e.event_id for e in run.applied_events],
        "history": sim.history(run_id),
    }


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
