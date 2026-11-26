"""Сервисный слой корзины.

Корзина хранится в БД (модели Cart/CartItem). Для гостей используется
session_key, для авторизованных пользователей — user. Вся логика
добавления/изменения/очистки собрана здесь, чтобы вьюхи оставались тонкими
и её можно было покрыть тестами.
"""
from decimal import Decimal

from django.db import transaction

from catalog.models import Product, ProductSize
from orders.models import Cart, CartItem


def get_or_create_cart(request):
    """Возвращает корзину для текущего запроса, создавая её при необходимости.

    Авторизованный пользователь всегда получает свою корзину по user.
    Гость получает корзину по session_key (сессия создаётся лениво).
    """
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
    return cart


def _resolve_size(product, size_id):
    if not size_id:
        return None
    return (
        ProductSize.objects.filter(pk=size_id, product=product).first()
    )


@transaction.atomic
def add_to_cart(request, product_id, size_id=None, quantity=1):
    """Добавляет товар в корзину. Возвращает позицию корзины.

    Поднимает ValueError при некорректных данных, чтобы вьюха могла
    показать понятное сообщение пользователю.
    """
    quantity = int(quantity)
    if quantity < 1:
        raise ValueError("Количество должно быть не меньше 1.")

    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        raise ValueError("Товар не найден или недоступен.")

    product_size = _resolve_size(product, size_id)

    if product_size is not None and product_size.stock < 1:
        raise ValueError("Выбранного размера нет в наличии.")

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        product_size=product_size,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity"])
    return item


@transaction.atomic
def update_item_quantity(request, item_id, quantity):
    """Меняет количество позиции. quantity <= 0 — удаляет позицию."""
    cart = get_or_create_cart(request)
    item = CartItem.objects.filter(pk=item_id, cart=cart).first()
    if item is None:
        raise ValueError("Позиция корзины не найдена.")

    quantity = int(quantity)
    if quantity <= 0:
        item.delete()
        return None

    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item


def remove_item(request, item_id):
    """Удаляет позицию из корзины. Возвращает True, если удалили."""
    cart = get_or_create_cart(request)
    deleted, _ = CartItem.objects.filter(pk=item_id, cart=cart).delete()
    return deleted > 0


def clear_cart(request):
    """Полностью очищает корзину текущего запроса."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return cart


def cart_summary(request):
    """Краткая сводка корзины для контекста шаблонов."""
    cart = get_or_create_cart(request)
    items = list(cart.items.select_related("product", "product_size").all())
    total_price = sum((item.subtotal for item in items), Decimal("0.00"))
    total_quantity = sum(item.quantity for item in items)
    return {
        "cart": cart,
        "cart_items": items,
        "cart_total_price": total_price,
        "cart_total_quantity": total_quantity,
    }
