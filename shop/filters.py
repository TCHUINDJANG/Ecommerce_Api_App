import django_filters
from .models import Product
from django.db.models import Avg




class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name = 'price',
        lookup_expr='gte'
    )

    max_price = django_filters.NumberFilter(
        field_name = 'price',
        lookup_expr='lte'
    )

    category = django_filters.CharFilter(
        field_name='category__slug'
    )

    in_stock = django_filters.BooleanFilter(
        field_name='stock',
        lookup_expr='isnull',
        label='En stock'
    )

    has_discount = django_filters.BooleanFilter(
        field_name='discount_price',
        lookup_expr='isnull',
        exclude=True,
        label="En promotion"
    )

    min_rating = django_filters.NumberFilter(
        method='filter_by_rating',
        label="Note minimale"
    )

    class Meta:
        model = Product
        fields = ['category' , 'available']


    def filter_by_rating(self , queryset , name , value):
        return queryset.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=value)