import base64
import time
from typing import Dict, Any, Optional, Callable
from .base import BasePaymentProvider
from ..config import PaymeConfig
from ..models import AccountVerificationResult, PaymentStatus, PaymentProviderType
from ..security.signature import SignatureValidator

class PaymeProvider(BasePaymentProvider):
    def __init__(self, config: PaymeConfig):
        self.config = config

    def generate_payment_link(
        self,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates Payme Checkout URL.
        Amount is in Tiyn (1 sum = 100 tiyn). If sum provided, it is multiplied by 100.
        """
        # Ensure tiyn
        amount_tiyn = amount if amount >= 100000 else amount * 100
        
        # Payme payload format: m={merchant_id};ac.order_id={order_id};a={amount_tiyn};c={return_url}
        raw_params = f"m={self.config.merchant_id};ac.order_id={order_id};a={amount_tiyn}"
        if return_url:
            raw_params += f";c={return_url}"
        
        if additional_params:
            for k, v in additional_params.items():
                raw_params += f";{k}={v}"

        encoded = base64.b64encode(raw_params.encode("utf-8")).decode("utf-8")
        base_url = "https://test.paycom.uz" if self.config.test_mode else "https://checkout.paycom.uz"
        return f"{base_url}/{encoded}"

    def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        on_verify: Callable,
        on_create: Callable,
        on_success: Callable,
        on_cancel: Callable,
        on_get_status: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        JSON-RPC 2.0 Payme Webhook Handler.
        """
        auth_header = headers.get("authorization") or headers.get("Authorization", "")
        if not SignatureValidator.verify_payme_auth(auth_header, self.config.secret_key, self.config.merchant_id):
            return {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {"code": -32504, "message": {"uz": "Avtorizatsiyadan o'tilmadi", "ru": "Недостаточно привилегий", "en": "Unauthorized"}}
            }

        method = payload.get("method")
        params = payload.get("params", {})
        req_id = payload.get("id")

        try:
            if method == "CheckPerformTransaction":
                return self._handle_check_perform(req_id, params, on_verify)
            elif method == "CreateTransaction":
                return self._handle_create_transaction(req_id, params, on_verify, on_create)
            elif method == "PerformTransaction":
                return self._handle_perform_transaction(req_id, params, on_success)
            elif method == "CancelTransaction":
                return self._handle_cancel_transaction(req_id, params, on_cancel)
            elif method == "CheckTransaction":
                return self._handle_check_transaction(req_id, params, on_get_status)
            elif method == "GetStatement":
                return {"jsonrpc": "2.0", "id": req_id, "result": {"transactions": []}}
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": {"uz": "Metod topilmadi", "ru": "Метод не найден", "en": "Method not found"}}
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -31008, "message": {"uz": str(e), "ru": str(e), "en": str(e)}}
            }

    def _handle_check_perform(self, req_id: Any, params: Dict[str, Any], on_verify: Callable) -> Dict[str, Any]:
        account = params.get("account", {})
        order_id = str(account.get("order_id") or account.get("id") or "")
        amount = int(params.get("amount", 0))

        verify_res: AccountVerificationResult = on_verify(order_id, amount, PaymentProviderType.PAYME)
        if not verify_res or not verify_res.is_valid:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -31050,
                    "message": {"uz": "Buyurtma topilmadi", "ru": "Заказ не найден", "en": "Order not found"},
                    "data": "order_id"
                }
            }

        if verify_res.expected_amount and verify_res.expected_amount != amount:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -31001,
                    "message": {"uz": "Noto'g'ri summa", "ru": "Неверная сумма", "en": "Invalid amount"}
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "allow": True,
                "detail": verify_res.additional_data or {}
            }
        }

    def _handle_create_transaction(self, req_id: Any, params: Dict[str, Any], on_verify: Callable, on_create: Callable) -> Dict[str, Any]:
        trans_id = params.get("id")
        trans_time = params.get("time")
        amount = int(params.get("amount", 0))
        account = params.get("account", {})
        order_id = str(account.get("order_id") or account.get("id") or "")

        # Verify account first
        verify_res: AccountVerificationResult = on_verify(order_id, amount, PaymentProviderType.PAYME)
        if not verify_res or not verify_res.is_valid:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -31050, "message": {"uz": "Buyurtma topilmadi", "ru": "Заказ не найден", "en": "Order not found"}}
            }

        # Create or fetch existing transaction in merchant storage
        res = on_create(trans_id=trans_id, order_id=order_id, amount=amount, trans_time=trans_time)
        create_time = res.get("create_time", int(time.time() * 1000))
        state = res.get("state", 1)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "create_time": create_time,
                "transaction": str(res.get("transaction_id", trans_id)),
                "state": state
            }
        }

    def _handle_perform_transaction(self, req_id: Any, params: Dict[str, Any], on_success: Callable) -> Dict[str, Any]:
        trans_id = params.get("id")
        res = on_success(trans_id=trans_id)
        perform_time = res.get("perform_time", int(time.time() * 1000))

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "transaction": str(res.get("transaction_id", trans_id)),
                "perform_time": perform_time,
                "state": 2
            }
        }

    def _handle_cancel_transaction(self, req_id: Any, params: Dict[str, Any], on_cancel: Callable) -> Dict[str, Any]:
        trans_id = params.get("id")
        reason = params.get("reason", 1)
        res = on_cancel(trans_id=trans_id, reason=reason)
        cancel_time = res.get("cancel_time", int(time.time() * 1000))
        state = res.get("state", -1)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "transaction": str(res.get("transaction_id", trans_id)),
                "cancel_time": cancel_time,
                "state": state
            }
        }

    def _handle_check_transaction(self, req_id: Any, params: Dict[str, Any], on_get_status: Optional[Callable]) -> Dict[str, Any]:
        trans_id = params.get("id")
        if on_get_status:
            res = on_get_status(trans_id=trans_id)
        else:
            res = {"create_time": int(time.time()*1000), "perform_time": 0, "cancel_time": 0, "state": 1, "reason": None}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "create_time": res.get("create_time", 0),
                "perform_time": res.get("perform_time", 0),
                "cancel_time": res.get("cancel_time", 0),
                "transaction": str(res.get("transaction_id", trans_id)),
                "state": res.get("state", 1),
                "reason": res.get("reason")
            }
        }
