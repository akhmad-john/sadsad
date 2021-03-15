from rest_framework import serializers
from smi.factory.models import Factory


class FactorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Factory
        exclude = (
            'created_at',
            'create_by',
            'update_by',
            'updated_at',
            'factory_link',
            'tex_link',
        )


class FactoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Factory
        exclude = (
            'factory_link',
            'tex_link',
        )


class FactoryMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Factory
        fields = (
            'id',
            'plant_id',
            'plantname',
        )


