import django_filters
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action

from smi.zone.models import Zone, ZoneFile
from smi.zone.serializers import ZoneSerializer, ZoneMiniSerializer, ZoneCreateSerializer, ZoneFileUploadSerializer
from smi.zone.filters import ZoneFilter
from smi.zone.utils.file_parser import parse_zone_from_file


class ZoneViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin, GenericViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = (
        'zonename',
        'zone_id',
        'indicator',
        'ip_address',
        'p_number',
    )
    ordering_fields = (
        'id',
        'zone_id',
        'zonename',
        'indicator__name',
        'direction__name',
        'head_panel',
        'factory__id',
        'ip_address',
        'created_at',
        'create_user',
        'updated_at',
        'update_user',
        'factory__plantname',
        'p_number',
        'factory__plant_id',
        'p_name'
    )
    filter_class = ZoneFilter
    model = Zone

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset
        factories = self.request.user.factories.all()
        return self.queryset.filter(factory__in=factories)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            return ZoneCreateSerializer
        else:
            return ZoneSerializer

    @action(methods=['GET'], detail=False, url_path='mini-list')
    def mini_list(self, request):
        serializer = ZoneMiniSerializer(self.filter_queryset(self.get_queryset()), many=True)
        return response.Response(serializer.data)


class ZoneFileUploadViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ZoneFileUploadSerializer
    queryset = ZoneFile.objects.all()

    def perform_create(self, serializer):
        obj = serializer.save()
        parse_zone_from_file(obj.id)

