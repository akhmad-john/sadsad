

def filter_contains(queryset, name, value):
    """
    :param queryset:
    :param name: name of field
    :param value: * in start or end of the string do extra logic
    :return: queryset with filters
    """
    if value.startswith('*'):
        queryset = queryset.filter(**{f'{name}__iendswith': value.translate({ord('*'): None})})
    elif value.endswith('*'):
        queryset = queryset.filter(**{f'{name}__istartswith': value.translate({ord('*'): None})})
    else:
        queryset = queryset.filter(name__icontains=value)
    return queryset
