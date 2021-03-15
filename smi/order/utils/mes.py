import json

from django.core.serializers.json import DjangoJSONEncoder


def mes_request_json_from_instance(order):
    stock_type = "900" if order.product.mat_type == "FERT" else "901"
    work_station_no = f"[{order.zone.head_panel}]" if order.zone.head_panel else f"{order.zone.p_number}"
    data = {
        "Duration": order.cycle,
        "MainStock": {
            "StockName": order.product.mat_name,
            "StockNo": order.product.mat_id,
            "UnitName": order.product.unit,
            "StockType": stock_type,
            "Status": True
        },
        "Quantity": str(order.psmng),
        "Status": order.active,
        "WorkOrderNo": order.aufnr,
        "StartDateStr": order.order_date,
        "WorkStationNo": work_station_no
    }
    data = json.dumps(data, cls=DjangoJSONEncoder)
    return data


