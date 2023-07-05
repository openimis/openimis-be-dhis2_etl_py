import logging
from typing import Any, Dict
from urllib.parse import urljoin
from xml.etree import ElementTree

import requests

from dhis2_etl.adx_transform.adx_models.adx_data import ADXMapping
from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.models.dhis2Enum import MergeMode

logger = logging.getLogger(__name__)


class ADXClient:
    def __init__(self, **kwargs):
        self.host = self._get_dhis_config('host', **kwargs)
        self.username = self._get_dhis_config('username', **kwargs)
        self.password = self._get_dhis_config('password', **kwargs)
        self.endpoint = self._get_adx_config('endpoint', **kwargs)
        self.content_type = self._get_adx_config('content_type', **kwargs)
        self.data_element_id_scheme = self._get_adx_config('data_element_id_scheme', **kwargs)
        self.org_unit_id_scheme = self._get_adx_config('org_unit_id_scheme', **kwargs)

        self._url = urljoin(self.host, self.endpoint)
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
        cube_xml = ElementTree.tostring(cube_dom)

        response = self._post(cube_xml)
        response.raise_for_status()
        logger.info(f"{cube.name} adx cube posted successfully")

    def _get_dhis_config(self, key: str, **kwargs) -> Any:
        return self._get_config(key, config=GeneralConfiguration.get_dhis2(), **kwargs)

    def _get_adx_config(self, key: str, **kwargs) -> Any:
        return self._get_config(key, config=GeneralConfiguration.get_adx(), **kwargs)

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
            'mergeMode': MergeMode.merge
        }

    def _post(self, payload: bytes) -> requests.Response:
        return self._current_session.post(
            self._url,
            data=payload,
            params=self._get_post_url_params(),
            headers=self._get_post_headers()
        )
