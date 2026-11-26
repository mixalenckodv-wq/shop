from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Категория обуви (кроссовки, ботинки, сандалии и т.д.)."""

    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Слаг", max_length=140, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Product(models.Model):
    """Товар — конкретная модель обуви."""

    class Gender(models.TextChoices):
        MEN = "men", "Мужская"
        WOMEN = "women", "Женская"
        UNISEX = "unisex", "Унисекс"
        KIDS = "kids", "Детская"

    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", max_length=220, unique=True, blank=True)
    brand = models.CharField("Бренд", max_length=120, blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    gender = models.CharField(
        "Пол", max_length=10, choices=Gender.choices, default=Gender.UNISEX
    )
    color = models.CharField("Цвет", max_length=60, blank=True)
    image = models.ImageField("Изображение", upload_to="products/", blank=True)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.brand} {self.name}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def total_stock(self):
        return sum(size.stock for size in self.sizes.all())

    @property
    def in_stock(self):
        return self.total_stock > 0


class ProductSize(models.Model):
    """Размер товара и остаток на складе."""

    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        related_name="sizes",
        on_delete=models.CASCADE,
    )
    size = models.DecimalField(
        "Размер", max_digits=4, decimal_places=1,
        help_text="Например: 42, 42.5, 36",
    )
    stock = models.PositiveIntegerField("Остаток", default=0)

    class Meta:
        verbose_name = "Размер товара"
        verbose_name_plural = "Размеры товара"
        ordering = ["size"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size"], name="unique_product_size"
            )
        ]

    def __str__(self):
        return f"{self.product} — {self.size} ({self.stock} шт.)"
