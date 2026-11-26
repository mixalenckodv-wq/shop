from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services


def cart_detail(request):
    """Страница корзины с позициями и итогами."""
    context = services.cart_summary(request)
    return render(request, "cart/cart_detail.html", context)


@require_POST
def add_to_cart(request):
    """Добавляет товар в корзину."""
    product_id = request.POST.get("product_id")
    size_id = request.POST.get("size_id")
    quantity = request.POST.get("quantity", 1)
    try:
        services.add_to_cart(request, product_id, size_id, quantity)
        messages.success(request, "Товар добавлен в корзину.")
    except (ValueError, TypeError) as exc:
        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "catalog:product_list")


@require_POST
def update_cart_item(request, item_id):
    """Меняет количество позиции корзины."""
    quantity = request.POST.get("quantity", 1)
    try:
        services.update_item_quantity(request, item_id, quantity)
    except (ValueError, TypeError) as exc:
        messages.error(request, str(exc))
    return redirect("cart:cart_detail")


@require_POST
def remove_cart_item(request, item_id):
    """Удаляет позицию из корзины."""
    services.remove_item(request, item_id)
    messages.success(request, "Товар удалён из корзины.")
    return redirect("cart:cart_detail")


@require_POST
def clear_cart(request):
    """Очищает корзину целиком."""
    services.clear_cart(request)
    messages.success(request, "Корзина очищена.")
    return redirect("cart:cart_detail")
