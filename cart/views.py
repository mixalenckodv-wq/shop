from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from . import services


@require_POST
def add_to_cart(request):
    """Добавляет товар в корзину и возвращает пользователя в каталог."""
    product_id = request.POST.get("product_id")
    size_id = request.POST.get("size_id")
    quantity = request.POST.get("quantity", 1)
    try:
        services.add_to_cart(request, product_id, size_id, quantity)
    except (ValueError, TypeError) as exc:
        from django.contrib import messages

        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "catalog:product_list")
