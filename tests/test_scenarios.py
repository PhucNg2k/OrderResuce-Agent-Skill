"""The five demo cases, played from fixtures/expected/*.json in REPLAY mode."""
import json

import pytest

from runtime.simulator import FIXTURES, Simulator

SCRIPTS = [
    (path.stem.upper(), script)
    for path in sorted((FIXTURES / "expected").glob("*.json"))
    for script in json.loads(path.read_text(encoding="utf-8"))["scripts"]
]


def check(decision, expect):
    for field, value in expect.items():
        actual = getattr(decision, field)
        if field == "reasons":
            assert set(value) <= set(actual), f"reasons {actual} missing {value}"
        else:
            assert actual == value, f"{field}: expected {value}, got {actual}\n{decision.message_vi}"


@pytest.mark.parametrize("case_id,script", SCRIPTS, ids=[f"{c}:{s['name']}" for c, s in SCRIPTS])
def test_demo_script(case_id, script):
    sim = Simulator()
    run, decision = sim.start(case_id)
    check(decision, script["start"])
    for step in script["steps"]:
        if "apply" in step:
            decisions = [sim.apply_event(run.run_id, step["apply"])]
        else:
            decisions = sim.advance(run.run_id, step["advance_minutes"])
        if step["expect"] is None:
            assert decisions == []
        else:
            check(decisions[-1], step["expect"])


def test_same_status_different_recommendations():
    """Core demo message: cases 1-4 share a status but get different first steps."""
    sim = Simulator()
    firsts = {cid: sim.start(cid)[1] for cid in ["CASE-01", "CASE-02", "CASE-03", "CASE-04"]}
    statuses = {sim.runs[d.run_id].facts.failure_status for d in firsts.values()}
    assert statuses == {"RECIPIENT_UNAVAILABLE"}
    signatures = {(d.action, d.cause, d.question_key) for d in firsts.values()}
    assert len(signatures) == 4


def test_audit_log_is_append_only_and_complete():
    from importlib import import_module  # noqa: F401
    from runtime.pipeline import load_skill

    sim = Simulator()
    run, _ = sim.start("CASE-01")
    sim.apply_event(run.run_id, "C01-E02")
    history = load_skill("audit-log").read_history(run.run_id)
    assert [h["action"] for h in history] == ["CLARIFY", "STANDARD_RETRY"]
    for entry in history:
        for key in ["decision_id", "trigger", "decided_at", "cause", "confidence", "evidence_ids",
                    "reasons", "next_owner", "policy_version", "model_info", "skills_run", "labels"]:
            assert key in entry
        assert "Dữ liệu giả lập" in entry["labels"]
