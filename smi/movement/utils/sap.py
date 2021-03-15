from smi.core.utils.sap_parse_helper import xml_to_list_of_dicts
from smi.movement.sap_parse_helper import sups_request
from smi.movement.tasks import sap_movement_url, sap_movement_query


def get_sap_product(sap_url=None, factory=None, zone=None, movementlog=None):
    if sap_url is None:
        sap_url = sap_movement_url

    queries = f'<Smiid>{movementlog.id}</Smiid><Plant>{factory.plant_id}</Plant><Warehouse>{zone.zone_id}</Warehouse><Pannum>{zone.p_number}</Pannum>'
    xml = sups_request(sap_url, data=sap_movement_query.format(queries), log=movementlog)
    data = xml_to_list_of_dicts(xml)
    for element in data:
        element['StockNo'] = element.pop('material')
        element['StockName'] = element.pop('materialtxt')
        element['Quantity'] = element.pop('materialquan')
        element['UnitName'] = element.pop('materialuom')
    return data
