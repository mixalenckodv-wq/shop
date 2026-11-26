"""Точка входа для настройки Telegram-бота в режиме webhook.

В webhook-режиме отдельный постоянно работающий процесс не нужен:
Django сам принимает обновления на /telegram/webhook/. Этот модуль
используется, чтобы один раз зарегистрировать webhook в Telegram.

Запуск:
    python -m telegram_bot.bot
"""
import logging
import sys

import django

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("telegram_bot")


def main():
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.conf import settings

    from telegram_bot import client

    if not client.is_configured():
        logger.error("TELEGRAM_BOT_TOKEN не задан — настройка webhook невозможна.")
        return 1

    webhook_url = getattr(settings, "TELEGRAM_WEBHOOK_URL", "")
    if not webhook_url:
        logger.error("TELEGRAM_WEBHOOK_URL не задан — некуда регистрировать webhook.")
        return 1

    secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or None
    try:
        result = client.set_webhook(webhook_url, secret_token=secret)
    except client.TelegramError as exc:
        logger.error("Не удалось установить webhook: %s", exc)
        return 1

    logger.info("Webhook установлен: %s", result.get("description", "ok"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
