from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_agent_card_has_identity_and_capabilities():
    card = client.get("/.well-known/agent-card.json").json()
    for key in ("agent_id", "group_id", "domain", "capabilities", "endpoint", "status"):
        assert key in card
    assert "plan_trip" in card["capabilities"]


def test_plan_one_day_history():
    r = client.post("/v1/tasks", json={"days": 1, "travelers": 2, "interests": ["history"]})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    stops = body["result"]["itinerary"][0]["stops"]
    assert len(stops) >= 2
    assert body["result"]["itinerary"][0]["total_minutes"] <= 480


def test_correlation_id_is_echoed():
    r = client.post("/v1/tasks", json={"days": 1}, headers={"X-Correlation-ID": "abc-123"})
    assert r.headers["X-Correlation-ID"] == "abc-123"
    assert r.json()["correlation_id"] == "abc-123"


def test_budget_adjustment_makes_plan_cheaper():
    base = client.post("/v1/tasks", json={"days": 2, "travelers": 2, "interests": ["history"]}).json()["result"]
    tight = client.post("/v1/tasks", json={"days": 2, "travelers": 2, "interests": ["history"],
                                           "budget_vnd": 600000}).json()["result"]
    assert tight["cost"]["total_vnd"] <= base["cost"]["total_vnd"]


def test_invalid_days_rejected():
    assert client.post("/v1/tasks", json={"days": 9}).status_code == 422
