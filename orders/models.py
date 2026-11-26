from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Product, ProductSize


class Cart(models.Model):
    """Корзина покупателя: привязана к пользователю или к сессии гостя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        null=True, blank=True,
        related_name="carts",
        on_delete=models.CASCADE,
    )
    session_key = models.CharField(
        "Ключ сессии", max_length=40, blank=True, db_index=True
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        owner = self.user or self.session_key or "аноним"
        return f"Корзина #{self.pk} ({owner})"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Позиция корзины: товар, размер и количество."""

    cart = models.ForeignKey(
        Cart, verbose_name="Корзина", related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )
    product_size = models.ForeignKey(
        ProductSize, verbose_name="Размер", null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    added_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "product_size"],
                name="unique_cart_item",
            )
        ]

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказ покупателя."""

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PROCESSING = "processing", "В обработке"
        SHIPPED = "shipped", "Отправлен"
        DONE = "done", "Выполнен"
        CANCELED = "canceled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        null=True, blank=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=30)
    telegram_chat_id = models.CharField(
        "Telegram chat_id", max_length=64, blank=True,
        help_text="Для отправки статуса заказа клиенту",
    )
    address = models.TextField("Адрес доставки")
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Заказ #{self.pk} — {self.first_name} ({self.get_status_display()})"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Позиция заказа. Цену и название фиксируем на момент оформления."""

    order = models.ForeignKey(
        Order, verbose_name="Заказ", related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    product_name = models.CharField("Название товара", max_length=200)
    size = models.DecimalField(
        "Размер", max_digits=4, decimal_places=1, null=True, blank=True
    )
    price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
