from uzpayment.security.signature import SignatureValidator
import base64

def test_payme_auth_validation():
    secret = "my_secure_secret"
    valid_header = "Basic " + base64.b64encode(f"Paycom:{secret}".encode("utf-8")).decode("utf-8")
    invalid_header = "Basic " + base64.b64encode(b"Paycom:wrong_secret").decode("utf-8")
    
    assert SignatureValidator.verify_payme_auth(valid_header, secret) is True
    assert SignatureValidator.verify_payme_auth(invalid_header, secret) is False
    assert SignatureValidator.verify_payme_auth("Bearer 123", secret) is False

def test_click_sign_validation():
    secret = "test_key"
    sign = SignatureValidator.generate_click_sign(
        click_trans_id="999",
        service_id="10",
        secret_key=secret,
        merchant_trans_id="INV-001",
        amount="1000",
        action="0",
        sign_time="2026-09-05"
    )
    
    params = {
        "click_trans_id": "999",
        "service_id": "10",
        "merchant_trans_id": "INV-001",
        "amount": "1000",
        "action": "0",
        "sign_time": "2026-09-05",
        "sign_string": sign
    }
    
    assert SignatureValidator.verify_click_sign(params, secret) is True
