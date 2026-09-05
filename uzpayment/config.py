from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymeConfig:
    merchant_id: str
    secret_key: str
    test_mode: bool = False
    endpoint: str = "/api/v1/payments/payme"

@dataclass
class ClickConfig:
    service_id: str
    merchant_id: str
    secret_key: str
    merchant_user_id: Optional[str] = None
    endpoint: str = "/api/v1/payments/click"

@dataclass
class UzumConfig:
    merchant_id: str
    secret_key: str
    endpoint: str = "/api/v1/payments/uzum"

@dataclass
class PaynetConfig:
    service_id: str
    username: str
    password: str
    endpoint: str = "/api/v1/payments/paynet"
