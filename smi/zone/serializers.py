from rest_framework import serializers
from smi.zone.models import Zone, ZoneFile
from smi.factory.serializers import FactorySerializer
from smi.account.serializers import UserMiniSerializer


class ZoneSerializer(serializers.ModelSerializer):
    factory = FactorySerializer()
    create_by = UserMiniSerializer()
    update_by = UserMiniSerializer()

    class Meta:
        model = Zone
        fields = '__all__'


class ZoneCreateSerializer(serializers.ModelSerializer):
    zone_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Zone
        fields = '__all__'


class ZoneMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = (
            'id',
            'zone_id',
            'zonename',
        )


class ZoneMiddleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = (
            'id',
            'zone_id',
            'zonename',
            'ip_address',
            'p_number',
            'head_panel',
            'p_name'
        )


class ZoneMovementSerializer(serializers.ModelSerializer):
    factory = FactorySerializer()

    class Meta:
        model = Zone
        fields = (
            'id',
            'zone_id',
            'zonename',
            'ip_address',
            'p_number',
            'p_name',
            'head_panel',
            'factory'
        )


class ZoneFileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZoneFile
        fields = '__all__'
