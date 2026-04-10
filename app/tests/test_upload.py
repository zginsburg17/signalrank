import io
from app.tests.conftest import API_HEADERS


VALID_CSV = (
    "customer_id,product_id,channel,message,event_date\n"
    '1,10,email,"Charged twice for my order",2026-04-01\n'
    '2,10,chat,"Support took too long",2026-04-02\n'
    '3,11,email,"Onboarding was confusing",2026-04-03\n'
)


def _csv_file(content: str, filename: str = "feedback.csv"):
    return {"file": (filename, io.BytesIO(content.encode()), "text/csv")}


def test_upload_csv_success(client):
    response = client.post(
        "/api/v1/upload/csv", files=_csv_file(VALID_CSV), headers=API_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows_received"] == 3
    assert data["rows_processed"] == 3
    assert data["rows_failed"] == 0


def test_upload_csv_partial_failure(client):
    # Row 2 has a non-integer customer_id — should count as failed, not crash.
    bad_csv = (
        "customer_id,product_id,channel,message,event_date\n"
        '1,10,email,"Valid message here",2026-04-01\n'
        'abc,10,email,"Bad customer id",2026-04-01\n'
    )
    response = client.post(
        "/api/v1/upload/csv", files=_csv_file(bad_csv), headers=API_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows_received"] == 2
    assert data["rows_processed"] == 1
    assert data["rows_failed"] == 1


def test_upload_csv_missing_columns(client):
    bad_csv = "customer_id,product_id\n1,10\n"
    response = client.post(
        "/api/v1/upload/csv", files=_csv_file(bad_csv), headers=API_HEADERS
    )
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]


def test_upload_non_csv_rejected(client):
    response = client.post(
        "/api/v1/upload/csv",
        files={"file": ("data.txt", io.BytesIO(b"not a csv"), "text/plain")},
        headers=API_HEADERS,
    )
    assert response.status_code == 400


def test_upload_missing_api_key(client):
    response = client.post("/api/v1/upload/csv", files=_csv_file(VALID_CSV))
    assert response.status_code == 401
