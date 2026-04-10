from app.tests.conftest import API_HEADERS


VALID_PAYLOAD = {
    "customer_id": 1,
    "product_id": 10,
    "channel": "email",
    "message": "Charged twice for my order",
    "event_date": "2026-04-01",
}


def test_create_feedback_success(client):
    response = client.post("/api/v1/feedback", json=VALID_PAYLOAD, headers=API_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert data["product_id"] == 10
    assert data["channel"] == "email"
    assert data["sentiment"] is not None
    assert data["issue_label"] is not None


def test_create_feedback_sets_billing_label(client):
    payload = {**VALID_PAYLOAD, "message": "I was charged twice for my subscription"}
    response = client.post("/api/v1/feedback", json=payload, headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json()["issue_label"] == "billing"


def test_create_feedback_sets_support_label(client):
    payload = {**VALID_PAYLOAD, "message": "Support never responded to my ticket"}
    response = client.post("/api/v1/feedback", json=payload, headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json()["issue_label"] == "support"


def test_create_feedback_missing_api_key(client):
    response = client.post("/api/v1/feedback", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_create_feedback_wrong_api_key(client):
    response = client.post(
        "/api/v1/feedback", json=VALID_PAYLOAD, headers={"X-Api-Key": "wrong"}
    )
    assert response.status_code == 401


def test_create_feedback_missing_required_field(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "message"}
    response = client.post("/api/v1/feedback", json=payload, headers=API_HEADERS)
    assert response.status_code == 422


def test_create_feedback_message_too_short(client):
    payload = {**VALID_PAYLOAD, "message": "ok"}
    response = client.post("/api/v1/feedback", json=payload, headers=API_HEADERS)
    assert response.status_code == 422
