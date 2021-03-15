import json
import time

import requests

from django.contrib.auth import get_user_model
from celery import shared_task
from decimal import Decimal
from time import sleep

from django.core.serializers.json import DjangoJSONEncoder

from smi.core.utils.sap_parse_helper import xml_to_list_of_dicts, sups_request
from smi.order import OrderStatus, KonvOrderCloseStatus, NoKonvOrderCloseStatus
from smi.order.sap_parse_helper import sups_request_order_check
from smi.order.utils.mes import mes_request_json_from_instance
from smi.order.utils.sap import sap_order_data, status_from_sap_data, sap_order_query_from_instance, \
    nekonv_order_close_query, konv_order_close_query, order_close_err_msgs, serial_nums_to_xml
from smi.zone.models import Zone
from smi.order.models import Order, KonvOrderClose, NeKonvOrderClose
from django.conf import settings
from smi.celery import app

User = get_user_model()

sap_order_url = settings.SAP_API['ORDER']['URL']
sap_order_query = settings.SAP_API['ORDER']['QUERY']

sap_orderchange_url = settings.SAP_API['ORDERCHANGE']['URL']
sap_orderchange_query = settings.SAP_API['ORDERCHANGE']['QUERY']

sap_orderclose_url = settings.SAP_API['ORDERCLOSE']['URL']
sap_orderclose_query = settings.SAP_API['ORDERCLOSE']['QUERY']

sap_ordercheck_url = settings.SAP_API['ORDERCHECK']['URL']
sap_ordercheck_query = settings.SAP_API['ORDERCHECK']['QUERY']


def create_sap_order(order, sap_url=None):
    if sap_url is None:
        sap_url = sap_order_url
    is_create = not bool(order.aufnr)

    sap_query = sap_order_query_from_instance(order)
    if is_create:
        sap_response, r_status = sups_request(sap_url, data=sap_order_query.format(sap_query))
    else:
        sap_response, r_status = sups_request(sap_url, data=sap_orderchange_query.format(sap_query))

    if r_status != 200:
        order.status = OrderStatus.ERROR if is_create else OrderStatus.EDIT_ERROR
        order.log_message = {"Status": r_status}
        order.save()
        return

    sap_data = sap_order_data(sap_response, is_create=is_create)
    order.status = status_from_sap_data(sap_data)
    order.log_message = {
        "Status": r_status,
        **sap_data,
    }
    order.save()

    smiid = int(sap_data.get('Smiid')) if sap_data else None
    if not smiid or smiid != order.id:
        order.status = OrderStatus.ERROR
        order.log_message = {
            "Messagetext": f"SMI iD неправильно (SAP не ответил с тем же {order.id})"
        }
        order.save()
    elif is_create:
        order.aufnr = sap_data['Porder']
        order.cycle = sap_data['Cycletime']
        order.cycleunit = sap_data['Cycletimeunit']
        order.active = True
        order.status_is_change = False
        order.save()


def send_order_mes(order, err_status=None):
    if err_status is None:
        err_status = OrderStatus.MES_ERROR
    url = order.factory.factory_link
    data = mes_request_json_from_instance(order)

    try:
        r = requests.post(url, data=data, headers={'Content-Type': 'application/json'}, timeout=2)
    except requests.exceptions.RequestException as e:
        order.status = err_status
        data = {
            "Ошибка статуса": "Ошибка истечения времени ожидания MES",
            "Message": f'{e}'
        }
        order.log_message = data
        order.save()
        return

    if r.status_code != 200:
        order.status = err_status
        data = {
            "Status": r.status_code
        }
    else:
        response_data = r.json()
        order.status = OrderStatus.MES_SUCCESS if response_data.get("RequestStatus") else OrderStatus.SMI_ERROR
        data = {
            "Status": r.status_code,
            **response_data
        }

    order.log_message = data
    order.save()


@app.task
def close_nekonv_order(order_close_id, order_id, sap_url=None):
    if sap_url is None:
        sap_url = sap_orderclose_url
    order_close = NeKonvOrderClose.objects.get(id=order_close_id)
    order = Order.objects.get(id=order_id)

    query = nekonv_order_close_query(order.factory.plant_id, order.aufnr, order_close.quantity, order_close_id)
    sap_response, r_status = sups_request(sap_url, data=sap_orderclose_query.format(query))
    data = xml_to_list_of_dicts(sap_response)

    error_items = [i for i in data if not Order.objects.filter(aufnr=i.get("porder")).exists()]
    if not error_items and data:
        order_close.status = NoKonvOrderCloseStatus.SUCCESS
    else:
        order_close.status, order_close.message = order_close_err_msgs(
            sap_url,
            query,
            sap_response,
            empty_response=not bool(data),
            errors=error_items
        )
    order_close.save()


@app.task
def close_konv_order(order_close_id, zone_id, sap_url=None):
    if sap_url is None:
        sap_url = sap_orderclose_url

    order_close = KonvOrderClose.objects.get(id=order_close_id)
    zone = Zone.objects.get(id=zone_id)

    query = konv_order_close_query(
        zone.factory.plant_id,
        zone.zone_id,
        zone.ip_address,
        zone.p_number,
        serial_nums_to_xml(order_close.serialnum),
        order_close.id
    )
    sap_response, r_status = sups_request(sap_url, data=sap_orderclose_query.format(query))
    data = xml_to_list_of_dicts(sap_response)
    error_items = [
        data.pop(i) for i, item in enumerate(data) if
        not Order.objects.filter(aufnr=item.get("porder")).exists() or
        not Order.objects.get(aufnr=item.get("porder")).active
    ]
    for item in data:
        order = Order.objects.get(aufnr=item.get("porder"))
        quantity = Decimal(item.get("confquan"))
        order.counter += quantity
        if order.counter >= order.psmng:
            order.psmng = order.counter
            order.active = False
        order.save()
    if not error_items:
        order_close.status = KonvOrderCloseStatus.SUCCESS
    else:
        order_close.status, order_close.message = order_close_err_msgs(
            sap_url,
            query,
            sap_response,
            empty_response=not bool(data),
            errors=error_items
        )
    order_close.save()


