import httpx
from typing import List, Dict, Any, Optional
from app.integrations.dispute_source import DisputeSource
from app.core.config import settings
from app.core.logging import logger


class RazorpayDisputeSource(DisputeSource):
    """
    Razorpay Dispute API client following official documentation:
    https://razorpay.com/docs/api/disputes/
    """

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        self.key_id = key_id or settings.RAZORPAY_KEY_ID
        self.key_secret = key_secret or settings.RAZORPAY_KEY_SECRET

    def _get_auth(self):
        if not self.key_id or not self.key_secret:
            raise ValueError("Razorpay test credentials (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET) not configured")
        return (self.key_id, self.key_secret)

    def list_disputes(self, limit: int = 50, skip: int = 0, status: Optional[str] = None) -> List[Dict[str, Any]]:
        auth = self._get_auth()
        params = {"count": limit, "skip": skip}
        if status:
            params["status"] = status

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self.BASE_URL}/disputes", auth=auth, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [])
                    return items
                else:
                    logger.error(f"Razorpay API error {resp.status_code}: {resp.text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay disputes: {e}")
            return []

    def get_dispute(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        # Hard Safety Guardrail: Never send synthetic dispute IDs to real Razorpay
        if dispute_id.startswith("disp_synth_"):
            raise ValueError(f"Safety constraint violation: Synthetic dispute {dispute_id} cannot be queried from live Razorpay API")

        auth = self._get_auth()
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self.BASE_URL}/disputes/{dispute_id}", auth=auth)
                if resp.status_code == 200:
                    return resp.json()
                return None
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay dispute {dispute_id}: {e}")
            return None

    def fetch_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        if payment_id.startswith("pay_synth_"):
            return None

        auth = self._get_auth()
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self.BASE_URL}/payments/{payment_id}", auth=auth)
                if resp.status_code == 200:
                    return resp.json()
                return None
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay payment {payment_id}: {e}")
            return None

    def submit_contest(self, dispute_id: str, summary: str, document_ids: List[str]) -> Dict[str, Any]:
        """
        Contest dispute on Razorpay (PATCH /v1/disputes/:id/contest).
        Official documentation constraint: summary <= 1,000 characters.
        """
        # Hard Safety Guardrail
        if dispute_id.startswith("disp_synth_"):
            raise ValueError(f"Safety constraint: Synthetic dispute ID '{dispute_id}' cannot be submitted to live Razorpay gateway")

        # Official limit verification
        if len(summary) > 1000:
            raise ValueError(f"Contest summary exceeds Razorpay official limit of 1000 characters (length: {len(summary)})")

        auth = self._get_auth()
        payload = {
            "summary": summary,
            "document_ids": document_ids,
            "action": "submit"
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.patch(f"{self.BASE_URL}/disputes/{dispute_id}/contest", auth=auth, json=payload)
                if resp.status_code in [200, 201]:
                    return resp.json()
                else:
                    return {
                        "success": False,
                        "error_code": resp.status_code,
                        "error_message": resp.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
