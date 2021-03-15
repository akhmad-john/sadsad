import django_filters
from smi.account.models import User
from django.contrib.auth.models import Permission

from smi.account.models import Role


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = (
            'username',
            'factories',
            'roles',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'is_active',
            'is_superuser',
            'last_login',
            'date_joined'
        )


class PermissionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', method='filter_name')

    class Meta:
        model = Permission
        fields = ('id','name',)
    
    def filter_name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(name__iendswith = value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(name__istartswith = value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(name__icontains=value)
        return queryset


class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', method='filter_name')
    display_name = django_filters.CharFilter(field_name='name', method='filter_display_name')

    class Meta:
        model = Role
        fields = ('id','name', 'display_name')
    
    def filter_name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(name__iendswith = value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(name__istartswith = value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(name__icontains=value)
        return queryset
    
    def filter_display_name(self, queryset, name, value):
        if value.startswith('*'):
            queryset = queryset.filter(display_name__iendswith = value.translate({ord('*'): None}))
        elif value.endswith('*'):
            queryset = queryset.filter(display_name__istartswith = value.translate({ord('*'): None}))
        else:
            queryset = queryset.filter(display_name__icontains=value)
        return queryset