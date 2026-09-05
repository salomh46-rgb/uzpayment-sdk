from .config import PaymeConfig, ClickConfig, UzumConfig, PaynetConfig
from .models import PaymentProviderType, PaymentStatus, AccountVerificationResult, TransactionRecord
from .exceptions import (
    UzPaymentError, AuthenticationError, AccountNotFoundError,
    InvalidAmountError, TransactionNotFoundError, TransactionAlreadyCompletedError
)
from .providers.payme import PaymeProvider
from .providers.click import ClickProvider
from .providers.uzum import UzumProvider
from .providers.paynet import PaynetProvider
from typing import Optional, Dict, Any

__version__ = "1.0.0"
__author__ = "Jasper (salomh46-rgb)"

class UzPayment:
    """
    Universal Payment Gateway Manager for Uzbekistan
    """
    def __init__(
        self,
        payme: Optional[PaymeConfig] = None,
        click: Optional[ClickConfig] = None,
        uzum: Optional[UzumConfig] = None,
        paynet: Optional[PaynetConfig] = None
    ):
        self.payme = PaymeProvider(payme) if payme else None
        self.click = ClickProvider(click) if click else None
        self.uzum = UzumProvider(uzum) if uzum else None
        self.paynet = PaynetProvider(paynet) if paynet else None

    def get_payment_url(
        self,
        provider: PaymentProviderType,
        amount: int,
        order_id: str,
        return_url: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates direct client checkout URL for the specified provider.
        """
        if provider == PaymentProviderType.PAYME:
            if not self.payme:
                raise ValueError("Payme provider is not configured.")
            return self.payme.generate_payment_link(amount, order_id, return_url, additional_params)
        
        elif provider == PaymentProviderType.CLICK:
            if not self.click:
                raise ValueError("Click provider is not configured.")
            return self.click.generate_payment_link(amount, order_id, return_url, additional_params)

        elif provider == PaymentProviderType.UZUM:
            if not self.uzum:
                raise ValueError("Uzum provider is not configured.")
            return self.uzum.generate_payment_link(amount, order_id, return_url, additional_params)

        elif provider == PaymentProviderType.PAYNET:
            if not self.paynet:
                raise ValueError("Paynet provider is not configured.")
            return self.paynet.generate_payment_link(amount, order_id, return_url, additional_params)

        raise ValueError(f"Unsupported payment provider: {provider}")
