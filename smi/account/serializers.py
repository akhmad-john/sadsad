from rest_framework import serializers
from django.contrib.auth.models import Permission
from smi.account.models import User, Role
from smi.factory.models import Factory
from smi.factory.serializers import FactoryMiniSerializer


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            'id',
            'name',
            'codename',
        )


class PermissionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            'id',
            'name',
        )


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField('get_permissions')

    def get_permissions(self, obj):
        result = [codename for codename in obj.permissions.values_list('codename', flat=True)]
        permissions = {}
        if result:
            for perm in result:
                permissions[perm] = True
        return permissions

    class Meta:
        model = Role
        fields = '__all__'


class RoleRecursiveSerializers(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(
        read_only=True, method_name="get_child_roles")

    permissions = PermissionMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'permissions',
            'children'
        )

    def get_child_roles(self, obj):
        """ self referral field """
        if obj.children:
            serializer = RoleRecursiveSerializers(
                instance=obj.children.all(),
                many=True
            )
            return serializer.data
        else:
            return None


class RecursiveRoleSerializers(serializers.ModelSerializer):
    def __init__(self, *args, user=None, **kwargs):
        super(RecursiveRoleSerializers, self).__init__(*args, **kwargs)
        self.user = user

    children = serializers.SerializerMethodField(
        read_only=True, method_name="get_child_roles")

    permissions = PermissionMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'permissions',
            'children',
        )

    def get_child_roles(self, obj):
        """ self referral field """
        if self.user:
            serializer = RecursiveRoleSerializers(
                user=self.user,
                instance=obj.children.filter(
                    id__in=list(role.id for role in list(self.user.roles.all().exclude(parent=None)))),
                many=True
            )
            return serializer.data


class UserSerializer(serializers.ModelSerializer):
    factories = FactoryMiniSerializer(many=True)
    roles = serializers.SerializerMethodField('get_roles')

    def get_roles(self, obj):
        roles = obj.roles.values_list('name', 'display_name', 'permissions__codename')
        result = {}
        for k, display_name, perm in roles:
            if k not in result:
                result[k] = {"permissions": {}, 'display_name': display_name}
            if perm:
                result[k]['permissions'].update(**{str(perm): True})

        # qs = Role.objects.filter(parent=None, users=obj)
        # serializer = RecursiveRoleSerializers(user=obj,instance=qs, many=True)
        return result

    class Meta:
        model = User
        fields = (
            'id',
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


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'full_name',
        )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'factories',
            'first_name',
            'last_name',
            'is_superuser',
            'roles',
        )

    def create(self, validated_data):
        password = validated_data['password']
        factories = validated_data.pop('factories', [])
        roles = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)
        user.factories.set(factories)
        user.roles.set(roles)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        factories = validated_data.pop('factories', [])
        roles = validated_data.pop('roles', [])
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        instance.factories.set(factories)
        instance.roles.set(roles)
        return instance


class EmptySerializer(serializers.Serializer):
    pass

