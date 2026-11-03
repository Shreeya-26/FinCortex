GOOD = {"salary": 80000, "rent": 22000, "food": 9000, "transport": 4000, "emi": 12000,
        "other_expenses": 8000, "existing_savings": 120000, "risk_appetite": "Medium"}


def test_health_reports_model(client):
    assert client.get("/health").json()["model_loaded"] is True


def test_analyze_returns_score_and_advice(client):
    r = client.post("/analyze", json=GOOD)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert body["verdict"] in {"Healthy", "Fair", "Needs attention"}
    assert sum(body["allocation"].values()) == 100
    assert any("emergency" in w.lower() for w in body["warnings"])   # 120k < 3 months of 55k


def test_better_habits_score_higher(client):
    risky = {**GOOD, "salary": 30000, "rent": 12000, "emi": 12000, "existing_savings": 0}
    assert client.post("/analyze", json=GOOD).json()["score"] > client.post("/analyze", json=risky).json()["score"]


def test_invalid_input_is_rejected(client):
    assert client.post("/analyze", json={**GOOD, "salary": 0}).status_code == 422
    assert client.post("/analyze", json={**GOOD, "rent": -5}).status_code == 422
    assert client.post("/analyze", json={**GOOD, "risk_appetite": "Wild"}).status_code == 422


def test_history_saves_and_deletes(client):
    first = client.post("/analyze", json=GOOD).json()
    client.post("/analyze", json=GOOD)
    items = client.get("/history").json()
    assert len(items) == 2 and items[0]["id"] > items[1]["id"]      # newest first
    assert client.delete(f"/history/{first['id']}").status_code == 204
    assert len(client.get("/history").json()) == 1
    assert client.delete("/history/9999").status_code == 404


def test_absurd_numbers_are_rejected(client):
    assert client.post("/analyze", json={**GOOD, "salary": 10**12}).status_code == 422
    assert client.post("/analyze", json={**GOOD, "existing_savings": 10**12}).status_code == 422
    # expenses of 1,00,000 x 3+ the salary are almost certainly a typo
    assert client.post("/analyze", json={**GOOD, "rent": 500000}).status_code == 422
    assert client.get("/history").json() == []          # nothing bad was saved


def test_cors_follows_settings(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app.main import app
    monkeypatch.setenv("FINCORTEX_DB", str(tmp_path / "t.db"))
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://my-app.vercel.app/")
    from app import config
    assert config.allowed_origins() == ["https://my-app.vercel.app"]       # trailing slash removed
    monkeypatch.delenv("ALLOWED_ORIGINS")
    assert "http://localhost:3000" in config.allowed_origins()             # safe default for local use
    with TestClient(app) as c:
        ok = c.options("/analyze", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
        bad = c.options("/analyze", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-origin" not in bad.headers


def test_why_this_score_names_the_real_problems(client):
    body = client.post("/analyze", json=GOOD).json()       # 1.8 months saved, 15% EMI
    names = [r["factor"] for r in body["reasons"]]
    assert "Emergency fund" in names
    assert [r["points"] for r in body["reasons"]] == sorted((r["points"] for r in body["reasons"]), reverse=True)
    assert all(r["points"] >= 2 for r in body["reasons"])
    assert body["biggest_win"]["projected_score"] > body["score"]


def test_heavy_emi_is_flagged_and_a_healthy_profile_has_no_big_problems(client):
    heavy = {**GOOD, "emi": 40000, "existing_savings": 500000}
    assert "Loan EMIs" in [r["factor"] for r in client.post("/analyze", json=heavy).json()["reasons"]]
    great = {"salary": 100000, "rent": 15000, "food": 8000, "transport": 3000, "emi": 5000,
             "other_expenses": 5000, "existing_savings": 900000, "risk_appetite": "Medium"}
    body = client.post("/analyze", json=great).json()
    assert body["reasons"] == [] and body["biggest_win"] is None


def test_overspender_gets_reasons_without_errors(client):
    broke = {**GOOD, "salary": 30000, "rent": 20000, "emi": 15000, "existing_savings": 0}
    r = client.post("/analyze", json=broke)
    assert r.status_code == 200 and len(r.json()["reasons"]) >= 2
