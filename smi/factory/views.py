import django_filters
from datetime import datetime
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
import pandas as pd
from smi.core.utils.file_parser import xlsx_response
from smi.factory.models import Factory
from smi.factory.serializers import FactoryMiniSerializer, FactorySerializer, FactoryListSerializer
from smi.factory.filters import FactoryFilter

from smi.core.utils.etc import export_to_excel


class FactoryViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = FactorySerializer
    queryset = Factory.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = (
        'name',
        'code',
    )
    ordering_fields = '__all__'
    filter_class = FactoryFilter
    model = Factory

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return self.queryset
        else:
            return self.request.user.factories.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            return FactorySerializer
        else:
            return FactoryListSerializer

    @action(methods=['GET'], detail=False, url_path='mini-list')
    def mini_list(self, request):
        serializer = FactoryMiniSerializer(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def report(self, *args, **kwargs):
        qs = self.queryset.values(
            'plant_id',
            'plantname',
            'firmtext',
            'created_at',
            'create_user__full_name',
            'updated_at',
            'update_user__full_name'
        ).order_by(
            'created_at',
            'plant_id',
            'updated_at'
        )
        df_output = pd.DataFrame(qs)
        df_output.columns = (
            'plant_id',
            'plantname',
            'firmtext',
            'created_at',
            'create_user',
            'updated_at',
            'update_user',
        )
        excel_file = export_to_excel(df_output)
        response = xlsx_response(excel_file.read(),
                                 filename='factories {}'.format(datetime.today().strftime('%d/%m/%Y')))
        return response

