from rest_framework import serializers
from smi.order.models import Order, Log, KonvOrderClose, NeKonvOrderClose, NeKonvOrderCloseReport, OrderCheck
from smi.product.serializers import ProductMiddleSerializer
from smi.factory.serializers import FactoryMiniSerializer
from smi.zone.serializers import ZoneMiddleSerializer
from smi.account.serializers import UserMiniSerializer


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class OrderRetrieveSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True)
    create_by = UserMiniSerializer()
    update_by = UserMiniSerializer()
    product = ProductMiddleSerializer()
    factory = FactoryMiniSerializer()
    zone = ZoneMiddleSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    counter = serializers.ReadOnlyField()
    order_date = serializers.DateTimeField(input_formats=['%Y-%m-%d'])

    class Meta:
        model = Order
        exclude = (
            'aufnr',
            'created_at',
            'create_by',
            'updated_at',
            'update_by',
            'cycle',
            'cycleunit',
            'active',
        )


class OrderCheckSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()

    class Meta:
        model = OrderCheck
        exclude = (
            'created_at',
            'create_by',
            'updated_at',
            'update_by',
            'active',
            'message',
            'sap_message',
        )


class OrderListSerializer(serializers.ModelSerializer):
    create = serializers.SerializerMethodField('create_status')
    update = serializers.SerializerMethodField('update_status')
    result = serializers.SerializerMethodField('calculation_result')
    product = ProductMiddleSerializer()
    factory = FactoryMiniSerializer()
    zone = ZoneMiddleSerializer()

    class Meta:
        model = Order
        fields = '__all__'

    def calculation_result(self, obj):
        return obj.psmng - obj.counter

    def create_status(self, obj):
        if obj.status == "Error" or obj.status == "MesError":
            return True
        return False

    def update_status(self, obj):
        if obj.status == "EditError" or obj.status == "EditMesError":
            return True
        return False


class OrderMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'aufnr',
            'psmng',
        )


class CurrentReportSerializer(serializers.Serializer):
    total_plan = serializers.DecimalField(max_digits=13, decimal_places=3, coerce_to_string=False)
    total_done = serializers.DecimalField(max_digits=13, decimal_places=3, coerce_to_string=False)
    remine = serializers.DecimalField(max_digits=13, decimal_places=3, coerce_to_string=False)


class KonvOrderCloseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KonvOrderClose
        fields = '__all__'


class NeKonvOrderCloseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeKonvOrderClose
        fields = '__all__'


class NeKonvOrderCloseChildSerializer(serializers.ModelSerializer):
    order = OrderListSerializer()

    class Meta:
        model = NeKonvOrderCloseReport
        fields = (
            'id',
            'created_at',
            'order',
            'quantity',
        )


class NeKonvOrderCloseReportSerializer(serializers.ModelSerializer):
    total = serializers.FloatField()
    product__id = serializers.IntegerField()
    product__mat_id = serializers.CharField()
    product__mat_name = serializers.CharField()
    product__unit = serializers.CharField()

    class Meta:
        model = NeKonvOrderCloseReport
        fields = (
            'product__id',
            'product__mat_id',
            'product__mat_name',
            'product__unit',
            'total',
        )

