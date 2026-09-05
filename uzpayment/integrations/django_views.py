import json
from typing import Callable, Optional
from ..models import AccountVerificationResult, PaymentProviderType
from .. import UzPayment

def create_django_views(
    gateway: UzPayment,
    on_verify: Callable,
    on_create: Callable,
    on_success: Callable,
    on_cancel: Optional[Callable] = None,
    on_get_status: Optional[Callable] = None
):
    try:
        from django.http import JsonResponse, HttpResponse
        from django.views import View
        from django.views.decorators.csrf import csrf_exempt
        from django.utils.decorators import method_decorator
    except ImportError:
        raise ImportError("Django is required: pip install django")

    class PaymeWebhookView(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super().dispatch(*args, **kwargs)

        def post(self, request, *args, **kwargs):
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except Exception:
                payload = {}
            headers = {k.lower(): v for k, v in request.headers.items()}
            res = gateway.payme.handle_webhook(
                payload=payload,
                headers=headers,
                on_verify=on_verify,
                on_create=on_create,
                on_success=on_success,
                on_cancel=on_cancel or (lambda **kw: {}),
                on_get_status=on_get_status
            )
            return JsonResponse(res)

    class ClickWebhookView(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super().dispatch(*args, **kwargs)

        def post(self, request, *args, **kwargs):
            payload = dict(request.POST) if request.POST else {}
            if not payload:
                try:
                    payload = json.loads(request.body.decode("utf-8"))
                except Exception:
                    pass
            headers = {k.lower(): v for k, v in request.headers.items()}
            res = gateway.click.handle_webhook(
                payload=payload,
                headers=headers,
                on_verify=on_verify,
                on_create=on_create,
                on_success=on_success,
                on_cancel=on_cancel or (lambda **kw: {}),
                on_get_status=on_get_status
            )
            return JsonResponse(res)

    return PaymeWebhookView, ClickWebhookView
