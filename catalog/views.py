from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Category, Product


class ProductListView(ListView):
    """Каталог товаров с фильтром по категории и поиском по названию."""

    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("sizes")
        )
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug, category__is_active=True)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(name__icontains=query) | qs.filter(brand__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["selected_category"] = self.request.GET.get("category", "")
        context["query"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    """Карточка товара с доступными размерами."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("sizes")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_sizes"] = self.object.sizes.filter(stock__gt=0)
        context["related_products"] = (
            Product.objects.filter(
                is_active=True, category=self.object.category
            )
            .exclude(pk=self.object.pk)[:4]
        )
        return context
