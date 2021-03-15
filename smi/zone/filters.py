import django_filters
from django.db.models import Q

from smi.core.filters import filter_contains
from smi.zone.models import Zone


class ZoneFilter(django_filters.FilterSet):
    zonename = django_filters.CharFilter(field_name='zonename', method=filter_contains)
    ip_address = django_filters.CharFilter(field_name='ip_address', method=filter_contains)
    factory_name = django_filters.CharFilter(field_name='factory__plantname', method=filter_contains)
    factory = django_filters.CharFilter(field_name='factory__plant_id', method=filter_contains)
    zone_id = django_filters.CharFilter(field_name='zone_id', method=filter_contains)
    p_number = django_filters.CharFilter(field_name='p_number', method=filter_contains)
    p_name = django_filters.CharFilter(field_name='p_number', method=filter_contains)
    head_panel = django_filters.CharFilter(field_name='head_panel', method=filter_contains)
    indicator = django_filters.CharFilter(field_name='indicator__name', method=filter_contains)
    direction = django_filters.CharFilter(field_name='direction__name', method=filter_contains)
    group_by = django_filters.CharFilter(method='filter_group_by')

    class Meta:
        model = Zone
        fields = (
            'id',
            'zone_id',
            'zonename',
            'factory',
            'ip_address',
            'created_at',
            'create_by',
            'updated_at',
            'update_by',
            'factory_name',
            'p_number',
            'p_name',
            'head_panel'
        )

    def filter_group_by(self, queryset, name, value):
        queryset = queryset.distinct(value).order_by(value)
        return queryset
