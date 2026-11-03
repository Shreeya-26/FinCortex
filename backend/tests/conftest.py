import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FINCORTEX_DB", str(tmp_path / "test.db"))   # fresh empty database per test
    with TestClient(app) as c:
        yield c
