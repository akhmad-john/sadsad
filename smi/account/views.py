import django_filters
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import Permission
from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from smi.account.models import User, Role
from smi.account.serializers import UserSerializer, EmptySerializer, UserCreateSerializer, RoleSerializer, \
    RoleRecursiveSerializers, PermissionSerializer
from smi.account.filters import UserFilter, PermissionFilter, RoleFilter


class CustomAuthToken(ObtainAuthToken, CreateAPIView):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(instance=user).data
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return Response({
            'token': token.key,
            'user': user_data,
        })


class Logout(CreateAPIView):
    serializer_class = EmptySerializer

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if request.user and getattr(request.user, 'id'):
            token = Token.objects.get(user=request.user)
            if token:
                if request.user.is_mes == False:
                    token.delete()
        return Response(status=status.HTTP_200_OK)


class UserViewSet(ListCreateAPIView, RetrieveUpdateAPIView, GenericViewSet):
    serializer_class = UserSerializer
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'username',
    )
    ordering_fields = '__all__'
    filter_class = UserFilter
    queryset = User.objects.filter(is_mes=False)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            return UserCreateSerializer
        else:
            return UserSerializer

    model = User


class RoleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    search_fields = '__all__'
    ordering_fields = '__all__'
    filter_class = RoleFilter

    @action(methods=['GET'], detail=False, url_path='recursive-list')
    def recursive_list(self, request):
        serializer = RoleRecursiveSerializers(self.filter_queryset(self.get_queryset().filter(parent=None)), many=True)
        return Response(serializer.data)

    model = Role


class PermissionViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    search_fields = '__all__'
    ordering_fields = '__all__'
    filter_class = PermissionFilter
    model = Permission

