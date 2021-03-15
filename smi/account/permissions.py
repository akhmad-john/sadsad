from rest_framework import permissions



class RoleModelPermissions(permissions.DjangoModelPermissions):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        permissions = []
        for role in request.user.roles.all():
            permissions.extend(list(role.permissions.values_list('codename', flat=True)))
        permission_codename = '{}_{}'
        if request.method == 'GET':
            permission_codename = f'view_{view.model._meta.model_name}'
        elif request.method == 'POST':
            permission_codename = f'add_{view.model._meta.model_name}'
        elif request.method == 'PUT':
            permission_codename = f'change_{view.model._meta.model_name}'
        elif request.method == 'DELETE':
            permission_codename = f'delete_{view.model._meta.model_name}'
        permissions.append('view_order')
        return permission_codename in permissions