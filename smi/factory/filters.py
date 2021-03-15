import django_filters
from smi.factory.models import Factory


class FactoryFilter(django_filters.FilterSet):
    class Meta:
        model = Factory
        exclude = ('factory_link', 'tex_link')
