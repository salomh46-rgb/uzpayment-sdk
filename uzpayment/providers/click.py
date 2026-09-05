import urllib.parse
from typing import Dict, Any, Optional, Callable
from .base import BasePaymentProvider
from ..config import ClickConfig
from ..models import AccountVerificationResult, PaymentProviderType
from ..security.signature import SignatureValidator

class ClickProvider(BasePaymentProvider):
    def __init__(self, config: ClickConfig):
        self.config = config

    def generate_payment_link(
        self,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates Click Merchant Checkout URL.
        Amount is in Sums.
        """
        params = {
            "service_id": self.config.service_id,
            "merchant_id": self.config.merchant_id,
            "amount": f"{amount:.2f}" if isinstance(amount, float) else str(amount),
            "transaction_param": str(order_id),
        }
        if return_url:
            params["return_url"] = return_url
        if additional_params:
            params.update(additional_params)

        query = urllib.parse.urlencode(params)
        return f"https://my.click.uz/services/pay?{query}"

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
        """
        Handles Click Prepare (action=0) and Complete (action=1) requests.
        """
        # Verify Sign
        if not SignatureValidator.verify_click_sign(payload, self.config.secret_key):
            return {
                "click_trans_id": payload.get("click_trans_id"),
                "merchant_trans_id": payload.get("merchant_trans_id"),
                "error": -1,
                "error_note": "SIGN CHECK FAILED"
            }

        action = str(payload.get("action", "0"))
        click_trans_id = payload.get("click_trans_id")
        merchant_trans_id = payload.get("merchant_trans_id")
        amount = float(payload.get("amount", 0))

        # ACTION 0: PREPARE
        if action == "0":
            verify_res: AccountVerificationResult = on_verify(str(merchant_trans_id), int(amount), PaymentProviderType.CLICK)
            if not verify_res or not verify_res.is_valid:
                return {
                    "click_trans_id": click_trans_id,
                    "merchant_trans_id": merchant_trans_id,
                    "error": -5,
                    "error_note": "User/Order does not exist"
                }

            create_res = on_create(
                trans_id=str(click_trans_id),
                order_id=str(merchant_trans_id),
                amount=int(amount),
                trans_time=payload.get("sign_time")
            )
            merchant_prepare_id = create_res.get("merchant_prepare_id", click_trans_id)

            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": merchant_prepare_id,
                "error": 0,
                "error_note": "Success"
            }

        # ACTION 1: COMPLETE
        elif action == "1":
            merchant_prepare_id = payload.get("merchant_prepare_id")
            error_code = int(payload.get("error", 0))
            
            if error_code < 0:
                if on_cancel:
                    on_cancel(trans_id=str(click_trans_id), reason=error_code)
                return {
                    "click_trans_id": click_trans_id,
                    "merchant_trans_id": merchant_trans_id,
                    "error": -9,
                    "error_note": "Transaction cancelled by Click"
                }

            success_res = on_success(trans_id=str(click_trans_id))
            merchant_confirm_id = success_res.get("merchant_confirm_id", merchant_prepare_id or click_trans_id)

            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": merchant_confirm_id,
                "error": 0,
                "error_note": "Success"
            }

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "error": -3,
            "error_note": "Action not found"
        }
