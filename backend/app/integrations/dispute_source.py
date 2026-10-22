from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DisputeSource(ABC):
    """
    Abstract interface for dispute providers (Mock, Razorpay).
    """

    @abstractmethod
    def list_disputes(self, limit: int = 50, skip: int = 0, status: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_dispute(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def submit_contest(self, dispute_id: str, summary: str, document_ids: List[str]) -> Dict[str, Any]:
        """
        Submit dispute contest. Enforces provider character limits and evidence conditions.
        """
        pass
