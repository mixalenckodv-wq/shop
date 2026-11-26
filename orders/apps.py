from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
    verbose_name = "Заказы"

    def ready(self):
        # Подключаем сигналы Telegram-уведомлений.
        from . import signals  # noqa: F401
