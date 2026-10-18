import pytest


@pytest.fixture(autouse=True)
def isolated_runs_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ORDER_RESCUE_RUNS_DIR", str(tmp_path / "runs"))
