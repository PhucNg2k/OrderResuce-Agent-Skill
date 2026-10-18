import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from runtime.api import app  # noqa: E402


def test_presenter_flow_over_http():
    client = TestClient(app)
    assert len(client.get("/cases").json()) == 5

    run = client.post("/runs", json={"case_id": "CASE-01"}).json()
    assert run["history"][0]["action"] == "CLARIFY"

    run = client.post(f"/runs/{run['run_id']}/events", json={"event_id": "C01-E02"}).json()
    assert [d["action"] for d in run["history"]] == ["CLARIFY", "STANDARD_RETRY"]

    assert client.post(f"/runs/{run['run_id']}/events", json={"event_id": "NOPE"}).status_code == 400


def test_ui_page_and_run_view_for_the_ui():
    client = TestClient(app)
    assert "Order Rescue" in client.get("/").text
    run = client.post("/runs", json={"case_id": "CASE-04"}).json()
    assert {e["id"] for e in run["evidence"]} == {"EV-04-SIG", "EV-04-NOTE", "EV-04-CLUSTER"}
    assert run["events"][0]["label"] == "Cảnh báo ngập được gỡ"
    assert run["history"][0]["skills_run"][-1] == "audit-log"
