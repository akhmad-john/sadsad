import logging
from django.db import transaction
from smi.core.utils.sap_parse_helper import sups_request, xml_to_list_of_dicts
from smi.product.models import Product
from smi.factory.models import Factory
from django.conf import settings
from smi.celery import app


sap_product_url = settings.SAP_API['PRODUCT']['URL']
sap_product_query = settings.SAP_API['PRODUCT']['QUERY']


@app.task
@transaction.atomic
def sync_product_table(sap_url=None):
    if sap_url is None:
        sap_url = sap_product_url
    queries = ''.join(['<item><Plant>{}</Plant></item>'.format(item)
                       for item in Factory.objects.values_list('plant_id', flat=True)])
    factories = {str(item.get('plant_id')): item.get('id') for item in Factory.objects.values('plant_id', 'id')}
    xml, _ = sups_request(sap_url, data=sap_product_query.format(queries))

    data = xml_to_list_of_dicts(xml)

    for product_kw in data:
        plant_id = product_kw.pop('plant')
        factory_id = factories.get(plant_id)
        if factory_id and plant_id:
            product_kw.update(factory_id=factory_id)
            try:
                factory = Factory.objects.get(id=product_kw['factory_id'])
                Product.objects.update_or_create(
                    factory=factory,
                    mat_id=product_kw['material'],
                    defaults={
                        'mat_name': product_kw['materialtxt'],
                        'unit': product_kw['materialuom'],
                        'pro_id': product_kw['producerind'],
                        'proid_name': product_kw['producertxt'],
                        'mat_type': product_kw['materialtype'],
                        'mat_type_name': product_kw['materialtypetxt'],
                        'oldmaterial': product_kw['oldmaterial']}
                )
            except Exception as e:
                logging.error(e)
    return True
