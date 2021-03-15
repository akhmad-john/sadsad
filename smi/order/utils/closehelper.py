from decimal import Decimal

from smi.core.utils.etc import get_or_none
from smi.order import KonvOrderCloseStatus
from smi.order.models import KonvOrderClose, NeKonvOrderClose, Order, NeKonvOrderCloseReport
from smi.order.utils.sap import serial_nums_to_xml
from smi.zone import ZoneDirection
from smi.zone.models import Zone
from smi.order.tasks import close_konv_order, close_nekonv_order, send_order_close_tex


def konv_close(serial_nums=None, ipaddress=None, p_number=None, data=None):
    order_close = KonvOrderClose.objects.create(ipaddress=ipaddress, p_number=p_number, serialnum=serial_nums, data=data)
    zone = get_or_none(Zone, ip_address=ipaddress, p_number=p_number)
    if zone:
        if zone.direction == ZoneDirection.MS:
            # bs logic
            close_konv_order.delay(
                order_close_id=order_close.id,
                zone_id=zone.id,
            )
        if zone.direction == ZoneDirection.MT:
            # for logs
            send_order_close_tex.delay(
                url=zone.factory.tex_link,
                data=data,
                order_close_id=order_close.id
            )
        data = {
            "ErrorMessage": "",
            "RequestStatus": True
        }
        return data

    smi_message, mes_message = konv_err_msgs(p_number, ipaddress)
    order_close.status = KonvOrderCloseStatus.MES_ERROR
    order_close.message = smi_message
    order_close.save()
    data = {
        "ErrorMessage": mes_message,
        "RequestStatus": False
    }
    return data


def nekonv_close(aufnr=None, quantity=None, data=None):
    order_close = NeKonvOrderClose.objects.create(aufnr=aufnr, quantity=quantity, data=data)
    order = get_or_none(Order, aufnr=aufnr)
    if order and order.active and (isinstance(quantity, int) or isinstance(quantity, float)):
        quantity = Decimal(quantity)
        order.counter += quantity
        if order.counter >= order.psmng:
            order.psmng = order.counter
            order.active = False
        order.save()
        NeKonvOrderCloseReport.objects.create(
            order=order,
            quantity=quantity,
            zone=order.zone,
            product=order.product,
        )
        close_nekonv_order.delay(
            order_close_id=order_close.id,
            order_id=order.id,
        )
        data = {
            "ErrorMessage": "",
            "RequestStatus": True
        }
        return data

    smi_message, mes_message = nekonv_err_msgs(bool(order), order.active)
    order_close.status = KonvOrderCloseStatus.MES_ERROR
    order_close.message = smi_message
    order_close.save()
    data = {
        "ErrorMessage": mes_message,
        "RequestStatus": False
    }
    return data


def konv_err_msgs(p_number, ipaddress):
    if not Zone.objects.filter(p_number=p_number).exists():
        smi_message = "WorkStationNo is not defined in SMI! (Номер рабочей станции не определен в SMI !)"
        mes_message = "WorkStationNo is not defined in SMI!"
    elif not Zone.objects.filter(ip_address=ipaddress).exists():
        smi_message = "TransCode is not defined in SMI! (iP адрес не определен в SMI !)"
        mes_message = "TransCode is not defined in SMI!"
    else:
        smi_message = "TransCode and WorkStationNo did not match in SMI! (iP адрес и Номер рабочей станции не совпадают в SMI !)"
        mes_message = "TransCode and WorkStationNo did not match in SMI!"
    return smi_message, mes_message


def nekonv_err_msgs(order_exists, is_active):
    if not order_exists:
        smi_message = "WorkOrder is not defined in SMI! (Производственный заказ в SMI не указан!)"
        mes_message = "WorkOrder is not defined in SMI!"
    elif not is_active:
        smi_message = "WorkOrder closed in SMI! (Статус производственного заказа в SMI закрыто !)"
        mes_message = "WorkOrder closed in SMI!"
    else:
        smi_message = "Quantity is not integer or float type.SMI receive only integer or float type for Quantity. " \
                      "(Вид поля 'количество' не является integer или float SMI не может принять.) "
        mes_message = "Quantity is not integer or float type.SMI receive only integer or float type for Quantity."
    return smi_message, mes_message
