from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
import time

class PaymentProviderType(str, Enum):
    PAYME = "payme"
    CLICK = "click"
    UZUM = "uzum"
    PAYNET = "paynet"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AccountVerificationResult:
    is_valid: bool
    order_id: str
    expected_amount: Optional[int] = None # in Tiyns (1 sum = 100 tiyn) or Sums
    detail: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransactionRecord:
    id: str
    provider: PaymentProviderType
    provider_trans_id: str
    order_id: str
    amount: int
    status: PaymentStatus
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))
    perform_time: int = 0
    cancel_time: int = 0
    reason: Optional[int] = None
