from django.conf.urls import url, include
from rest_framework import routers

from ..document.views import UploadImageViewSet, UploadDocumentViewSet

router = routers.DefaultRouter()
router.register(r'images', UploadImageViewSet)
router.register(r'documents', UploadDocumentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
