import os

from django.http import HttpResponse
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..document.models import ImageModel, DocumentModel
from ..document.serializers import ImageModelSerializer, DocumentSerializer
from ..document.tasks import create_thumbnail_images


class UploadDocumentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = DocumentSerializer
    queryset = DocumentModel.objects.all()
    model = DocumentModel

    def create(self, request, *args, **kwargs):
        if request.FILES and request.FILES.getlist("files"):
            objs = list()
            for file in request.FILES.getlist("files"):
                objs.append(DocumentModel(file=file))
            docs = DocumentModel.objects.bulk_create(objs)
            serializer = self.serializer_class(docs, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True, url_path='download')
    def download(self, request, *args, **kwargs):
        # TODO: dynamic content_type for file
        instance = self.get_object()
        response = HttpResponse(instance.file,
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f"attachment; filename={instance.file_name}"
        return response


class UploadImageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ImageModelSerializer
    queryset = ImageModel.objects.all()
    model = ImageModel

    def create(self, request, *args, **kwargs):
        if request.FILES and request.FILES.getlist("files"):
            objs = list()
            for file in request.FILES.getlist("files"):
                ct = os.path.splitext(file.name.lower())[1]
                if ct not in ('.jpg', '.jpeg', '.png'):
                    raise ValidationError('available format (.jpg, .jpeg, .png)')
                objs.append(ImageModel(file=file))
            images = ImageModel.objects.bulk_create(objs)
            serializer = self.serializer_class(images, many=True)
            obj_ids = [i.id for i in images]
            create_thumbnail_images(obj_ids)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

