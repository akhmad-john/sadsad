import django_filters
from django.db.models import Q

from smi.core.filters import filter_contains
from smi.order.models import Order, Log, NeKonvOrderClose, KonvOrderClose, NeKonvOrderCloseReport


class OrderFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name="id", method=filter_contains)
    aufnr = django_filters.CharFilter(field_name='aufnr', method=filter_contains)
    mat_id = django_filters.CharFilter(field_name='product__mat_id', method=filter_contains)
    mat_name = django_filters.CharFilter(field_name='product__mat_name', method=filter_contains)
    psmng = django_filters.CharFilter(field_name='psmng', method=filter_contains)
    mat_type = django_filters.CharFilter(field_name='product__mat_type', method=filter_contains)
    zonename = django_filters.CharFilter(field_name='zone__zonename', method=filter_contains)
    ip_address = django_filters.CharFilter(field_name='zone__ip_address', method=filter_contains)
    p_number = django_filters.CharFilter(field_name='zone__p_number', method=filter_contains)
    status = django_filters.CharFilter(field_name='status', method=filter_contains)
    create_update = django_filters.CharFilter(method='filter_create_update')
    created_at = django_filters.DateFilter(field_name='created_at__date', input_formats=['%Y-%m-%d', ],
                                           lookup_expr='icontains')
    order_date = django_filters.DateFilter(field_name='order_date__date', input_formats=['%Y-%m-%d', ],
                                           lookup_expr='icontains')
    from_date = django_filters.DateFilter(field_name='created_at__date', input_formats=['%Y-%m-%d', ],
                                          lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='created_at__date', input_formats=['%Y-%m-%d', ],
                                        lookup_expr='lte')

    class Meta:
        model = Order
        fields = (
            'id',
            'factory',
            'product',
            'aufnr',
            'mat_id',
            'psmng',
            'mat_name',
            'mat_type',
            'zonename',
            'ip_address',
            'p_number',
            'created_at',
            'status',
            'create_update',
            'order_date',
        )

    def filter_create_update(self, queryset, name, value):
        if value == 'create':
            queryset = queryset.filter(Q(status="Error") | Q(status="MesError"))
        elif value == 'update':
            queryset = queryset.filter(Q(status="EditError") | Q(status="EditMesError"))
        return queryset


class LogFilter(django_filters.FilterSet):

    class Meta:
        model = Log
        exclude = ('message',)


class NeKonvOrderCloseFilter(django_filters.FilterSet):

    class Meta:
        model = NeKonvOrderClose
        exclude = ('data',)


class KonvOrderCloseFilter(django_filters.FilterSet):

    class Meta:
        model = KonvOrderClose
        exclude = ('data',)


class NeKonvOrderCloseReportFilter(django_filters.FilterSet):
    from_date = django_filters.DateTimeFilter(field_name='created_at', input_formats=['%Y-%m-%d %H:%M'],
                                              lookup_expr='gt')
    to_date = django_filters.DateTimeFilter(field_name='updated_at', input_formats=['%Y-%m-%d %H:%M'],
                                            lookup_expr='lt')
    mat_id = django_filters.CharFilter(field_name='product__mat_id', method=filter_contains)
    mat_name = django_filters.CharFilter(field_name='product__mat_name', method="filter_mat_name")
    p_number = django_filters.CharFilter(method="filter_p_number")

    class Meta:
        model = NeKonvOrderCloseReport
        fields = (
            'product',
            'mat_id',
            'mat_name',
            'from_date',
            'to_date',
            'p_number'
        )

    def filter_p_number(self, queryset, name, value):
        p_number_list = value.split(',')
        queryset = queryset.filter(zone__p_number__in=p_number_list)
        return queryset
