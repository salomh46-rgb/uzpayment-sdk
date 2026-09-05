import hashlib
import hmac
import base64
from typing import Dict, Any

class SignatureValidator:
    @staticmethod
    def verify_payme_auth(auth_header: str, secret_key: str, merchant_id: str = "") -> bool:
        """
        Payme sends Basic Auth: 'Basic base64(Paycom:secret_key)' or 'Basic base64(merchant_id:secret_key)'
        """
        if not auth_header or not auth_header.startswith("Basic "):
            return False
        
        try:
            encoded = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            parts = decoded.split(":")
            if len(parts) != 2:
                return False
            user, key = parts
            return key == secret_key
        except Exception:
            return False

    @staticmethod
    def generate_click_sign(
        click_trans_id: str,
        service_id: str,
        secret_key: str,
        merchant_trans_id: str,
        amount: str,
        action: str,
        sign_time: str,
        merchant_prepare_id: str = ""
    ) -> str:
        """
        Click MD5 sign calculation rule:
        Prepare: md5(click_trans_id + service_id + secret_key + merchant_trans_id + amount + action + sign_time)
        Complete: md5(click_trans_id + service_id + secret_key + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
        """
        if str(action) == "1" and merchant_prepare_id:
            raw = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{sign_time}"
        else:
            raw = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
        
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_click_sign(
        params: Dict[str, Any],
        secret_key: str
    ) -> bool:
        expected_sign = params.get("sign_string", "").lower()
        if not expected_sign:
            return False
        
        calculated = SignatureValidator.generate_click_sign(
            click_trans_id=str(params.get("click_trans_id", "")),
            service_id=str(params.get("service_id", "")),
            secret_key=secret_key,
            merchant_trans_id=str(params.get("merchant_trans_id", "")),
            amount=str(params.get("amount", "")),
            action=str(params.get("action", "")),
            sign_time=str(params.get("sign_time", "")),
            merchant_prepare_id=str(params.get("merchant_prepare_id", ""))
        ).lower()

        return hmac.compare_digest(expected_sign, calculated)
