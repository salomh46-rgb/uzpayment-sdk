from typing import Callable, Optional
from ..models import AccountVerificationResult, PaymentProviderType
from .. import UzPayment

def create_payment_router(
    gateway: UzPayment,
    on_verify: Callable[[str, int, PaymentProviderType], AccountVerificationResult],
    on_create: Callable,
    on_success: Callable,
    on_cancel: Optional[Callable] = None,
    on_get_status: Optional[Callable] = None
):
    """
    Creates ready-to-mount FastAPI APIRouter with Payme and Click webhook endpoints.
    """
    try:
        from fastapi import APIRouter, Request, Response
        from fastapi.responses import JSONResponse
    except ImportError:
        raise ImportError("FastAPI is required for this integration: pip install fastapi")

    router = APIRouter(prefix="/payments", tags=["UzPayment Gateways"])

    if gateway.payme:
        @router.post("/payme")
        async def handle_payme_webhook(request: Request):
            payload = await request.json()
            headers = dict(request.headers)
            res = gateway.payme.handle_webhook(
                payload=payload,
                headers=headers,
                on_verify=on_verify,
                on_create=on_create,
                on_success=on_success,
                on_cancel=on_cancel or (lambda **kw: {}),
                on_get_status=on_get_status
            )
            return JSONResponse(content=res)

    if gateway.click:
        @router.post("/click/prepare")
        @router.post("/click/complete")
        @router.post("/click")
        async def handle_click_webhook(request: Request):
            # Click may send form data or JSON
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type:
                form = await request.form()
                payload = dict(form)
            else:
                try:
                    payload = await request.json()
                except Exception:
                    form = await request.form()
                    payload = dict(form)

            headers = dict(request.headers)
            res = gateway.click.handle_webhook(
                payload=payload,
                headers=headers,
                on_verify=on_verify,
                on_create=on_create,
                on_success=on_success,
                on_cancel=on_cancel or (lambda **kw: {}),
                on_get_status=on_get_status
            )
            return JSONResponse(content=res)

    return router
