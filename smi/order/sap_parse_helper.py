import logging
import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from django.contrib.auth import get_user_model
from smi import settings
from smi.core.utils.sap_parse_helper import sups_request
from smi.order import OrderStatus

from smi.order.models import Log

User = get_user_model()

default_headers = {
    'Content-Type': 'application/soap+xml; charset=utf-8',
    'Authorization': settings.SAP_API['AUTH_TOKEN'],
}

default_auth = (settings.SAP_API['LOGIN'], settings.SAP_API['PASSWORD'])

soap_data_template = """
    <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
        <soapenv:Header/>
        <soapenv:Body>
            {}
        </soapenv:Body>
    </soapenv:Envelope> 
"""


def sups_request_order_check(url, headers=None, data=None, auth=None, ordercheck=None):
    if headers is None:
        headers = default_headers
    if auth is None:
        auth = default_auth
    data = soap_data_template.format(data).encode('utf-8')
    try:
        r = requests.post(url, auth=requests.auth.HTTPBasicAuth(*auth), data=data, headers=headers, timeout=30)
        if r.status_code != 200:
            logging.warning(f'status {r.status_code} for {url}')
            ordercheck.status = "Error"
            ordercheck.message = f' status {r.status_code} for {url}'
            ordercheck.save()
            return None
        return dict(xmltodict.parse(r.content)['env:Envelope']['env:Body']['n0:ZsmiCheckMaterialCostEstimResponse'][
                        'GsExportData'])
    except Exception as e:
        ordercheck.status = "Error"
        ordercheck.message = f'TimeOut Error {e}'
        ordercheck.save()
        return None


def xml_to_dic(xml_text):
    items = xmltodict.parse(xml_text)['env:Envelope']['env:Body']['n0:ZppConfurmPoViaSmiResponse']['GsExportData']

    items = dict(items)

    return items

