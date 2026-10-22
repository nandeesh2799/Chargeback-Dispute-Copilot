import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["dispute_source"] == "mock"


def test_dashboard_summary():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_disputes"] == 50
    assert "urgent_queue" in data
    assert data["win_rate_percentage"] >= 0.0


def test_disputes_list_and_filter():
    res = client.get("/api/disputes?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 10
    assert "id" in data[0]

    # Filter by reason
    res_filter = client.get("/api/disputes?reason=product_not_received")
    assert res_filter.status_code == 200
    for item in res_filter.json():
        assert item["reason_code"] == "product_not_received"


def test_dispute_detail():
    res = client.get("/api/disputes?limit=1")
    disp_id = res.json()[0]["id"]

    res_detail = client.get(f"/api/disputes/{disp_id}")
    assert res_detail.status_code == 200
    data = res_detail.json()
    assert data["id"] == disp_id
    assert "order" in data
    assert "payment" in data
    assert "customer" in data


def test_investigation_and_scoring_flow():
    res = client.get("/api/disputes?limit=1")
    disp_id = res.json()[0]["id"]

    # Trigger investigation
    res_inv = client.post(f"/api/disputes/{disp_id}/investigate")
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    assert inv_data["investigation_status"] == "completed"
    assert "checklist_audit" in inv_data

    # Calculate score
    res_score = client.post(f"/api/disputes/{disp_id}/score")
    assert res_score.status_code == 200
    score_data = res_score.json()
    assert 0.0 <= score_data["score"] <= 100.0
    assert "top_positive_factors" in score_data


def test_draft_edit_validation():
    res = client.get("/api/disputes?limit=1")
    disp_id = res.json()[0]["id"]

    # Valid draft update
    res_patch = client.patch(f"/api/disputes/{disp_id}/draft", json={
        "contest_summary": "Merchant verified delivery via OTP with carrier Dunzo Express.",
        "representation_letter": "Detailed formal representation rebuttal."
    })
    assert res_patch.status_code == 200
    assert res_patch.json()["contest_summary"] == "Merchant verified delivery via OTP with carrier Dunzo Express."

    # Invalid draft exceeding 1000 chars should fail with validation error (422 / 400)
    res_invalid = client.patch(f"/api/disputes/{disp_id}/draft", json={
        "contest_summary": "x" * 1001,
        "representation_letter": "Letter"
    })
    assert res_invalid.status_code in [400, 422]


def test_pdf_report_generation():
    res = client.get("/api/disputes?limit=1")
    disp_id = res.json()[0]["id"]

    res_pdf = client.get(f"/api/disputes/{disp_id}/report")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000
