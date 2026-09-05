from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models import AccountVerificationResult, PaymentStatus

class BasePaymentProvider(ABC):
    @abstractmethod
    def generate_payment_link(
        self,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generates a direct checkout URL for the client"""
        pass

    @abstractmethod
    def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        on_verify: Any,
        on_create: Any,
        on_success: Any,
        on_cancel: Any,
        on_get_status: Any
    ) -> Dict[str, Any]:
        """Processes incoming provider webhook and invokes application callbacks"""
        pass
