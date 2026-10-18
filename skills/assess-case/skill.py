import json
import os
from pathlib import Path

from pydantic import ValidationError

from runtime.models import Assessment, PipelineState

RUNS_WHEN_HALTED = False
PROMPT_VERSION = "assess-v1"
PROMPT = (Path(__file__).parent / "prompt.md").read_text(encoding="utf-8")
REPLAY_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "replay"


class ModelError(Exception):
    pass


def call_model(snapshot: dict) -> tuple[Assessment, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:  # optional dependency: `uv sync --extra live`
        raise ModelError("model_unavailable") from exc

    model = os.getenv("ORDER_RESCUE_MODEL", "gpt-5.4-mini")
    try:
        client = OpenAI(timeout=float(os.getenv("ORDER_RESCUE_TIMEOUT", "20")))
        response = client.responses.parse(
            model=model,
            instructions=PROMPT,
            input=json.dumps(snapshot, ensure_ascii=False),
            text_format=Assessment,
        )
    except ValidationError as exc:
        raise ModelError("invalid_model_output") from exc
    except Exception as exc:  # network, auth, timeout, rate limit
        raise ModelError("model_unavailable") from exc
    if response.output_parsed is None:
        raise ModelError("model_refused_or_empty")
    return response.output_parsed, model


def record_replay(state: PipelineState, assessment: Assessment, model: str) -> None:
    path = REPLAY_DIR / f"{state.run.case.case_id.lower()}.json"
    store = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    store[state.replay_key] = {
        "source": "live_model",
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_version": state.policy["policy_version"],
        "output": assessment.model_dump(mode="json"),
    }
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def from_replay(state: PipelineState) -> Assessment:
    entry = state.replay_store.get(state.replay_key)
    if entry is None:
        raise ModelError("replay_missing")
    if entry.get("prompt_version") != PROMPT_VERSION or entry.get("policy_version") != state.policy["policy_version"]:
        raise ModelError("replay_version_mismatch")
    state.model_info.update(model=entry.get("model"), replay_source=entry.get("source"))
    try:
        return Assessment.model_validate(entry["output"])
    except ValidationError as exc:
        raise ModelError("invalid_model_output") from exc


def run(state: PipelineState) -> PipelineState:
    state.model_info = {"mode": state.mode, "prompt_version": PROMPT_VERSION, "replay_key": state.replay_key}
    try:
        if state.mode == "LIVE_AI":
            state.assessment, model = call_model(state.snapshot)
            state.model_info["model"] = model
            if os.getenv("ORDER_RESCUE_RECORD") == "1":
                record_replay(state, state.assessment, model)
        else:
            state.assessment = from_replay(state)
    except ModelError as exc:
        state.escalate(str(exc))
    return state
