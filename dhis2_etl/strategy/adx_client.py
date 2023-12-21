import logging
from typing import Any, Dict
from urllib.parse import urljoin
from xml.etree import ElementTree

from dict2obj import Dict2Obj

import requests
from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.serializers.adx import XMLFormatter
from dhis2_etl.models.adx.data import ADXMapping
from dhis2_etl.models.dhis2.enum import MergeMode

logger = logging.getLogger('openIMIS')


class ADXClient:
    def __init__(self, **kwargs):
        dhis2 = Dict2Obj(GeneralConfiguration.get_dhis2())
        adx = Dict2Obj(GeneralConfiguration.get_adx())
        self.host =  dhis2.host
        self.username = dhis2.username
        self.password = dhis2.password
        self.endpoint = adx.endpoint
        self.content_type = adx.content_type
        self.data_element_id_scheme = adx.data_element_id_scheme
        self.org_unit_id_scheme = adx.org_unit_id_scheme

        self._url =self.host+ ('/' if  self.host[-1:] != '!' else '') +self.endpoint
        self._xml_formatter = XMLFormatter()

    def __enter__(self):
        self._current_session = requests.Session()
        self._current_session.auth = (self.username, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._current_session:
            self._current_session.close()

    def post_cube(self, cube: ADXMapping) -> None:
        cube_dom = self._xml_formatter.format_adx(cube)
        if cube_dom is not None:
            cube_xml = ElementTree.tostring(cube_dom)

            response = self._post(cube_xml)
            #response.raise_for_status()
            if response.status_code and response.status_code >= 200  and response.status_code < 300:
                logger.info(f"posted successfully")
            else:
                logger.error(f"error {response.status_code}\nurl:{response.url}\nmessage:{response.text}")


    @staticmethod
    def _get_config(key: str, config: Dict, **kwargs) -> Any:
        return kwargs.get(key) if kwargs and key in kwargs else config[key]

    def _get_post_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': self.content_type,
        }

    def _get_post_url_params(self) -> Dict[str, str]:
        return {
            'dataElementIdScheme': self.data_element_id_scheme,
            'orgUnitIdScheme': self.org_unit_id_scheme,
            'categoryOptionComboIdScheme':'uid'
        }

    def _post(self, payload: bytes,) -> requests.Response:
        params=self._get_post_url_params()
        logger.debug('POST to %s&%s:\n%s',self._url,params,payload)
        
        return self._current_session.post(
            self._url,
            data=payload,
            params=params,
            headers=self._get_post_headers()
        )

    def updateOrgUnitAndCatComboOption(self):
        url =self.host+ ('/' if  self.host[-1:] != '!' else '') + 'maintenance'
        return self._current_session.post(
            url,
            params={'categoryOptionComboUpdate':'true',
                        'ouPathsUpdate':'true'}
        )
