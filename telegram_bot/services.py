"""Формирование и отправка уведомлений по заказам.

Уведомление администратору — при создании заказа.
Уведомление клиенту — при смене статуса (например, «в обработке»).
Все ошибки отправки логируются и не прерывают бизнес-логику заказа.
"""
import logging

from django.conf import settings

from . import client

logger = logging.getLogger(__name__)


def _escape(value):
    """Минимальное экранирование под parse_mode=HTML."""
    text = "" if value is None else str(value)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _order_lines(order):
    lines = []
    for item in order.items.all():
        size = f", размер {item.size}" if item.size is not None else ""
        lines.append(
            f"• {_escape(item.product_name)}{size} — "
            f"{item.quantity} × {item.price} ₽ = {item.subtotal} ₽"
        )
    return "\n".join(lines) or "• (позиции отсутствуют)"


def build_admin_message(order):
    """Текст уведомления для администратора о новом заказе."""
    return (
        f"🛒 <b>Новый заказ #{order.id}</b>\n"
        f"Клиент: {_escape(order.first_name)} {_escape(order.last_name)}\n"
        f"Телефон: {_escape(order.phone)}\n"
        f"Email: {_escape(order.email) or '—'}\n"
        f"Адрес: {_escape(order.address)}\n\n"
        f"{_order_lines(order)}\n\n"
        f"<b>Итого: {order.total_price} ₽</b>"
    )


def build_customer_status_message(order):
    """Текст уведомления клиенту о статусе заказа."""
    return (
        f"✅ <b>Ваш заказ #{order.id} принят в обработку</b>\n\n"
        f"{_order_lines(order)}\n\n"
        f"Итого: <b>{order.total_price} ₽</b>\n"
        f"Статус: {_escape(order.get_status_display())}\n\n"
        f"Мы свяжемся с вами для подтверждения."
    )


def notify_admin_new_order(order):
    """Отправляет администратору уведомление о новом заказе.

    Возвращает True при успешной отправке, иначе False (ошибка логируется).
    """
    if not client.is_configured():
        logger.warning("Telegram не настроен — уведомление администратору пропущено.")
        return False
    admin_chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "")
    if not admin_chat_id:
        logger.warning("TELEGRAM_ADMIN_CHAT_ID не задан — уведомление пропущено.")
        return False
    try:
        client.send_message(admin_chat_id, build_admin_message(order))
        return True
    except client.TelegramError:
        logger.exception("Не удалось отправить уведомление администратору о заказе #%s", order.id)
        return False


def notify_customer_status(order):
    """Отправляет клиенту сообщение, что заказ в обработке.

    chat_id клиента хранится в заказе (Order.telegram_chat_id).
    """
    if not client.is_configured():
        logger.warning("Telegram не настроен — уведомление клиенту пропущено.")
        return False
    chat_id = getattr(order, "telegram_chat_id", "")
    if not chat_id:
        logger.info("У заказа #%s нет telegram_chat_id — сообщение клиенту пропущено.", order.id)
        return False
    try:
        client.send_message(chat_id, build_customer_status_message(order))
        return True
    except client.TelegramError:
        logger.exception("Не удалось отправить статус клиенту по заказу #%s", order.id)
        return False
