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
