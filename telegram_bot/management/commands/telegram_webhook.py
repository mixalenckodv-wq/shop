"""Management-команда управления webhook Telegram.

Примеры:
    python manage.py telegram_webhook --set
    python manage.py telegram_webhook --delete
    python manage.py telegram_webhook --info
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from telegram_bot import client


class Command(BaseCommand):
    help = "Устанавливает, удаляет или показывает статус webhook Telegram."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--set", action="store_true", help="Установить webhook")
        group.add_argument("--delete", action="store_true", help="Удалить webhook")
        group.add_argument("--info", action="store_true", help="Показать текущий webhook")

    def handle(self, *args, **options):
        if not client.is_configured():
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN не задан."))
            return

        try:
            if options["set"]:
                self._set_webhook()
            elif options["delete"]:
                result = client.delete_webhook()
                self.stdout.write(self.style.SUCCESS(
                    f"Webhook удалён: {result.get('description', 'ok')}"
                ))
            elif options["info"]:
                result = client._post("getWebhookInfo", {})
                self.stdout.write(str(result.get("result", {})))
        except client.TelegramError as exc:
            self.stderr.write(self.style.ERROR(f"Ошибка Telegram API: {exc}"))

    def _set_webhook(self):
        url = getattr(settings, "TELEGRAM_WEBHOOK_URL", "")
        if not url:
            self.stderr.write(self.style.ERROR("TELEGRAM_WEBHOOK_URL не задан."))
            return
        secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or None
        result = client.set_webhook(url, secret_token=secret)
        self.stdout.write(self.style.SUCCESS(
            f"Webhook установлен на {url}: {result.get('description', 'ok')}"
        ))
