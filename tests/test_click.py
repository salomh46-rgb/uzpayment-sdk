from uzpayment import UzPayment, ClickConfig, PaymentProviderType, AccountVerificationResult
from uzpayment.security.signature import SignatureValidator

def test_click_payment_url_generation():
    config = ClickConfig(service_id="12345", merchant_id="67890", secret_key="SECRET_KEY")
    gateway = UzPayment(click=config)
    
    url = gateway.get_payment_url(PaymentProviderType.CLICK, amount=50000, order_id="ORD-55")
    assert "https://my.click.uz/services/pay" in url
    assert "service_id=12345" in url
    assert "merchant_id=67890" in url
    assert "amount=50000" in url
    assert "transaction_param=ORD-55" in url

def test_click_prepare_and_complete():
    secret = "CLICK_SECRET"
    config = ClickConfig(service_id="100", merchant_id="200", secret_key=secret)
    gateway = UzPayment(click=config)
    
    # 1. Prepare
    sign = SignatureValidator.generate_click_sign(
        click_trans_id="111",
        service_id="100",
        secret_key=secret,
        merchant_trans_id="ORD-1",
        amount="50000",
        action="0",
        sign_time="2026-09-05 12:00:00"
    )
    
    prepare_payload = {
        "click_trans_id": "111",
        "service_id": "100",
        "merchant_trans_id": "ORD-1",
        "amount": "50000",
        "action": "0",
        "sign_time": "2026-09-05 12:00:00",
        "sign_string": sign
    }
    
    def on_verify(order_id, amount, provider):
        return AccountVerificationResult(is_valid=True, order_id=order_id)
        
    def on_create(trans_id, order_id, amount, trans_time=None):
        return {"merchant_prepare_id": "PREP-1"}

    def on_success(trans_id):
        return {"merchant_confirm_id": "CONF-1"}

    res = gateway.click.handle_webhook(
        payload=prepare_payload,
        headers={},
        on_verify=on_verify,
        on_create=on_create,
        on_success=on_success
    )
    
    assert res["error"] == 0
    assert res["merchant_prepare_id"] == "PREP-1"
