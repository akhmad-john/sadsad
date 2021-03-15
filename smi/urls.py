"""smi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from .document.urls import urlpatterns as document_urls
from smi.account import views as account_views
from smi.factory import views as factory_views
from smi.product import views as product_views
from smi.zone import views as zone_views
from smi.order import views as order_views
from smi.movement import views as movement_views

account_router = routers.DefaultRouter()
account_router.register(r'users', account_views.UserViewSet)
account_router.register(r'roles', account_views.RoleViewSet)
account_router.register(r'permissions', account_views.PermissionViewSet)

factory_router = routers.DefaultRouter()
factory_router.register(r'factories', factory_views.FactoryViewSet)

zone_router = routers.DefaultRouter()
zone_router.register(r'zones', zone_views.ZoneViewSet)

product_router = routers.DefaultRouter()
product_router.register(r'products', product_views.ProductViewSet)

order_router = routers.DefaultRouter()
order_router.register(r'orders', order_views.OrderViewSet)
order_router.register(r'check', order_views.OrderCheckViewSet)
order_router.register(r'nekonv-logs', order_views.NeKonvOrderCloseViewSet)
order_router.register(r'konv-logs', order_views.KonvOrderCloseViewSet)
order_router.register(r'reports', order_views.OrderReportViewSet)


movement_router = routers.DefaultRouter()
movement_router.register(r'id-cards', movement_views.IdCardViewSet)
movement_router.register(r'cards-upload', movement_views.IdCardFileUploadViewSet)
movement_router.register(r'product-movements-upload', movement_views.PrMovFileUploadViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('account/', include(account_router.urls)),
    path('account/login/', account_views.CustomAuthToken.as_view(), name="login"),
    path('account/logout/', account_views.Logout.as_view(), name="logout"),

    path('factory/', include(factory_router.urls)),
    path('product/', include(product_router.urls)),
    path('zone/', include(zone_router.urls)),
    path('order/', include(order_router.urls)),
    path('movement/', include(movement_router.urls)),
    path('mes/order/order-close/', order_views.NeKonvOrederView.as_view(), name='order_close'),

    path('mes/movement/get-product-post/', movement_views.MesPostView.as_view(), name='mespost'),
    path('mes/movement/send-product-post/', movement_views.MesSapPostView.as_view(), name='messappost'),
    path('api-file/', include(document_urls)),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
