import logging

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree

from smi import settings


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


def sups_request(url, headers=None, data=None, auth=None):
    if headers is None:
        headers = default_headers
    if auth is None:
        auth = default_auth
    data = soap_data_template.format(data).encode('utf-8')
    try:
        r = requests.post(url, auth=requests.auth.HTTPBasicAuth(*auth), data=data, headers=headers, timeout=30)
    except Exception as e:
        return None, None
    if r.status_code != 200:
        logging.warning(f'status {r.status_code} for {url}')
        return None, r.status_code
    return r.content, r.status_code


def xml_to_list_of_dicts(xml_text, elem_name='item'):
    tree = ElementTree.fromstring(xml_text)
    items = []
    for item in tree.iter(elem_name):
        single = dict()
        for child in item:
            single.update({child.tag.lower(): child.text.strip() if child.text else child.text})
        items.append(single)

    return items


def xml_to_list_of_dict_with_child(xml, keys_to_body=None):
    if keys_to_body is None:
        items = xmltodict.parse(xml)['env:Envelope']['env:Body']
        items = items[list(items.keys())[0]]['ExData']
        if items:
            items = items['item']
            if type(items) is not list:
                items = [items]
        else:
            return None
    else:
        items = xmltodict.parse(xml)
        for key in keys_to_body:
            items = items[key]
    return items
