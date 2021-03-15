import django_filters

from smi.movement.models import IdCard, ProductMovement, MovementLog, TransferLog


class IdCardFilter(django_filters.FilterSet):
    factory_name = django_filters.CharFilter(method='filter_factory_plantname')
    factory_plantid = django_filters.CharFilter(method='filter_factory_plantid')
    card_number = django_filters.CharFilter(field_name='card_number', method='filter_card_number')
    name = django_filters.CharFilter(field_name='name', method='filter_name')

    class Meta:
        model = IdCard
        fields = ('id', 'card_number', 'name', 'factory_name', 'factory_plantid')

    def filter_factory_plantname(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(factory__plantname__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(factory__plantname__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(factory__plantname__icontains=value)
        return queryset

    def filter_factory_plantid(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(factory__plant_id__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(factory__plant_id__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(factory__plant_id__icontains=value)
        return queryset

    def filter_name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(name__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(name__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(name__icontains=value)
        return queryset

    def filter_card_number(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(card_number__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(card_number__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(card_number__icontains=value)
        return queryset


class ProductMovementFilter(django_filters.FilterSet):
    zone_from_zone_id = django_filters.CharFilter(method='filter_zone_from__zone_id')
    zone_from_zonename = django_filters.CharFilter(method='filter_zone_from__zonename')
    zone_from_p_number = django_filters.CharFilter(method='filter_zone_from__p_number')
    zone_from_ip_address = django_filters.CharFilter(method='filter_zone_from__ip_address')
    zone_from_factory_plantname = django_filters.CharFilter(method='filter_zone_from__factory__plantname')
    zone_from_factory_plant_id = django_filters.CharFilter(method='filter_zone_from__factory__plant_id')
    zone_to_zone_id = django_filters.CharFilter(method='filter_zone_to__zone_id')
    zone_to_zonename = django_filters.CharFilter(method='filter_zone_to__zonename')
    zone_to_p_number = django_filters.CharFilter(method='filter_zone_to__p_number')
    zone_to_ip_address = django_filters.CharFilter(method='filter_zone_to__ip_address')
    zone_to_factory_plantname = django_filters.CharFilter(method='filter_zone_to__factory__plantname')
    zone_to_factory_plant_id = django_filters.CharFilter(method='filter_zone_to__factory__plant_id')
    idcard_om_idcard_number = django_filters.CharFilter(method='filter_card_om__card_number')
    idcard_om_name = django_filters.CharFilter(method='filter_card_om__name')
    idcard_pm_idcard_number = django_filters.CharFilter(method='filter_card_pm__card_number')
    idcard_pm_name = django_filters.CharFilter(method='filter_card_pm__name')

    class Meta:
        model = ProductMovement
        fields = ('id',
                  'zone_from_zone_id',
                  'zone_from_zonename',
                  'zone_from_p_number',
                  'zone_from_ip_address',
                  'zone_from_factory_plantname',
                  'zone_from_factory_plant_id',
                  'zone_to_zone_id',
                  'zone_to_zonename',
                  'zone_to_p_number',
                  'zone_to_ip_address',
                  'zone_to_factory_plantname',
                  'zone_to_factory_plant_id',
                  'idcard_om_name',
                  'idcard_om_idcard_number',
                  'idcard_pm_name',
                  'idcard_pm_idcard_number',
                  )

    def filter_zone_from__zone_id(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__zone_id__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__zone_id__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__zone_id__icontains=value)
        return queryset

    def filter_zone_from__zonename(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__zonename__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__zonename__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__zonename__icontains=value)
        return queryset

    def filter_zone_from__p_number(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__p_number__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__p_number__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__p_number__icontains=value)
        return queryset

    def filter_zone_from__ip_address(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__ip_address__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__ip_address__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__ip_address__icontains=value)
        return queryset

    def filter_zone_from__factory__plantname(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__factory__plantname__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__factory__plantname__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__factory__plantname__icontains=value)
        return queryset

    def filter_zone_from__factory__plant_id(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_from__factory__plant_id__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_from__factory__plant_id__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_from__factory__plant_id__icontains=value)
        return queryset

    def filter_zone_to__zone_id(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__zone_id__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__zone_id__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__zone_id__icontains=value)
        return queryset

    def filter_zone_to__zonename(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__zonename__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__zonename__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__zonename__icontains=value)
        return queryset

    def filter_zone_to__p_number(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__p_number__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__p_number__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__p_number__icontains=value)
        return queryset

    def filter_zone_to__ip_address(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__ip_address__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__ip_address__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__ip_address__icontains=value)
        return queryset

    def filter_zone_to__factory__plantname(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__factory__plantname__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__factory__plantname__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__factory__plantname__icontains=value)
        return queryset

    def filter_zone_to__factory__plant_id(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(zone_to__factory__plant_id__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(zone_to__factory__plant_id__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(zone_to__factory__plant_id__icontains=value)
        return queryset

    def filter_card_om__name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(card_om__name__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(card_om__name__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(card_om__name__icontains=value)
        return queryset

    def filter_card_om__card_number(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(card_om__card_number__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(card_om__card_number__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(card_om__card_number__icontains=value)
        return queryset

    def filter_card_pm__name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(card_pm__name__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(card_pm__name__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(card_pm__name__icontains=value)
        return queryset

    def filter_card_pm__card_number(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(card_pm__card_number__iendswith=value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(card_pm__card_number__istartswith=value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(card_pm__card_number__icontains=value)
        return queryset


class MovementLogFilter(django_filters.FilterSet):
    class Meta:
        model = MovementLog
        fields = '__all__'


class TransferLogFilter(django_filters.FilterSet):
    class Meta:
        model = TransferLog
        fields = '__all__'
