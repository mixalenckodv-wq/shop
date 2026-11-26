from django.contrib import admin

from .models import Category, Product, ProductSize


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "brand", "category", "price",
        "gender", "is_active", "total_stock",
    )
    list_filter = ("is_active", "gender", "category")
    search_fields = ("name", "brand")
    list_select_related = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductSizeInline]


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "stock")
    list_filter = ("size",)
    search_fields = ("product__name", "product__brand")
    list_select_related = ("product",)
