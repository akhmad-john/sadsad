import pandas as pd

from smi.core.utils.etc import get_or_none
from smi.factory.models import Factory
from smi.movement.sap_parse_helper import sups_request
from django.conf import settings
from smi.movement.models import TransferLog, IdCardFile, IdCard, ProductMovement, ProductMovementFile
from smi.celery import app
from smi.movement.utils.parse_helper import check_pr_movement_file_row
from smi.zone.models import Zone

sap_movement_url = settings.SAP_API['MOVEMENT']['URL']
sap_movement_query = settings.SAP_API['MOVEMENT']['QUERY']

sap_productmovement_url = settings.SAP_API['PRODUCTMOVEMENT']['URL']
sap_productmovement_query = settings.SAP_API['PRODUCTMOVEMENT']['QUERY']


@app.task
def get_sap_message(sap_url=None, factory=None, zonefrom=None, zoneto=None, postingdate=None, items=None,
                    transferlog=None):
    transferlog = TransferLog.objects.get(id=transferlog)
    if sap_url is None:
        sap_url = sap_productmovement_url

    items = [f'<item><Material>{item[0]}</Material><Materialquan>{item[1]}</Materialquan></item>' for item in items]
    queries = f'<Smiid>{transferlog.id}</Smiid><Plant>{factory}</Plant><Warehouseout>{zonefrom}</Warehouseout><Warehousein>{zoneto}</Warehousein><Postingdate>{postingdate}</Postingdate><Item>{"".join(items)}</Item>'
    xml = sups_request(sap_url, data=sap_productmovement_query.format(queries), log=transferlog)


@app.task
def sync_reload_transfer():
    transfer_qs = TransferLog.objects.filter(status="SapError")
    for transfer in transfer_qs:
        zone_from = Zone.objects.get(p_number=transfer.zone_from)
        zone_to = Zone.objects.get(p_number=transfer.zone_to)
        items = [material for material in transfer.log_materials.values('material', 'materialquan')]
        get_sap_message.delay(factory=transfer.factory_from, zonefrom=zone_from.zone_id, zoneto=zone_to.zone_id,
                              postingdate=transfer.postingdate, items=items, transferlog=transfer.id)


@app.task
def parse_card_from_file(card_file_id):
    obj = IdCardFile.objects.get(id=card_file_id)
    df = pd.read_excel(obj.file.file)
    df.replace({pd.np.nan: None}, inplace=True)
    error_list = []
    for i, row in enumerate(df.values.tolist()):
        if row[1]:
            try:
                IdCard.objects.update_or_create(factory=Factory.objects.get(plant_id=row[0]), card_number=row[1],
                                                defaults={'name': row[2]})
            except Exception as e:
                error_list.append({i + 2: row, "Error": f'{e}'})
        else:
            error_list.append({i + 2: row, 'Error': "Id card is empty"})
    if error_list:
        IdCardFile.objects.filter(id=obj.id).update(errors=error_list)


@app.task
def parse_product_movement_from_file(movement_file_id):
    obj = ProductMovementFile.objects.get(id=movement_file_id)
    df = pd.read_excel(obj.file.file, dtype=str)
    df.replace({pd.np.nan: None}, inplace=True)
    error_list = []

    for i, row in enumerate(df.to_dict('records'), start=1):
        incorrect_cell = check_pr_movement_file_row(i, err_template='{} must not be empty!', **row)
        if incorrect_cell:
            error_list.append(incorrect_cell)
            continue
        from_plant_id, from_zone_id, from_p_number, from_ip_address, from_card_number, to_plant_id, to_zone_id, \
        to_p_number, to_ip_address, to_card_number = row.values()

        factory_from = get_or_none(Factory, plant_id=from_plant_id)
        card_om = get_or_none(IdCard, factory=factory_from, card_number=from_card_number)
        zone_from = get_or_none(Zone, factory=factory_from, zone_id=from_zone_id, p_number=from_p_number,
                                ip_address=from_ip_address)

        factory_to = get_or_none(Factory, plant_id=to_plant_id)
        card_pm = get_or_none(IdCard, factory=factory_to, card_number=to_card_number)
        zone_to = get_or_none(Zone, factory=factory_to, zone_id=to_zone_id, p_number=to_p_number,
                              ip_address=to_ip_address)

        data = {
            'factory_from': factory_from,
            'card_om ': card_om,
            'zone_from': zone_from,
            'factory_to': factory_to,
            'card_pm': card_pm,
            'zone_to': zone_to,
        }
        incorrect_cell = check_pr_movement_file_row(i, **data)
        if incorrect_cell:
            error_list.append(incorrect_cell)
            continue

        if zone_from and zone_to and card_om and card_pm:
            ProductMovement.objects.get_or_create(
                zone_from=zone_from,
                zone_to=zone_to,
                card_om=card_om,
                card_pm=card_pm
            )
    if error_list:
        ProductMovementFile.objects.filter(id=obj.id).update(errors=error_list)

