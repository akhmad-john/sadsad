import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from smi.document.models import DocumentModel
from smi.movement.models import IdCard, ProductMovement, MovementLog, TransferLog, LogMaterial, IdCardFile, \
    ProductMovementFile

from smi.factory.serializers import FactoryMiniSerializer
from smi.zone.serializers import ZoneMovementSerializer
from smi.account.serializers import UserMiniSerializer


class IdCardSerializer(serializers.ModelSerializer):
    factory = FactoryMiniSerializer()

    class Meta:
        model = IdCard
        fields = '__all__'


class IdCardMiniSerializer(serializers.ModelSerializer):
    factory = FactoryMiniSerializer()

    class Meta:
        model = IdCard
        fields = '__all__'


class IdCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdCard
        fields = '__all__'


class ProductMovementSerializer(serializers.ModelSerializer):
    zone_from = ZoneMovementSerializer()
    zone_to = ZoneMovementSerializer()
    card_om = IdCardSerializer()
    card_pm = IdCardSerializer()
    create_user = UserMiniSerializer()
    update_user = UserMiniSerializer()

    class Meta:
        model = ProductMovement
        fields = '__all__'


class ProductMovementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMovement
        exclude = (
            'created_at',
            'create_by',
            'updated_at',
            'update_by',
        )


class MovementLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementLog
        fields = '__all__'


class LogMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogMaterial
        fields = (
            'material',
            'materialquan',
        )


class TransferLogSerializer(serializers.ModelSerializer):
    log_materials = LogMaterialSerializer(many=True)

    class Meta:
        model = TransferLog
        fields = '__all__'


class IdCardFileSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(queryset=DocumentModel.objects.all(), required=True)

    class Meta:
        model = IdCardFile
        fields = '__all__'

    def validate(self, attrs):
        if os.path.splitext(attrs.get('file').file.name)[1].lower() not in ('.xls', '.xlsx'):
            raise ValidationError('file format is not correct')
        return super(IdCardFileSerializer, self).validate(attrs)


class ProductMovementFileSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(queryset=DocumentModel.objects.all(), required=True)

    class Meta:
        model = ProductMovementFile
        fields = '__all__'

    def validate(self, attrs):
        if os.path.splitext(attrs.get('file').file.name)[1].lower() not in ('.xls', '.xlsx'):
            raise ValidationError('file format is not correct')
        return super(ProductMovementFileSerializer, self).validate(attrs)
