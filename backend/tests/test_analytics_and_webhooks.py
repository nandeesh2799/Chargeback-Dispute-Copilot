import io
import json
import pytest
from fastapi.testclient import TestClient


def test_analytics_overview(client: TestClient):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "outcomes_by_reason" in data
    assert "completeness_buckets" in data
    assert "response_turnaround" in data
    assert data["sample_size"] == 50
    assert len(data["outcomes_by_reason"]) > 0


def test_analytics_model_evaluation(client: TestClient):
    res = client.get("/api/analytics/model-evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "accuracy" in data
    assert "roc_auc" in data
    assert "f1_score" in data
    assert data["accuracy"] > 0.80
    assert "confusion_matrix" in data
    assert "feature_importances" in data


def test_disputes_csv_export(client: TestClient):
    res = client.get("/api/disputes/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    lines = res.text.strip().split("\n")
    assert len(lines) > 1
    assert "Dispute ID" in lines[0]
    assert "Order Ref" in lines[0]


def test_dispute_evidence_retrieval(client: TestClient):
    # Retrieve first dispute
    res_list = client.get("/api/disputes?limit=1")
    assert res_list.status_code == 200
    disp_id = res_list.json()[0]["id"]

    res_ev = client.get(f"/api/disputes/{disp_id}/evidence")
    assert res_ev.status_code == 200
    evidence_items = res_ev.json()
    assert isinstance(evidence_items, list)


def test_evidence_upload_validation(client: TestClient):
    res_list = client.get("/api/disputes?limit=1")
    disp_id = res_list.json()[0]["id"]

    # Valid upload: mock text file
    file_content = b"Proof of delivery signed by recipient at 10:30 AM."
    files = {"file": ("proof_delivery.txt", io.BytesIO(file_content), "text/plain")}
    data = {
        "evidence_type": "delivery_proof",
        "title": "Automated Carrier Log",
        "relevance_note": "Confirms signed delivery"
    }

    res_upload = client.post(f"/api/disputes/{disp_id}/evidence", files=files, data=data)
    assert res_upload.status_code == 200
    resp_json = res_upload.json()
    assert resp_json["evidence_item"]["title"] == "Automated Carrier Log"
    assert resp_json["evidence_item"]["sha256_hash"] is not None

    # Invalid upload: disallowed extension
    files_invalid = {"file": ("malicious.exe", io.BytesIO(b"executable content"), "application/x-msdownload")}
    res_invalid = client.post(f"/api/disputes/{disp_id}/evidence", files=files_invalid, data=data)
    assert res_invalid.status_code == 400


def test_webhook_idempotency(client: TestClient):
    import uuid
    # Unique event id per test run
    event_id = f"test_evt_{uuid.uuid4().hex[:10]}"
    payload = {
        "event_id": event_id,
        "event": "dispute.created",
        "payload": {
            "dispute": {
                "entity": {
                    "id": "disp_sample_wh_01",
                    "amount": 250000,
                    "currency": "INR",
                    "reason_code": "product_not_received"
                }
            }
        }
    }

    # First delivery
    res1 = client.post("/api/webhooks/razorpay", json=payload)
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"

    # Duplicate delivery
    res2 = client.post("/api/webhooks/razorpay", json=payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "ignored"
    assert res2.json()["reason"] == "duplicate_event_id"


def test_draft_approval_workflow(client: TestClient):
    res_list = client.get("/api/disputes?limit=1")
    disp_id = res_list.json()[0]["id"]

    # Run investigation and score first
    client.post(f"/api/disputes/{disp_id}/investigate")
    client.post(f"/api/disputes/{disp_id}/score")

    # Approve draft
    res_approve = client.post(f"/api/disputes/{disp_id}/draft/approve")
    assert res_approve.status_code == 200
    data = res_approve.json()
    assert data["is_approved"] is True
