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

## 🌟 Nega aynan UzPayment SDK? (Why UzPayment?)

O'zbekistonda Click, Payme yoki Uzum Bank to'lov tizimlarini alohida ulash va har birining imzolarini (MD5, Basic Auth, JSON-RPC) tekshirish juda ko'p vaqt va kod talab qiladi.

**UzPayment SDK** barcha to'lov tizimlarini yagona, toza va professional interfeysga birlashtiradi:
- ⚡️ **3 qatorda to'lovlarni ulash** (FastAPI, Django, Flask uchun tayyor adapterlar).
- 🔒 **100% Xavfsizlik:** MD5, HMAC va Basic Auth imzo tekshiruvlari avtomatik ishlaydi.
- 🔗 **Tezkor Checkout Link & QR:** Click, Payme va Uzum uchun to'lov havolalarini 1 ta funksiya bilan yaratish.
- 📦 **PyPI standarti:** `pip install uzpayment` orqali to'g'ridan-to'g'ri o'rnatish.
- 🧪 **Lokal Test Server:** Real hisob raqamsiz ham webhooks va to'lovlarni kompyuteringizda testlash.

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

## 🚀 Tezkor Qo'llanma (Quickstart)

### 1. To'lov Havolalarini Yaratish (Checkout URL Generator)

```python
from uzpayment import UzPayment, PaymeConfig, ClickConfig, PaymentProviderType

# Initsializatsiya
gateway = UzPayment(
    payme=PaymeConfig(merchant_id="YOUR_PAYME_ID", secret_key="YOUR_PAYME_SECRET"),
    click=ClickConfig(service_id="YOUR_SERVICE_ID", merchant_id="YOUR_MERCHANT_ID", secret_key="YOUR_CLICK_SECRET")
)

# 1. Payme to'lov havolasi
payme_url = gateway.get_payment_url(
    provider=PaymentProviderType.PAYME,
    amount=50000, # 50 000 so'm
    order_id="INV-1001",
    return_url="https://myshop.uz/order/1001/success"
)
print("Payme URL:", payme_url)

# 2. Click to'lov havolasi
click_url = gateway.get_payment_url(
    provider=PaymentProviderType.CLICK,
    amount=50000,
    order_id="INV-1001",
    return_url="https://myshop.uz/order/1001/success"
)
print("Click URL:", click_url)
```

---

### 2. FastAPI ga Webhook ulash (3 Qatorda!)

```python
from fastapi import FastAPI
from uzpayment import UzPayment, PaymeConfig, ClickConfig, AccountVerificationResult, PaymentProviderType
from uzpayment.integrations.fastapi import create_payment_router

app = FastAPI()

gateway = UzPayment(
    payme=PaymeConfig(merchant_id="...", secret_key="..."),
    click=ClickConfig(service_id="...", merchant_id="...", secret_key="...")
)

# Biznes mantiq: Buyurtmani tekshirish
def verify_order(order_id: str, amount: int, provider: PaymentProviderType) -> AccountVerificationResult:
    # Bazadan orderni topib summasini tekshiring
    return AccountVerificationResult(is_valid=True, order_id=order_id)

# Biznes mantiq: To'lov muvaffaqiyatli o'tganda (Kassa/Status yangilash)
def on_payment_success(trans_id: str):
    print(f"✅ To'lov muvaffaqiyatli qabul qilindi: {trans_id}")
    return {"status": "SUCCESS"}

# Tayyor webhook routelarni ulang: /payments/payme va /payments/click
app.include_router(create_payment_router(
    gateway=gateway,
    on_verify=verify_order,
    on_create=lambda **kw: {"transaction_id": kw.get("trans_id"), "state": 1},
    on_success=on_payment_success
))
```

---

### 3. Django ga Webhook ulash

```python
# urls.py
from django.urls import path
from uzpayment import UzPayment, PaymeConfig, ClickConfig
from uzpayment.integrations.django_views import create_django_views

gateway = UzPayment(
    payme=PaymeConfig(merchant_id="...", secret_key="..."),
    click=ClickConfig(service_id="...", merchant_id="...", secret_key="...")
)

PaymeView, ClickView = create_django_views(
    gateway=gateway,
    on_verify=my_verify_func,
    on_create=my_create_func,
    on_success=my_success_func
)

urlpatterns = [
    path("api/payments/payme/", PaymeView.as_view()),
    path("api/payments/click/", ClickView.as_view()),
]
```

---

## 🧪 Testlarni Ishga Tushirish (Running Unit Tests)

```bash
pytest tests/ -v
```

---

## 👨‍💻 Muallif & Dasturchi
- **Muallif:** [Jasper](https://github.com/salomh46-rgb)
- **Portfolio:** [bestportfoliyo-o4z2.vercel.app](https://bestportfoliyo-o4z2.vercel.app/)
- **Loyiha Repozitoriyasi:** [https://github.com/salomh46-rgb/uzpayment-sdk](https://github.com/salomh46-rgb/uzpayment-sdk)
- **Litsenziya:** MIT License

---

<div align="center">
  <b>⭐️ Agar loyiha sizga ma'qul kelgan bo'lsa, GitHub-da Star (⭐️) bosishni unutmang!</b>
</div>
