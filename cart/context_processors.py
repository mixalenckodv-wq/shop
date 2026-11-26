"""Контекст-процессор, добавляющий сводку корзины во все шаблоны.

Благодаря ему в шапке сайта всегда доступен счётчик товаров и сумма,
без ручной передачи контекста из каждой вьюхи.
"""


def cart(request):
    from . import services

    try:
        summary = services.cart_summary(request)
    except Exception:  # noqa: BLE001 — не ломаем страницу из-за корзины
        return {"cart_total_quantity": 0, "cart_total_price": 0}
    return {
        "cart_total_quantity": summary["cart_total_quantity"],
        "cart_total_price": summary["cart_total_price"],
    }
