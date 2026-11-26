"""Webhook-эндпоинт для приёма обновлений от Telegram.

Telegram отправляет сюда POST-запросы с обновлениями. Для защиты endpoint
проверяем секретный заголовок X-Telegram-Bot-Api-Secret-Token, если он задан
в настройках (TELEGRAM_WEBHOOK_SECRET).
"""
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import client

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    """Принимает обновления от Telegram и отвечает 200 OK."""
    secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "")
    if secret:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header != secret:
            logger.warning("Webhook: неверный секретный заголовок.")
            return HttpResponseForbidden("forbidden")

    try:
        update = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        logger.warning("Webhook: некорректный JSON.")
        return HttpResponse("ok")  # 200, чтобы Telegram не долбил повторами

    _handle_update(update)
    return HttpResponse("ok")


def _handle_update(update):
    """Обработка входящего обновления.

    По умолчанию отвечаем на команду /start, показывая chat_id —
    это удобно, чтобы клиент узнал свой chat_id и указал его при заказе.
    """
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return

    if text.startswith("/start"):
        if not client.is_configured():
            return
        reply = (
            f"Здравствуйте! Ваш chat_id: <code>{chat_id}</code>\n"
            "Укажите его при оформлении заказа — и мы будем присылать "
            "статусы по вашему заказу."
        )
        try:
            client.send_message(chat_id, reply)
        except client.TelegramError:
            logger.exception("Webhook: не удалось ответить на /start чату %s", chat_id)
