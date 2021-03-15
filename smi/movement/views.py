import django_filters
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from smi.core.utils.etc import export_to_excel, get_or_none
from smi.core.utils.file_parser import xlsx_response
from smi.movement import TransferLogStatus
from smi.movement.models import IdCard, ProductMovement, MovementLog, TransferLog, LogMaterial, IdCardFile, \
    ProductMovementFile
from smi.movement.serializers import (IdCardSerializer,
                                      IdCardCreateSerializer,
                                      IdCardMiniSerializer, IdCardFileSerializer, ProductMovementFileSerializer)
from smi.movement.filters import IdCardFilter
from smi.movement.tasks import get_sap_message, parse_card_from_file, parse_product_movement_from_file
from smi.movement.utils.sap import get_sap_product

from smi.factory.models import Factory
from smi.movement.utils.mes import mes_data_checker, ErrorMesMessages
from smi.movement.utils.parse_helper import is_correct_date_form
from smi.zone.models import Zone


class IdCardViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                    mixins.CreateModelMixin, GenericViewSet):
    serializer_class = IdCardSerializer
    queryset = IdCard.objects.all()
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    )
    search_fields = (
        'card_number',
        'name',
    )
    ordering_fields = (
        'id',
        'card_number',
        'name',
        'factory__plantname',
        'factory__plant_id'
    )
    filter_class = IdCardFilter
    model = IdCard

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            return IdCardCreateSerializer
        else:
            return IdCardSerializer

    @action(methods=['GET'], detail=False, url_path='mini-list')
    def mini_list(self, request):
        serializer = IdCardMiniSerializer(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def report(self, *args, **kwargs):
        qs = self.queryset.values(
            'factory__plant_id',
            'factory__plantname',
            'card_number',
            'name',
        )
        df_output = pd.DataFrame(qs)
        df_output.columns = (
            'Завод номер',
            'Наименование завода',
            '№ бейджика',
            'ФИО',
        )
        excel_file = export_to_excel(df_output)
        response = xlsx_response(excel_file.read(), filename='idcards {}'.format(datetime.today().strftime('%d/%m/%Y')))
        return response

    @action(methods=['GET'], detail=False, url_path='download-example')
    def example(self, *args, **kwargs):
        qs = self.queryset.values(
            'factory__plant_id',
            'card_number',
            'name',
        )
        df_output = pd.DataFrame(qs[:1])
        df_output.columns = (
            'Завод номер',
            '№ бейджика',
            'ФИО',
        )
        excel_file = export_to_excel(df_output)
        response = xlsx_response(excel_file.read(), filename='idcards {}'.format(datetime.today().strftime('%d/%m/%Y')))
        return response


class IdCardFileUploadViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = IdCardFileSerializer
    queryset = IdCardFile.objects.all()

    def perform_create(self, serializer):
        obj = serializer.save()
        parse_card_from_file.delay(obj.id)


class PrMovFileUploadViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ProductMovementFileSerializer
    queryset = ProductMovementFile.objects.all()

    def perform_create(self, serializer):
        obj = serializer.save()
        parse_product_movement_from_file(obj.id)


# mes use it
class MesPostView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, *args, **kwargs):
        if self.request.user.is_mes:
            data = self.request.data
            try:
                plant_id = int(float(data.get('PlantNo')))
            except ValueError:
                plant_id = data.get('PlantNo')
            p_number = data.get('WorkStationNo')
            movementlog = MovementLog.objects.create(factory=plant_id, zone=p_number)

            if isinstance(plant_id, int):
                if Factory.objects.filter(plant_id=int(plant_id)).exists():
                    if Zone.objects.filter(p_number=p_number).exists():
                        factory = Factory.objects.get(plant_id=int(plant_id))
                        if Zone.objects.filter(factory=factory, p_number=p_number).exists():
                            zone = Zone.objects.get(p_number=p_number)
                            zone_list = [
                                {"PlantNo": rel.zone_to.factory.plant_id, "WorkStationNo": rel.zone_to.p_number,
                                 "WorkStationName": rel.zone_to.zonename} for rel in
                                zone.zone_from_set.select_related("zone_to").all().order_by().distinct('zone_to')]
                            sap_data = get_sap_product(factory=factory, zone=zone, movementlog=movementlog)
                            data = {
                                'AvailableWorkStationList': zone_list,
                                'AvailableStockList': sap_data
                            }
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            smi_message = "WorkStationNo and PlantNo did not match in SMI! (Номер рабочий станции и завод номер не совпадают в SMI !)"
                            message = 'WorkStationNo and PlantNo did not match in SMI!'
                    else:
                        smi_message = "WorkStationNo is not defined in SMI! (Номер рабочий станции не определено в SMI !)"
                        message = 'WorkStationNo is not defined in SMI!'
                else:
                    smi_message = "PlantNo is not defined in SMI! (Виденный номер завода не существует в SMI !)"
                    message = 'PlantNo is not defined in SMI!'
            else:
                smi_message = "PlantNo is not integer! (Вид поля 'Номер завода' не integer)"
                message = 'PlantNo is not integer!'
            movementlog.status = "MesError"
            movementlog.message = smi_message
            movementlog.save()
            data = {
                "ErrorMessage": message,
                "RequestStatus": False
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "ErrorMessage": "Authentication failed",
                "RequestStatus": False
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)


