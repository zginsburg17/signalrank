from app.tests.conftest import API_HEADERS


def _post_feedback(client, message: str, channel: str = "email"):
    return client.post(
        "/api/v1/feedback",
        json={
            "customer_id": 1,
            "product_id": 10,
            "channel": channel,
            "message": message,
            "event_date": "2026-04-01",
        },
        headers=API_HEADERS,
    )


def test_issues_empty(client):
    response = client.get("/api/v1/insights/issues", headers=API_HEADERS)
    assert response.status_code == 200
    assert response.json() == []


def test_issues_ranked_by_negative_mentions(client):
    # Create 2 billing (negative) and 1 support (negative).
    _post_feedback(client, "Charged twice for my order")
    _post_feedback(client, "Billed for a plan I never signed up for")
    _post_feedback(client, "Support never responded to my ticket")

    response = client.get("/api/v1/insights/issues", headers=API_HEADERS)
    assert response.status_code == 200
    issues = response.json()

    labels = [i["issue_label"] for i in issues]
    # billing has 2 negative mentions so should rank first
    assert labels[0] == "billing"
    assert "support" in labels


def test_issues_response_shape(client):
    _post_feedback(client, "Onboarding was confusing")
    response = client.get("/api/v1/insights/issues", headers=API_HEADERS)
    assert response.status_code == 200
    item = response.json()[0]
    assert "issue_label" in item
    assert "total_mentions" in item
    assert "negative_mentions" in item
    assert "channels" in item
    assert isinstance(item["channels"], list)


def test_issues_missing_api_key(client):
    response = client.get("/api/v1/insights/issues")
    assert response.status_code == 401
