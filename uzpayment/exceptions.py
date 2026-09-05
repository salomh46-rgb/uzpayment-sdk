from typing import Optional, Any

class UzPaymentError(Exception):
    """Base exception for all UzPayment errors"""
    def __init__(self, message: str, code: int = -1, data: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

class AuthenticationError(UzPaymentError):
    """Raised when authentication / signature verification fails"""
    def __init__(self, message: str = "Invalid credentials or signature"):
        super().__init__(message, code=-32504)

class AccountNotFoundError(UzPaymentError):
    """Raised when the specified order / user account does not exist"""
    def __init__(self, message: str = "Account not found", field: str = "order_id"):
        super().__init__(message, code=-31050, data={"field": field})

class InvalidAmountError(UzPaymentError):
    """Raised when payment amount does not match invoice or is invalid"""
    def __init__(self, message: str = "Incorrect amount"):
        super().__init__(message, code=-31001)

class TransactionNotFoundError(UzPaymentError):
    """Raised when transaction is not found"""
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(message, code=-31003)

class TransactionAlreadyCompletedError(UzPaymentError):
    """Raised when attempting to modify already completed transaction"""
    def __init__(self, message: str = "Transaction already completed"):
        super().__init__(message, code=-31007)

class TransactionCancelledError(UzPaymentError):
    """Raised when transaction has already been cancelled"""
    def __init__(self, message: str = "Transaction is cancelled"):
        super().__init__(message, code=-31008)
