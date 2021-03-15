import django_filters
from django.utils.crypto import get_random_string
import string
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from smi.product.serializers import ProductSerializer, ProductMiniSerializer
from smi.product.models import Product
from smi.product.filters import ProductFilter
from smi.product.tasks import sync_product_table


class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = (
        'mat_id',
        'mat_name',
    )
    ordering_fields = '__all__'

    filter_class = ProductFilter
    model = Product

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_superuser:
            return queryset
        factories = self.request.user.factories.all()
        return queryset.filter(factory__in=factories)

    @action(methods=['GET'], detail=False, url_path='mini-list')
    def mini_list(self, request):
        serializer = ProductMiniSerializer(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='sap-upload')
    def sap_upload(self, request):
        sync_product_table.delay()
        return Response(status=status.HTTP_200_OK)
