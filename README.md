# 💳 UzPayment SDK — Universal Payment Gateway for Uzbekistan

<div align="center">

[![NPM Version](https://img.shields.io/npm/v/@javohirbek3302/uzpayment-sdk.svg?style=for-the-badge&logo=npm&color=CB3837)](https://www.npmjs.com/package/@javohirbek3302/uzpayment-sdk)
[![PyPI Version](https://img.shields.io/badge/PyPI-v1.0.0-blue.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/uzpayment/)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-100%25_Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![FastAPI & Django](https://img.shields.io/badge/Frameworks-FastAPI%20%7C%20Django%20%7C%20Flask-009688?style=for-the-badge&logo=fastapi&logoColor=white)](examples/)

<p align="center">
  <b>Production-ready, type-safe, and asynchronous Multi-Provider Payment Gateway SDK for Uzbekistan (Click, Payme, Uzum Bank, Paynet).</b>
</p>

</div>

---

## 🏛️ Architecture Overview

```mermaid
graph LR
    Client([🛒 User / Frontend App]) -->|Initiate Checkout| Gateway[💳 UzPayment SDK Core]
    
    subgraph Multi-Provider Adapters
        Gateway --> Payme[💳 Payme API v2]
        Gateway --> Click[💳 Click Merchant API]
        Gateway --> Uzum[💳 Uzum Bank Gateway]
        Gateway --> Paynet[💳 Paynet Direct]
    end
    
    Payme --> Verifier{MD5 / Basic Auth Verifier}
    Click --> Signer{HMAC-SHA256 Signer}
    
    Verifier --> Webhook[⚡ FastAPI / Django Webhook Router]
    Signer --> Webhook
    Webhook --> DB[(📦 Orders Database)]
```

---

## 🌟 Nega aynan UzPayment SDK? (Key Highlights)

- ⚡ **3 qatorda to'lovlarni ulash** (FastAPI, Django, Flask uchun plug-and-play adapterlar).
- 🔒 **100% Xavfsizlik:** MD5, HMAC-SHA256 va Basic Auth imzo tekshiruvlari avtomatik ishlaydi.
- 🔗 **Tezkor Checkout Link & QR:** Click, Payme va Uzum uchun to'lov havolalarini 1 ta funksiya bilan yaratish.
- 📦 **PyPI & NPM Standarti:** `pip install uzpayment` orqali to'g'ridan-to'g'ri o'rnatish.
- 🧪 **Lokal Mock Server:** Real hisob raqamsiz ham webhooks va to'lovlarni lokal mashinangizda testlash.

---

## 📦 O'rnatish (Installation)

```bash
pip install uzpayment
```

Yoki framework adapterlari bilan:
```bash
pip install "uzpayment[fastapi]" # FastAPI uchun
pip install "uzpayment[django]"  # Django uchun
```

---

## 🚀 Quickstart: FastAPI ga 3 Qatorda Ulash!

```python
from fastapi import FastAPI
from uzpayment import UzPayment, PaymeConfig, ClickConfig, AccountVerificationResult, PaymentProviderType
from uzpayment.integrations.fastapi import create_payment_router

app = FastAPI()

gateway = UzPayment(
    payme=PaymeConfig(merchant_id="YOUR_PAYME_ID", secret_key="YOUR_PAYME_SECRET"),
    click=ClickConfig(service_id="YOUR_SERVICE_ID", merchant_id="YOUR_MERCHANT_ID", secret_key="YOUR_CLICK_SECRET")
)

def verify_order(order_id: str, amount: int, provider: PaymentProviderType) -> AccountVerificationResult:
    return AccountVerificationResult(is_valid=True, order_id=order_id)

def on_payment_success(trans_id: str):
    print(f"✅ To'lov muvaffaqiyatli qabul qilindi: {trans_id}")
    return {"status": "SUCCESS"}

app.include_router(create_payment_router(
    gateway=gateway,
    on_verify=verify_order,
    on_create=lambda **kw: {"transaction_id": kw.get("trans_id"), "state": 1},
    on_success=on_payment_success
))
```

---

## 🧪 Run Automated Tests

```bash
pytest -v tests/
```

---

## 👨‍💻 Muallif & Dasturchi
- **Muallif:** [Javohirbek Asqarov (Jasper)](https://github.com/salomh46-rgb)
- **Portfolio:** [bestportfoliyo-o4z2.vercel.app](https://bestportfoliyo-o4z2.vercel.app/)
- **Litsenziya:** MIT License
