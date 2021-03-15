import django_filters
from datetime import timedelta
from django.db.models import Sum, F
import pandas as pd
from datetime import datetime
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from smi.core.utils.etc import export_to_excel
from smi.core.utils.file_parser import xlsx_response
from smi.order import OrderStatus
from smi.order.models import Order, Log, NeKonvOrderClose, KonvOrderClose, TrashOrderClose, NeKonvOrderCloseReport, \
    OrderCheck
from smi.order.serializers import (OrderCreateSerializer,
                                   OrderListSerializer,
                                   OrderMiniSerializer,
                                   OrderRetrieveSerializer,
                                   KonvOrderCloseSerializer,
                                   NeKonvOrderCloseSerializer,
                                   CurrentReportSerializer,
                                   OrderCheckSerializer)
from smi.order.filters import OrderFilter, KonvOrderCloseFilter, NeKonvOrderCloseFilter
from smi.order.tasks import create_sap_order, send_order_mes, sync_konv_error_close_by_admin, sap_check, \
    close_konv_order, close_nekonv_order
from smi.order.utils.closehelper import konv_close, nekonv_close
from smi.zone.models import Zone


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = (
        'aufnr',
        'id',
    )
    ordering_fields = (
        'id',
        'aufnr',
        'product__mat_id',
        'product__mat_name',
        'product__mat_type_name',
        'zone__zonename',
        'zone__ip_address',
        'zone__p_number',
        'created_at',
        'status',
        'active',
        'order_date'
    )
    filter_class = OrderFilter
    model = Order

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.request.user.orders_created.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderRetrieveSerializer
        elif self.action == 'mini_list':
            return OrderMiniSerializer
        else:
            return OrderListSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        create_sap_order(order)
        if order.status == OrderStatus.SUCCESS:
            send_order_mes(order=order)

    def perform_update(self, serializer):
        if not self.get_object().is_editable:
            return Response({"Error": "This order can not be changed"}, status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()
        Log.objects.create(order=order, name='Производственный заказ успешно был изменен в SMI')
        create_sap_order(order=order)
        if order.status == OrderStatus.SUCCESS or order.status == OrderStatus.SAP_ERROR:
            send_order_mes(order=order, err_status=OrderStatus.EDIT_MES_ERROR)

    @action(methods=['GET'], detail=False, url_path='mini-list')
    def mini_list(self, request):
        serializer = OrderMiniSerializer(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='reload-order')
    def reload_order(self, request, pk):
        order = self.get_object()
        if order.status not in OrderStatus.RELOAD_AVAILABLE_STATUSES:
            return Response({"Ошибка статус": "Статус этого заказа успешен {}".format(order.id)},
                            status=status.HTTP_400_BAD_REQUEST)

        order_status = order.status
        if order_status in (OrderStatus.ERROR, OrderStatus.EDIT_ERROR):
            create_sap_order(order)
            if order_status == OrderStatus.SUCCESS or order_status == OrderStatus.SAP_ERROR:
                send_order_mes(order, err_status=order_status)
        elif order_status in (OrderStatus.MES_ERROR, OrderStatus.EDIT_MES_ERROR):
            send_order_mes(order=order, err_status=order_status)

        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def report(self, *args, **kwargs):
        cols = Order.report_cols()
        qs = self.filter_queryset(self.get_queryset()).annotate(result=F('psmng') - F('counter')).values(*cols.keys())
        if not qs.exists():
            return Response({"Error": "There is no data to report"}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(qs)
        df.rename(columns=cols)
        excel_file = export_to_excel(df)
        response = xlsx_response(excel_file.read(),
                                 filename='Orders {}'.format(datetime.today().strftime('%d/%m/%Y')))
        return response


class OrderCheckViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = OrderCheckSerializer
    queryset = OrderCheck.objects.all()
    model = OrderCheck

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            ordercheck = OrderCheck.objects.get(id=serializer.data['id'])
            sap_result = sap_check(ordercheck=ordercheck)
            ordercheck = OrderCheck.objects.get(id=serializer.data['id'])
            if sap_result:
                data = {
                    "message": ordercheck.sap_message,
                    "status": True
                }
            else:
                if ordercheck.status == "Error":
                    data = {
                        "message": "пожалуйста повторите попытку проверку  калькуляций",
                        "status": False
                    }
                else:
                    data = {
                        "message": ordercheck.sap_message,
                        "status": False
                    }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.error, status=status.HTTP_404_NOT_FOUND)


class NeKonvOrederView(APIView):
    """
    This api use only for mes incoming messages.
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, *args, **kwargs):
        if not self.request.user.is_mes:
            return Response({"Error": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED)

        data = self.request.data
        if not data.get('ProducedStocks'):
            TrashOrderClose.objects.create(message="ProduceStocks is empty", data=data)
            return Response({"Error": "ProduceStocks is empty"}, status=status.HTTP_400_BAD_REQUEST)

        produced_stock = data.get('ProducedStocks')[0]
        aufnr = data.get('WorkOrderNo', None)
        serial_nums = produced_stock.get('SerialList', None)

        if serial_nums:
            # sap and tex
            ipaddress = data.get('TransCode', None)
            p_number = data.get('WorkStationNo', None)
            data = konv_close(serial_nums=serial_nums, ipaddress=ipaddress, p_number=p_number, data=data)

        elif aufnr:
            # only sap
            quantity = produced_stock.get('Quantity', None)
            data = nekonv_close(aufnr=aufnr, quantity=quantity, data=data)

        else:
            TrashOrderClose.objects.create(message="WorkOrderNo and SerialList are not defined in SMI!", data=data)
            data = {
                "ErrorMessage": "WorkOrderNo and SerialList are not defined in SMI!",
                "RequestStatus": False
            }

        return Response(data, status=status.HTTP_200_OK)


# front use it
class OrderReportViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = ('aufnr', 'id')
    ordering_fields = (
        'id', 'aufnr', 'product__mat_id', 'product__mat_name', 'product__mat_type_name', 'zone__zonename',
        'zone__ip_address', 'zone__p_number', 'created_at', 'status', 'active', 'order_date')
    filter_class = OrderFilter

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.queryset
        else:
            return None

    model = Order

    @action(methods=['GET'], detail=False, url_path='day-report')
    def day_report(self, request):
        qs = self.filter_queryset(self.get_queryset()).aggregate(total_plan=Sum('psmng'), total_done=Sum('counter'))
        if qs['total_plan'] is None:
            qs['total_plan'] = 0
        if qs['total_done'] is None:
            qs['total_done'] = 0
        qs['remine'] = qs['total_plan'] - qs['total_done']
        serializer = CurrentReportSerializer(qs, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='current-report')
    def current_report(self, request):
        qs = self.filter_queryset(self.get_queryset()).filter(order_date__date=datetime.today().date()).aggregate(
            total_plan=Sum('psmng'), total_done=Sum('counter'))
        if qs['total_plan'] is None:
            qs['total_plan'] = 0
        if qs['total_done'] is None:
            qs['total_done'] = 0
        qs['remine'] = qs['total_plan'] - qs['total_done']

        serializer = CurrentReportSerializer(qs, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='weekly-report')
    def weekly_report(self, request):
        reports = []
        for i in range(datetime.today().date().isoweekday() - 1, 0, -1):
            qs = self.filter_queryset(self.get_queryset()).filter(
                order_date__date=datetime.today().date() - timedelta(i)).aggregate(total_plan=Sum('psmng'),
                                                                                   total_done=Sum('counter'))
            if qs['total_plan'] is None:
                qs['total_plan'] = 0
            if qs['total_done'] is None:
                qs['total_done'] = 0
            qs['remine'] = qs['total_plan'] - qs['total_done']
            serializer = CurrentReportSerializer(qs, many=False)
            reports.append(serializer.data)
        return Response(reports, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def report(self, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        if qs.count() >= 1:
            df_output = pd.DataFrame(qs.annotate(result=F('psmng') - F('counter')).values('id',
                                                                                          'aufnr',
                                                                                          'status',
                                                                                          'active',
                                                                                          'created_at',
                                                                                          'order_date',
                                                                                          'product__mat_id',
                                                                                          'product__mat_name',
                                                                                          'cycle',
                                                                                          'cycleunit',
                                                                                          'product__mat_type_name',
                                                                                          'product__unit',
                                                                                          'zone__zonename',
                                                                                          'zone__p_number',
                                                                                          'zone__ip_address',
                                                                                          'psmng',
                                                                                          'counter',
                                                                                          'result'
                                                                                          ))
            df_output.columns = ['Номер заказа SMI',
                                 'Номер заказа SAP',
                                 'Журнал',
                                 'Статус',
                                 'Дата создания',
                                 'Дата заказа',
                                 'Код материала',
                                 'Наименование материала',
                                 'Время цикла',
                                 'Eдиница цикла',
                                 "Вид материала",
                                 'Ед.изм',
                                 'Участок',
                                 'Номер панели',
                                 'IP адрес',
                                 'План количество',
                                 'Факт количество',
                                 'Разница П/Ф']
            excel_file = export_to_excel(df_output)
            response = xlsx_response(excel_file.read(),
                                     filename='Orders {}'.format(datetime.today().strftime('%d/%m/%Y')))
            return response
        else:
            return Response({"Error": "There is no data to report"}, status=status.HTTP_404_NOT_FOUND)


# owner use it
class NeKonvOrderCloseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    serializer_class = NeKonvOrderCloseSerializer
    queryset = NeKonvOrderClose.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        OrderingFilter
    )
    ordering_fields = '__all__'
    filter_class = NeKonvOrderCloseFilter
    model = NeKonvOrderClose

    @action(methods=['GET'], detail=False, url_path='reload')
    def reload(self, request):
        nekonv_qs = NeKonvOrderClose.objects.filter(status="Error")
        for orderclose in nekonv_qs:
            if Order.objects.select_related().filter(aufnr=orderclose.aufnr).exists() and Order.objects.filter(
                    aufnr=orderclose.aufnr).count() == 1:
                order = Order.objects.get(aufnr=orderclose.aufnr)
                close_nekonv_order.delay(order_close_id=orderclose.id, order_id=order.id)
            else:
                orderclose.status = "SmiError"
                orderclose.message = "Order does not exist or has multiple orders with {} aufnr".format(
                    orderclose.aufnr)
                orderclose.save()
        return Response(status=status.HTTP_200_OK)


# owner use it
class KonvOrderCloseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = KonvOrderCloseSerializer
    queryset = KonvOrderClose.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        OrderingFilter
    )
    ordering_fields = '__all__'
    filter_class = KonvOrderCloseFilter
    model = KonvOrderClose

    @action(methods=['GET'], detail=True, url_path='reload-orderclose')
    def reload_order_close(self, request, pk):
        orderclose = self.get_object()
        if orderclose.status == "Error":
            if Zone.objects.filter(ip_address=orderclose.ipaddress, p_number=orderclose.p_number).exists():
                zone = Zone.objects.get(ip_address=orderclose.ipaddress, p_number=orderclose.p_number)
                close_konv_order.delay(order_close_id=orderclose.id, zone_id=zone.id)
            else:
                orderclose.status = "SmiError"
                orderclose.message = "Zone does not exist for this order close or has multiple zones with {} orderclose".format(
                    orderclose.id)
                orderclose.save()
            return Response({"Success": "Reloaded"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "This has already been already success"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='reload')
    def reload(self, request):
        sync_konv_error_close_by_admin.delay()
        return Response(status=status.HTTP_200_OK)

