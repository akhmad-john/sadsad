import django_filters
from smi.product.models import Product


class ProductFilter(django_filters.FilterSet):

    class Meta:
        model = Product
        fields = '__all__'