@shared_task
def sync_konv_error_close_by_admin():
    konv_qs = KonvOrderClose.objects.filter(status="Error")
    for orderclose in konv_qs:
        if Zone.objects.filter(ip_address=orderclose.ipaddress, p_number=orderclose.p_number).exists():
            zone = Zone.objects.get(ip_address=orderclose.ipaddress, p_number=orderclose.p_number)
            close_konv_order.delay(
                order_close_id=orderclose.id,
                zone_id=zone.id,
            )
        else:
            orderclose.status = "SmiError"
            orderclose.message = "Zone does not exist for this order close or has multiple zones with {} orderclose".format(
                orderclose.id)
            orderclose.save()
        sleep(1.5)
    konv_qs_tex = KonvOrderClose.objects.filter(status="TexError")
    for orderclose in konv_qs_tex:
        if Zone.objects.filter(ip_address=orderclose.ipaddress, p_number=orderclose.p_number).exists():
            zone = Zone.objects.get(ip_address=orderclose.ipaddress, p_number=orderclose.p_number)
            send_order_close_tex.delay(url=zone.factory.tex_link, data=orderclose.data, order_close_id=orderclose.id)
        else:
            orderclose.status = "SmiError"
            orderclose.message = "Zone does not exist for this order close or has multiple zones with {} orderclose".format(
                orderclose.id)
            orderclose.save()


# TODO: next tasks without refactoring


@app.task
def sap_check(ordercheck, sap_url=None):
    if sap_url is None:
        sap_url = sap_ordercheck_url
    query = """<Plant>{0}</Plant>
            <Smiid>{1}</Smiid>
            <Material>{2}</Material>""".format(ordercheck.factory.plant_id,
                                               ordercheck.id,
                                               ordercheck.product.mat_id, )

    response = sups_request_order_check(sap_url, ordercheck=ordercheck, data=sap_ordercheck_query.format(query))
    if response:
        if response['Messagetext']:
            ordercheck.sap_message = response['Messagetext']
        else:
            ordercheck.sap_message = "Проверка калькуляций был успешно завершен!"
        ordercheck.status = 'Success'
        if response['Messagetype'] == 'S':
            ordercheck.active = True
            ordercheck.save()
            return True
        else:
            ordercheck.active = False
            ordercheck.save()
            return False
    return False


@app.task
def sync_nekonv_error_close():
    for order_close in NeKonvOrderClose.objects.filter(status=NoKonvOrderCloseStatus.ERROR):
        if Order.objects.filter(aufnr=order_close.aufnr).exists() \
                and Order.objects.filter(aufnr=order_close.aufnr).count() == 1:
            order = Order.objects.get(aufnr=order_close.aufnr)
            close_nekonv_order.delay(order_close_id=order_close.id, order_id=order.id)
        else:
            order_close.status = "SmiError"
            order_close.message = "Order does not exist or has multiple orders with {} aufnr".format(order_close.aufnr)
            order_close.save()


@app.task
def sync_konv_error_close():
    for order_close in KonvOrderClose.objects.filter(status=KonvOrderCloseStatus.ERROR):
        if Zone.objects.filter(ip_address=order_close.ipaddress, p_number=order_close.p_number).exists():
            zone = Zone.objects.get(ip_address=order_close.ipaddress, p_number=order_close.p_number)
            close_konv_order.delay(order_close_id=order_close.id, zone_id=zone.id)
        else:
            order_close.status = KonvOrderCloseStatus.SMI_ERROR
            order_close.message = "Zone does not exist for this order close or has multiple zones with {} orderclose" \
                .format(order_close.id)
            order_close.save()

    for order_close in KonvOrderClose.objects.filter(status=KonvOrderCloseStatus.TEX_ERROR):
        if Zone.objects.filter(ip_address=order_close.ipaddress, p_number=order_close.p_number).exists():
            zone = Zone.objects.get(ip_address=order_close.ipaddress, p_number=order_close.p_number)
            send_order_close_tex.delay(url=zone.factory.tex_link, data=order_close.data, order_close_id=order_close.id)
        else:
            order_close.status = KonvOrderCloseStatus.SMI_ERROR
            order_close.message = "Zone does not exist for this order close or has multiple zones with {} orderclose" \
                .format(order_close.id)
            order_close.save()


@app.task
def send_order_close_tex(url=None, data=None, order_close_id=None):
    headers = {
        'Content-Type': 'application/json'
    }
    order_close = KonvOrderClose.objects.get(id=order_close_id)
    data = json.dumps(data, cls=DjangoJSONEncoder)
    try:
        r = requests.post(url, data=data, headers=headers, timeout=15)
    except Exception as e:
        order_close.status = 'TexError'
        order_close.message = f'TimeOut Error, {e}'
        order_close.save()
        return
    if r.status_code != 200:
        order_close.status = "TexError"
        order_close.message = f'{r.content}, status {r.status_code} for {url}'
    else:
        order_close.status = 'Success'
        order_close.message = f"Tex Success keldi, {r.content}"
    order_close.save()


