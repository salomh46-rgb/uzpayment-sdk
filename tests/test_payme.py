import base64
from uzpayment import UzPayment, PaymeConfig, PaymentProviderType, AccountVerificationResult

def test_payme_payment_url_generation():
    config = PaymeConfig(merchant_id="TEST_MERCHANT", secret_key="TEST_SECRET", test_mode=True)
    gateway = UzPayment(payme=config)
    
    url = gateway.get_payment_url(PaymentProviderType.PAYME, amount=50000, order_id="ORD-101", return_url="https://mysite.uz/success")
    assert "https://test.paycom.uz/" in url
    
    # Decode base64 param
    token = url.split("https://test.paycom.uz/")[1]
    decoded = base64.b64decode(token).decode("utf-8")
    assert "m=TEST_MERCHANT" in decoded
    assert "ac.order_id=ORD-101" in decoded
    assert "a=5000000" in decoded # in tiyn
    assert "c=https://mysite.uz/success" in decoded

def test_payme_check_perform_transaction():
    config = PaymeConfig(merchant_id="TEST_M", secret_key="SECRET_123")
    gateway = UzPayment(payme=config)
    
    auth_header = "Basic " + base64.b64encode(b"Paycom:SECRET_123").decode("utf-8")
    
    payload = {
        "method": "CheckPerformTransaction",
        "params": {
            "amount": 5000000,
            "account": {"order_id": "ORD-1"}
        },
        "id": 100
    }
    
    def on_verify(order_id, amount, provider):
        return AccountVerificationResult(is_valid=True, order_id=order_id)

    res = gateway.payme.handle_webhook(
        payload=payload,
        headers={"authorization": auth_header},
        on_verify=on_verify,
        on_create=lambda **kw: {},
        on_success=lambda **kw: {},
        on_cancel=lambda **kw: {}
    )
    
    assert res["error"] is None if "error" in res else True
    assert res["result"]["allow"] is True
