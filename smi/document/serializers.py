from rest_framework import serializers
from ..document.models import ImageModel, DocumentModel


class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True)

    class Meta:
        model = DocumentModel
        fields = '__all__'


class ImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageModel
        fields = (
            'id',
            'file',
            'thumbnail_150',
        )
        read_only_fields = (
            'thumbnail_150',
        )

