import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.integrations.razorpay.client import RazorpayDisputeSource


def run_e2e_verification():
    print("=" * 70)
    print("RUNNING END-TO-END WORKFLOW VERIFICATION: CHARGEBACK & DISPUTE COPILOT")
    print("=" * 70)

    client = TestClient(app)

    # Step 1: Health & Demo Mode
    print("\n[Step 1] Verifying System Health & Active Mode...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert health_data["status"] == "healthy"
    assert health_data["dispute_source"] == "mock"
    print(f"  ✓ System healthy: {health_data['service']} (Mode: {health_data['dispute_source']})")

    # Step 2: Seeded Dashboard
    print("\n[Step 2] Validating Executive Dashboard Seeded Metrics...")
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    dash = res.json()
    assert dash["total_disputes"] == 50
    assert dash["open_disputes"] > 0
    assert dash["total_amount_at_risk"] > 0
    print(f"  ✓ Caseload: {dash['total_disputes']} disputes | At Risk: INR {dash['total_amount_at_risk']/100:.2f} | Win Rate: {dash['win_rate_percentage']:.1f}%")

    # Step 3: Filter Dispute Queue
    print("\n[Step 3] Filtering Dispute Queue by Reason & Status...")
    res = client.get("/api/disputes?reason=product_not_received&limit=10")
    assert res.status_code == 200
    pnr_list = res.json()
    assert len(pnr_list) > 0
    for d in pnr_list:
        assert d["reason_code"] == "product_not_received"
    test_disp_id = pnr_list[0]["id"]
    print(f"  ✓ Filtered {len(pnr_list)} 'product_not_received' cases. Selected for deep inspection: {test_disp_id}")

    # Step 4: Open Dispute Detail Workspace
    print(f"\n[Step 4] Opening Detailed Workspace for {test_disp_id}...")
    res = client.get(f"/api/disputes/{test_disp_id}")
    assert res.status_code == 200
    detail = res.json()
    assert "order" in detail
    assert "payment" in detail
    assert "customer" in detail
    print(f"  ✓ Order #{detail['order']['order_number']} | Customer: {detail['customer']['name']} | Amount: INR {detail['amount']/100:.2f}")

    # Step 5: Review Evidence Checklist
    print(f"\n[Step 5] Inspecting Evidence Vault & Checklist...")
    res = client.get(f"/api/disputes/{test_disp_id}/evidence")
    assert res.status_code == 200
    evidence_links = res.json()
    print(f"  ✓ Attached exhibits count: {len(evidence_links)}")

    # Step 6: Trigger 10-Step AI Investigation
    print(f"\n[Step 6] Running 10-Step AI Investigation Agent...")
    res = client.post(f"/api/disputes/{test_disp_id}/investigate")
    assert res.status_code == 200
    inv = res.json()
    assert inv["investigation_status"] == "completed"
    print(f"  ✓ Investigation completed in {inv['execution_duration_ms']}ms using {inv['model_provider']}")
    print(f"  ✓ Findings: {inv['findings_summary'][:100]}...")
    if inv["contradictions"]:
        print(f"  ✓ Inconsistency Detected: {inv['contradictions'][0]['title']}")

    # Step 7: Generate & Edit Draft in Response Studio
    print(f"\n[Step 7] Inspecting & Editing Response Draft...")
    res = client.get(f"/api/disputes/{test_disp_id}/draft")
    assert res.status_code == 200
    draft = res.json()
    orig_len = len(draft["contest_summary"])
    assert orig_len <= 1000, f"Contest summary exceeds 1000 chars ({orig_len})"
    print(f"  ✓ Active contest summary length: {orig_len} / 1000 chars")

    # Step 8: Calculate & Inspect Explainable Win-Score
    print(f"\n[Step 8] Executing Explainable Win-Score ML Pipeline...")
    res = client.post(f"/api/disputes/{test_disp_id}/score")
    assert res.status_code == 200
    score_res = res.json()
    assert 0.0 <= score_res["score"] <= 100.0
    print(f"  ✓ Calibrated Win-Score: {score_res['score']:.1f}% (Tier: {score_res['tier'].upper()})")
    if score_res["top_positive_factors"]:
        top_pos = score_res["top_positive_factors"][0]
        print(f"    + Driver: {top_pos['description']} (+{top_pos['impact_points']:.1f} pts)")
    if score_res["top_negative_factors"]:
        top_neg = score_res["top_negative_factors"][0]
        print(f"    - Driver: {top_neg['description']} ({top_neg['impact_points']:.1f} pts)")

    # Step 9: Export PDF Report
    print(f"\n[Step 9] Streaming Full PDF Representation Report...")
    res = client.get(f"/api/disputes/{test_disp_id}/report")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000
    print(f"  ✓ Generated executive PDF ({len(res.content)} bytes) with complete evidence provenance")

    # Step 10: Save Edited Draft & Approve
    print(f"\n[Step 10] Saving & Formally Approving Response Draft...")
    updated_summary = (
        f"Formal contest for dispute {test_disp_id}. Goods were fulfilled and delivered to customer "
        f"per verified carrier telematics. All mandatory merchant scheme conditions met."
    )
    res = client.patch(f"/api/disputes/{test_disp_id}/draft", json={
        "contest_summary": updated_summary,
        "representation_letter": draft["representation_letter"]
    })
    assert res.status_code == 200

    res_app = client.post(f"/api/disputes/{test_disp_id}/draft/approve")
    assert res_app.status_code == 200
    assert res_app.json()["is_approved"] is True
    print(f"  ✓ Response draft approved by Risk Lead")

    # Step 11: Safety Guardrails Verification
    print(f"\n[Step 11] Verifying Gateway Safety Guardrails...")
    rzp_client = RazorpayDisputeSource(key_id="rzp_test_dummy", key_secret="dummy_secret")
    try:
        rzp_client.submit_contest(test_disp_id, "Attempted submission", [])
        raise AssertionError("Safety constraint failed: Synthetic dispute was submitted to live client!")
    except ValueError as e:
        print(f"  ✓ Guardrail Confirmed: Blocked live submission of synthetic ID ({e})")

    try:
        rzp_client.submit_contest("disp_real_1234", "A" * 1005, [])
        raise AssertionError("Safety constraint failed: Length > 1000 was accepted!")
    except ValueError as e:
        print(f"  ✓ Guardrail Confirmed: Blocked contest summary exceeding 1000 chars ({e})")

    # Step 12: Audit Log Validation
    print(f"\n[Step 12] Inspecting Consequential Audit Log Trail...")
    res = client.get("/api/settings/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    print(f"  ✓ Verified {len(logs)} audit entries in database")

    print("\n" + "=" * 70)
    print("ALL 12 END-TO-END WORKFLOW MILESTONES VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_e2e_verification()