class MesSapPostView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, *args, **kwargs):
        if not self.request.user.is_mes:
            return Response({"Error": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data
        posting_date = data.get("TransferDate")
        request_date = data.get('RequestedDate')
        sender_work_station = data.get("SenderWorkStation")
        receiver_work_station = data.get("ReceiverWorkStation")
        card_from = data.get('SenderConfirmID')
        card_to = data.get('ReceiverConfirmID')
        items = data.get('TransferStockList')
        try:
            factory_from = int(float(sender_work_station.get("PlantNo")))
        except ValueError:
            factory_from = sender_work_station.get("PlantNo")
        try:
            factory_to = int(float(receiver_work_station.get("PlantNo")))
        except ValueError:
            factory_to = receiver_work_station.get("PlantNo")
        zone_from = sender_work_station.get("WorkStationNo")
        zone_to = receiver_work_station.get("WorkStationNo")
        transfer_log = TransferLog.objects.create(
            factory_from=factory_from,
            factory_to=factory_to,
            zone_from=zone_from,
            zone_to=zone_to,
            postingdate=posting_date,
            requestdate=request_date,
            card_from=card_from,
            card_to=card_to
        )

        LogMaterial.objects.bulk_create(
            [
                LogMaterial(
                    transfer_log=transfer_log,
                    material=item.get('StockNo'),
                    materialquan=item.get("Quantity")) for item in items
            ]
        )

        mes_data_checker(
            is_correct_date_form(posting_date),
            err_msgs=ErrorMesMessages.INVALID_DATE,
            log_obj=transfer_log
        )

        mes_data_checker(
            isinstance(factory_from, int),
            err_msgs=ErrorMesMessages.INVALID_FACTORY_FROM,
            log_obj=transfer_log
        )

        mes_data_checker(
            isinstance(factory_to, int),
            err_msgs=ErrorMesMessages.INVALID_FACTORY_TO,
            log_obj=transfer_log
        )

        factory_from, _, _ = mes_data_checker(
            get_or_none(Factory, plant_id=factory_from),
            err_msgs=ErrorMesMessages.FACTORY_FROM,
            log_obj=transfer_log
        )
        zone_from_obj, _, _ = mes_data_checker(
            get_or_none(Zone, factory=factory_from, p_number=zone_from),
            err_msgs=ErrorMesMessages.ZONE_FROM,
            log_obj=transfer_log
        )
        factory_to, _, _ = mes_data_checker(
            get_or_none(Factory, plant_id=factory_to),
            err_msgs=ErrorMesMessages.FACTORY_TO,
            log_obj=transfer_log
        )
        zone_to_obj, _, _ = mes_data_checker(
            get_or_none(Zone, factory=factory_to, p_number=zone_to),
            err_msgs=ErrorMesMessages.ZONE_TO,
            log_obj=transfer_log
        )

        mes_data_checker(
            IdCard.objects.filter(card_number=card_from).exists(),
            err_msgs=ErrorMesMessages.CARD_FROM,
            log_obj=transfer_log
        )
        mes_data_checker(
            IdCard.objects.filter(card_number=card_to).exists(),
            err_msgs=ErrorMesMessages.CARD_TO,
            log_obj=transfer_log
        )

        mes_data_checker(
            ProductMovement.objects.filter(
                zone_from=zone_from_obj,
                zone_to=zone_to_obj,
            ).exists(),
            err_msgs=ErrorMesMessages.ZONE_PR_MOV,
            log_obj=transfer_log
        )
        mes_data_checker(
            ProductMovement.objects.filter(
                zone_from=zone_from_obj,
                zone_to=zone_to_obj,
                card_om__card_number=card_from,
            ).exists(),
            err_msgs=ErrorMesMessages.CARD_FROM_PR_MOV,
            log_obj=transfer_log
        )
        mes_data_checker(
            ProductMovement.objects.filter(
                zone_from=zone_from_obj,
                zone_to=zone_to_obj,
                card_om__card_number=card_from,
                card_pm__card_number=card_to
            ).exists(),
            err_msgs=ErrorMesMessages.CARD_TO_PR_MOV,
            log_obj=transfer_log
        )

        get_sap_message.delay(
            factory=factory_from.plant_id,
            zonefrom=zone_from_obj.zone_id,
            zoneto=zone_to_obj.zone_id,
            postingdate=posting_date,
            items=[(item.get('StockNo'), item.get('Quantity')) for item in items],
            transferlog=transfer_log.id
        )

        transfer_log.status = TransferLogStatus.CREATED
        transfer_log.save()
        data = {
            "ErrorMessage": "",
            "RequestStatus": True
        }
        return Response(data, status=status.HTTP_200_OK)
