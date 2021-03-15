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


def sups_request(url, headers=None, data=None, auth=None, log=None):
    if headers is None:
        headers = default_headers
    if auth is None:
        auth = default_auth
    data = soap_data_template.format(data).encode('utf-8')
    try:
        r = requests.post(url, auth=requests.auth.HTTPBasicAuth(*auth), data=data, headers=headers, timeout=15)
        if r.status_code != 200:
            logging.warning(f'status {r.status_code} for {url}')
            if log:
                log.status = "SapError"
                log.message = f'status {r.status_code} for {url}, {data}'
                log.save()
            return None
        if log:
            log.status = "Success"
            log.save()
        return r.content
    except Exception as e:
        log.status = "SapError"
        log.message = f'TimeOut Error, {e}'
        log.save()
        return None

