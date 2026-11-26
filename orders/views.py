from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from cart import services as cart_services
from .forms import OrderCreateForm
from .models import Order, OrderItem


@transaction.atomic
def _create_order_from_cart(request, cart, form):
    """Создаёт заказ и позиции из корзины, списывает остатки, чистит корзину."""
    order = form.save(commit=False)
    if request.user.is_authenticated:
        order.user = request.user
    order.save()

    for item in cart.items.select_related("product", "product_size").all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=str(item.product),
            size=item.product_size.size if item.product_size else None,
            price=item.product.price,
            quantity=item.quantity,
        )
        size = item.product_size
        if size is not None and size.stock >= item.quantity:
            size.stock -= item.quantity
            size.save(update_fields=["stock"])

    cart.items.all().delete()
    return order


def checkout(request):
    """Оформление заказа: показывает форму и создаёт заказ из корзины."""
    cart = cart_services.get_or_create_cart(request)
    if not cart.items.exists():
        messages.info(request, "Корзина пуста — добавьте товары перед оформлением.")
        return redirect("catalog:product_list")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = _create_order_from_cart(request, cart, form)
            return redirect("orders:order_success", pk=order.pk)
    else:
        form = OrderCreateForm()

    context = {
        "form": form,
        **cart_services.cart_summary(request),
    }
    return render(request, "orders/checkout.html", context)


def order_success(request, pk):
    """Страница успешного оформления заказа."""
    order = Order.objects.filter(pk=pk).prefetch_related("items").first()
    return render(request, "orders/order_success.html", {"order": order})
