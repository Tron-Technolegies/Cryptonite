# filters.py
import django_filters
from AdminApp.models import Product


# 🔹 enable ?brand=a,b,c
class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    # price range
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # multi-select
    brand = CharInFilter(field_name="brand", lookup_expr="in")
    coin = CharInFilter(field_name="currency", lookup_expr="in")

    # boolean
    inStock = django_filters.BooleanFilter(field_name="is_available")

    class Meta:
        model = Product
        fields = [
            "brand",
            "currency",
            "is_available",
        ]
