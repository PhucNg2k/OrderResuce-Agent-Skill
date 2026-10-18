import json
import os
from pathlib import Path

from runtime.models import PipelineState

RUNS_WHEN_HALTED = True


def runs_dir() -> Path:
    return Path(os.getenv("ORDER_RESCUE_RUNS_DIR", Path(__file__).resolve().parents[2] / "runs"))


def log_path(run_id: str) -> Path:
    return runs_dir() / run_id / "decisions.jsonl"


def read_history(run_id: str) -> list[dict]:
    path = log_path(run_id)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run(state: PipelineState) -> PipelineState:
    decision = state.decision
    if any(row["decision_id"] == decision.decision_id for row in read_history(decision.run_id)):
        return state

    entry = decision.model_dump(mode="json") | {
        "validation_issues": state.validation_issues,
        "skills_run": state.trace + ["audit-log"],
        "snapshot_evidence_ids": sorted(state.evidence_index),
    }
    path = log_path(decision.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return state
