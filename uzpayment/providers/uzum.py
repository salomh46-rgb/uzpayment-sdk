import urllib.parse
from typing import Dict, Any, Optional, Callable
from .base import BasePaymentProvider
from ..config import UzumConfig
from ..models import AccountVerificationResult, PaymentProviderType

class UzumProvider(BasePaymentProvider):
    def __init__(self, config: UzumConfig):
        self.config = config

    def generate_payment_link(
        self,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates Uzum Bank / Uzum Pay checkout link.
        """
        params = {
            "merchant_id": self.config.merchant_id,
            "order_id": str(order_id),
            "amount": str(amount),
        }
        if return_url:
            params["success_url"] = return_url
        if additional_params:
            params.update(additional_params)

        query = urllib.parse.urlencode(params)
        return f"https://pay.uzumbank.uz/checkout?{query}"

    def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        on_verify: Callable,
        on_create: Callable,
        on_success: Callable,
        on_cancel: Optional[Callable] = None,
        on_get_status: Optional[Callable] = None
    ) -> Dict[str, Any]:
        event = payload.get("event")
        order_id = payload.get("order_id")
        amount = int(payload.get("amount", 0))
        trans_id = payload.get("transaction_id", order_id)

        if event == "PAYMENT_SUCCESS":
            on_success(trans_id=trans_id)
            return {"status": "OK", "code": 0}
        elif event == "PAYMENT_FAILED":
            if on_cancel:
                on_cancel(trans_id=trans_id, reason=payload.get("error_code", 1))
            return {"status": "OK", "code": 0}
        
        return {"status": "UNKNOWN_EVENT", "code": -1}
