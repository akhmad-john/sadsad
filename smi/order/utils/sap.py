import xmltodict

from smi.order import OrderStatus, KonvOrderCloseStatus


def sap_order_data(sap_response, is_create=True):
    data = dict(
        xmltodict.parse(sap_response)
        ['env:Envelope']
        ['env:Body']
        ['n0:ZppCreatePoViaSmiResponse' if is_create else 'n0:ZppChangePoViaSmiResponse']
        ['GsExportData']
    )
    return data


def status_from_sap_data(sap_data):
    sap_status = sap_data.get('Messagetype')
    status = OrderStatus.SMI_ERROR
    if sap_status == "S":
        status = OrderStatus.SUCCESS
    elif sap_status == "I":
        status = OrderStatus.SAP_ERROR
    return status


def sap_order_query_from_instance(order):
    """
    null aufnr order means new sap order
    """
    if not order.aufnr:
        query = f"""
            <Plant>{order.factory.plant_id}</Plant>
            <Porder/>
            <Smiid>{order.id}</Smiid>
            <Warehouse>{order.zone.zone_id}</Warehouse>
            <Material>{order.product.mat_id}</Material>
            <Orderquan>{order.psmng}</Orderquan>
            <Orderdate>{order.created_at.strftime('%Y-%m-%d')}</Orderdate>
        """
    else:
        query = f'<Smiid>{order.id}</Smiid>' \
                f'<Porder>{order.aufnr}</Porder>' \
                f'<Orderquan>{order.psmng}</Orderquan>'
    return query


def nekonv_order_close_query(plant_id, aufnr, quantity, order_close_id):
    query = f"""<Plant>{plant_id}</Plant>
           <Warehouse/>
           <Ipaddr/>
           <Indica/>
           <Porder>{aufnr}</Porder>
           <Orderquan>{quantity}</Orderquan>
           <Serialnums/>
           <Smiid>{order_close_id}</Smiid>"""
    return query


def konv_order_close_query(plant_id, zone_id, ip_address, p_number, serial_nums, order_close_id):
    query = f"""<Plant>{plant_id}</Plant>
                <Warehouse>{zone_id}</Warehouse>
                <Ipaddr>{ip_address}</Ipaddr>
                <Indica>{p_number}</Indica>
                <Porder/>
                <Orderquan/>
                <Serialnums>{serial_nums}</Serialnums>
                <Smiid>{order_close_id}</Smiid>"""
    return query


def serial_nums_to_xml(serial_nums):
    if isinstance(serial_nums, str):
        serial_list = ['<item>{}</item>'.format(serial.replace("'", '')) for serial in
                       serial_nums.strip('][').split(', ')]
    else:
        serial_list = ['<item>{}</item>'.format(serial) for serial in serial_nums]
    return ''.join(serial_list)


def order_close_err_msgs(*args, empty_response=True, errors=None):
    if empty_response:
        status = KonvOrderCloseStatus.ERROR
        message = f"SAP не отправил производственный заказ в SMI " + ", ".join(*args)
    else:
        status = KonvOrderCloseStatus.SMI_ERROR
        message = f"SAP отправил производственный заказы которые не существует в SMI; Список заказов: " \
                  f"{', '.join(errors)}"
    return status, message
