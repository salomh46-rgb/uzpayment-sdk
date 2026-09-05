import base64
from typing import Dict, Any, Optional, Callable
from .base import BasePaymentProvider
from ..config import PaynetConfig
from ..models import AccountVerificationResult, PaymentProviderType

class PaynetProvider(BasePaymentProvider):
    def __init__(self, config: PaynetConfig):
        self.config = config

    def generate_payment_link(
        self,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        return f"https://paynet.uz/pay?service_id={self.config.service_id}&order_id={order_id}&amount={amount}"

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
        # Authenticate Basic Auth
        auth = headers.get("authorization", "")
        if auth.startswith("Basic "):
            decoded = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
            u, p = decoded.split(":")
            if u != self.config.username or p != self.config.password:
                return {"status": "UNAUTHORIZED", "code": 401}

        method = payload.get("method")
        params = payload.get("params", {})
        
        if method == "CheckTransaction":
            res = on_verify(str(params.get("order_id")), int(params.get("amount", 0)), PaymentProviderType.PAYNET)
            return {"status": "OK" if res.is_valid else "ERROR", "code": 0 if res.is_valid else 100}
        elif method == "PerformTransaction":
            on_success(trans_id=str(params.get("transaction_id")))
            return {"status": "OK", "code": 0}

        return {"status": "NOT_FOUND", "code": 404}
