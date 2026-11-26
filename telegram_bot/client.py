"""Тонкий HTTP-клиент Telegram Bot API.

Отправка сообщений выполняется обычными POST-запросами к Bot API, поэтому
дополнительные зависимости не нужны — используем стандартный urllib.
Токен берётся из настроек (переменная окружения TELEGRAM_BOT_TOKEN).
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org"
REQUEST_TIMEOUT = 10


class TelegramError(Exception):
    """Ошибка при обращении к Telegram Bot API."""


def _api_url(method):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise TelegramError("TELEGRAM_BOT_TOKEN не задан.")
    return f"{API_BASE}/bot{token}/{method}"


def _post(method, payload):
    """Отправляет POST-запрос к Bot API и возвращает распарсенный JSON."""
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _api_url(method),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise TelegramError(f"Telegram API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise TelegramError(f"Не удалось связаться с Telegram API: {exc.reason}") from exc

    result = json.loads(body)
    if not result.get("ok"):
        raise TelegramError(result.get("description", "Неизвестная ошибка Telegram API"))
    return result


def is_configured():
    """Настроена ли интеграция (есть токен)."""
    return bool(getattr(settings, "TELEGRAM_BOT_TOKEN", ""))


def send_message(chat_id, text, parse_mode="HTML"):
    """Отправляет текстовое сообщение в чат.

    Возвращает dict с ответом Bot API. Бросает TelegramError при сбое.
    """
    if not chat_id:
        raise TelegramError("Не указан chat_id получателя.")
    return _post(
        "sendMessage",
        {"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
    )


def set_webhook(url, secret_token=None):
    """Устанавливает webhook для бота."""
    payload = {"url": url, "allowed_updates": ["message"]}
    if secret_token:
        payload["secret_token"] = secret_token
    return _post("setWebhook", payload)


def delete_webhook():
    """Удаляет webhook (полезно при отладке через polling)."""
    return _post("deleteWebhook", {})
