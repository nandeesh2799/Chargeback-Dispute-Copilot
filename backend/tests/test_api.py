import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["dispute_source"] in ["mock", "razorpay"]


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


def test_disputes_list_total_count_header():
    res = client.get("/api/disputes?limit=5")
    assert res.status_code == 200
    assert "X-Total-Count" in res.headers
    assert int(res.headers["X-Total-Count"]) >= 50


def test_evidence_type_validation_and_sha256_hash():
    res = client.get("/api/disputes?limit=1")
    disp_id = res.json()[0]["id"]

    # 1. Valid evidence_type should NOT fall back to 'other'
    sample_content = b"PDF invoice mock content 12345"
    files = {"file": ("invoice.pdf", sample_content, "application/pdf")}
    res_upload = client.post(
        f"/api/disputes/{disp_id}/evidence",
        data={
            "title": "Tax Invoice Exhibit",
            "description": "Itemized invoice",
            "evidence_type": "order_invoice"
        },
        files=files
    )
    assert res_upload.status_code == 200
    evi_item = res_upload.json()["evidence_item"]
    assert evi_item["evidence_type"] == "order_invoice"
    assert evi_item["sha256_hash"] is not None
    import hashlib
    assert evi_item["sha256_hash"] == hashlib.sha256(sample_content).hexdigest()

    # 2. Reject prohibited extension
    bad_files = {"file": ("malicious.exe", b"binary", "application/octet-stream")}
    res_bad = client.post(
        f"/api/disputes/{disp_id}/evidence",
        data={"title": "Malicious file", "evidence_type": "other"},
        files=bad_files
    )
    assert res_bad.status_code == 400
    assert "not permitted" in res_bad.json()["detail"]


def test_contest_state_machine_guard():
    # Find a lost dispute in DB
    res_list = client.get("/api/disputes?status=lost&limit=1")
    lost_disputes = res_list.json()
    if lost_disputes:
        lost_id = lost_disputes[0]["id"]
        res_contest = client.post(f"/api/disputes/{lost_id}/contest")
        # Should be rejected with 409 Conflict
        assert res_contest.status_code == 409
        assert "cannot be contested" in res_contest.json()["detail"]


def test_dashboard_trend_chronological():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    trend = res.json()["recent_trend"]
    assert len(trend) > 0
    # Ensure all elements have date, opened, won, lost keys
    for item in trend:
        assert "date" in item
        assert "opened" in item
