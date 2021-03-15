from rest_framework import serializers
from smi.product.models import Product
from smi.factory.serializers import FactoryMiniSerializer


class ProductSerializer(serializers.ModelSerializer):
    factory = FactoryMiniSerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ProductMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'mat_id',
            'mat_name',
            'unit',
            'oldmaterial',
        )


class ProductMiddleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'mat_id',
            'mat_name',
            'unit',
            'pro_id',
            'proid_name',
            'mat_type',
            'mat_type_name',
            'oldmaterial',
        )

