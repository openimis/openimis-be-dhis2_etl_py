from unittest.mock import MagicMock, patch

from django.test import TestCase

from dhis2_etl.adx_client import ADXClient
from dhis2_etl.adx_transform.adx_models.adx_data import ADXMapping


class ADXClientTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.adx_client = ADXClient()

    def test_adx_client_config(self):
        self.assertTrue(all((self.adx_client.host,
                             self.adx_client.password,
                             self.adx_client.username,
                             self.adx_client.endpoint,
                             self.adx_client.org_unit_id_scheme,
                             self.adx_client.data_element_id_scheme,
                             self.adx_client.content_type)))

    @patch('dhis2_etl.adx_client.ADXClient._post')
    def test_adx_client_post_cube(self, mock_post_method):
        mock_response = MagicMock()
        mock_post_method.return_value = mock_response

        cube = ADXMapping(name='Test', groups=[])
        self.adx_client.post_cube(cube)

        mock_post_method.assert_called_once_with(b'<adx />')
        mock_response.raise_for_status.assert_called_once()
