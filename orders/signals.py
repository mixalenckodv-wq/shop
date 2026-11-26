"""Сигналы заказов для Telegram-уведомлений.

- post_save: при создании заказа — уведомляем администратора;
- при смене статуса на «В обработке» — уведомляем клиента.

Отправка выполняется после коммита транзакции, чтобы уведомление уходило
только по реально сохранённому заказу.
"""
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def on_order_saved(sender, instance, created, **kwargs):
    # Импортируем лениво, чтобы избежать циклических импортов и работы при
    # неприменённых миграциях.
    from telegram_bot import services as tg

    if created:
        transaction.on_commit(lambda: tg.notify_admin_new_order(instance))
        return

    if instance.status == Order.Status.PROCESSING:
        transaction.on_commit(lambda: tg.notify_customer_status(instance))
