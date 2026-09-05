from fastapi import FastAPI
from uzpayment import UzPayment, PaymeConfig, ClickConfig, AccountVerificationResult, PaymentProviderType
from uzpayment.integrations.fastapi import create_payment_router
import uvicorn

app = FastAPI(title="UzPayment FastAPI Integration Demo")

# 1. Initialize Gateway
gateway = UzPayment(
    payme=PaymeConfig(
        merchant_id="64821a8f9...",
        secret_key="your_payme_secret_key",
        test_mode=True
    ),
    click=ClickConfig(
        service_id="12345",
        merchant_id="67890",
        secret_key="your_click_secret_key"
    )
)

# In-memory orders for demo
ORDERS = {
    "ORD-1001": {"amount": 50000, "status": "pending"},
    "ORD-1002": {"amount": 120000, "status": "pending"}
}

# 2. Define Business Logic Callbacks
def verify_order(order_id: str, amount: int, provider: PaymentProviderType) -> AccountVerificationResult:
    order = ORDERS.get(order_id)
    if not order:
        return AccountVerificationResult(is_valid=False, order_id=order_id, detail="Order not found")
    
    # Check amount (Payme sends tiyns, Click sends sums)
    expected_sum = order["amount"]
    expected_tiyn = expected_sum * 100
    
    if provider == PaymentProviderType.PAYME and amount != expected_tiyn:
        return AccountVerificationResult(is_valid=False, order_id=order_id, expected_amount=expected_tiyn)
    elif provider == PaymentProviderType.CLICK and amount != expected_sum:
        return AccountVerificationResult(is_valid=False, order_id=order_id, expected_amount=expected_sum)

    return AccountVerificationResult(is_valid=True, order_id=order_id)

def create_transaction(trans_id: str, order_id: str, amount: int, trans_time: Any = None):
    print(f"Creating transaction: {trans_id} for order {order_id}")
    return {"transaction_id": trans_id, "state": 1}

def success_transaction(trans_id: str):
    print(f"Payment SUCCESS for transaction: {trans_id}")
    return {"transaction_id": trans_id, "state": 2}

# 3. Mount Payment Webhooks
app.include_router(create_payment_router(
    gateway=gateway,
    on_verify=verify_order,
    on_create=create_transaction,
    on_success=success_transaction
))

@app.get("/checkout/{order_id}")
def checkout(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        return {"error": "Order not found"}
    
    payme_url = gateway.get_payment_url(PaymentProviderType.PAYME, amount=order["amount"], order_id=order_id)
    click_url = gateway.get_payment_url(PaymentProviderType.CLICK, amount=order["amount"], order_id=order_id)
    
    return {
        "order_id": order_id,
        "amount": order["amount"],
        "payment_urls": {
            "payme": payme_url,
            "click": click_url
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
