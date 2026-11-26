from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_quantity", "total_price", "updated_at")
    search_fields = ("user__username", "session_key")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "size", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "first_name", "last_name", "phone",
        "status", "total_price", "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]
    list_select_related = ("user",)

    fieldsets = (
        ("Клиент", {
            "fields": ("user", "first_name", "last_name", "email", "phone", "telegram_chat_id")
        }),
        ("Доставка", {"fields": ("address", "comment")}),
        ("Статус", {"fields": ("status", "created_at", "updated_at")}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "size", "price", "quantity", "subtotal")
    search_fields = ("product_name", "order__id")
    list_select_related = ("order", "product")
