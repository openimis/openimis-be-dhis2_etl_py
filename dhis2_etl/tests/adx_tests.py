import datetime
from dataclasses import asdict
from typing import List
from xml.etree import ElementTree

from django.test import TestCase
from location.models import HealthFacility, Location

from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.adx_transform.builders import ADXBuilder
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingDataValueDefinition, \
    ADXMappingCategoryDefinition, ADXCategoryOptionDefinition, ADXMappingCubeDefinition, ADXMappingGroupDefinition
from dhis2_etl.utils import build_dhis2_id
from insuree.models import Insuree

from insuree.models import Gender
from insuree.test_helpers import create_test_insuree
from location.test_helpers import create_test_health_facility
from dhis2_etl.adx_transform.adx_models.adx_time_period import ISOFormatPeriodType, PeriodParsingException


class ADXTestCase(TestCase):
    _50_YEARS_AGO = datetime.datetime(2022, 7, 1)-datetime.timedelta(days=365*50)
    AGE_CATEGORY_DEFINITION = ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=[
            ADXCategoryOptionDefinition(
                code="<=50yo",
                filter=lambda insuree_qs: insuree_qs.filter(dob__gte=ADXTestCase._50_YEARS_AGO)),
            ADXCategoryOptionDefinition(
                code=">50yo",
                filter=lambda insuree_qs: insuree_qs.filter(dob__lt=ADXTestCase._50_YEARS_AGO))
        ]
    )
    SEX_CATEGORY_DEFINITION = ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", filter=lambda insuree_qs: insuree_qs.filter(gender__code='M')),
            ADXCategoryOptionDefinition(
                code="F", filter=lambda insuree_qs: insuree_qs.filter(gender__code='F'))
        ]
    )

    TEST_ADX_DEFINITION = ADXMappingCubeDefinition(
        name='TEST_HF_ADX_DEFINITION',
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                dataset=HealthFacility,
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        related_from_dataset_func=lambda hf: hf.insurees,
                        aggregation_function=lambda insuress_qs: str(insuress_qs.count()),
                        categories=[AGE_CATEGORY_DEFINITION, SEX_CATEGORY_DEFINITION]
                    )
                ]
            )
        ]
    )

    TEST_ADX_DEFINITION_NO_CAT = ADXMappingCubeDefinition(
        name='TEST_HF_ADX_DEFINITION',
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                dataset=HealthFacility,
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        related_from_dataset_func=lambda hf: hf.insurees,
                        aggregation_function=lambda insuress_qs: str(insuress_qs.count()),
                        categories=[]
                    )
                ]
            )
        ]
    )

    VALID_TEST_PERIOD = "2019-01-01/P2Y"
    INVALID_TEST_PERIOD_1 = "2019-01-01/A2X"
    INVALID_TEST_PERIOD_2 = "2019-01-01P2Y"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_test_organization_unit()

    def test_adx_mapping(self):
        adx_format = self._create_test_adx()
        self.assertEqual(asdict(adx_format), self.EXPECTED_ADX_DICT)

    def test_adx_mapping_no_category(self):
        adx_format = self._create_test_adx(test_definition=self.TEST_ADX_DEFINITION_NO_CAT)
        self.assertEqual(asdict(adx_format), self.EXPECTED_ADX_DICT_NO_CATEGORY)

    def test_adx_mapping_invalid_period_1(self):
        with self.assertRaises(PeriodParsingException):
            self._create_test_adx(self.INVALID_TEST_PERIOD_1)

    def test_adx_mapping_invalid_period_2(self):
        with self.assertRaises(PeriodParsingException):
            self._create_test_adx(self.INVALID_TEST_PERIOD_2)

    def test_xml_format(self):
        adx_format = self._create_test_adx()
        xml_formatter = XMLFormatter()
        xml_format = xml_formatter.format_adx(adx_format)
        expected = ElementTree.fromstring(self.EXPECTED_XML_DUMP)
        self.assertEqual(ElementTree.tostring(expected), ElementTree.tostring(xml_format))

    def _create_test_adx(self, test_period=VALID_TEST_PERIOD, test_definition=TEST_ADX_DEFINITION):
        builder = ADXBuilder(test_definition)
        org_units = [self._TEST_HF.uuid]
        return builder.create_adx_cube(test_period, org_units)

    @classmethod
    def _create_test_organization_unit(cls):
        # First valid district
        district = Location.objects.filter(type='D', validity_to__isnull=True).first()
        cls._TEST_HF = create_test_health_facility('HFT', district.id)
        cls._TEST_INSUREES = [
            cls._create_test_insuree('chft1', 'M', '1950-01-01', '2018-12-01'),
            cls._create_test_insuree('chft2', 'M', '2000-01-01', '2020-01-01'),
            cls._create_test_insuree('chft3', 'F', '2000-01-01', '2020-02-01'),
            cls._create_test_insuree('chft4', 'F', '2000-01-01', '2020-02-01'),
            cls._create_test_insuree('chft5', 'F', '1950-01-01', '2022-01-01'),
        ]

        org_unit = build_dhis2_id(cls._TEST_HF.uuid)
        cls.EXPECTED_ADX_DICT = {
            'name': 'TEST_HF_ADX_DEFINITION',
            'groups': [{
                'org_unit': org_unit,
                'period': '2019-01-01/P2Y',
                'data_set': "HEALTHFACILITY",
                'comment': 'Test Comment',
                'data_values': [{
                    'data_element': 'NB_INSUREES',
                    'value': '1',
                    'aggregations': [{
                        'label_name': 'ageGroup',
                        'label_value': '<=50yo'
                    }, {
                        'label_name': 'sex',
                        'label_value': 'M'
                    }]
                }, {
                    'data_element': 'NB_INSUREES',
                    'value': '2',
                    'aggregations': [{
                        'label_name': 'ageGroup',
                        'label_value': '<=50yo'
                    }, {
                        'label_name': 'sex',
                        'label_value': 'F'
                    }]
                }, {
                    'data_element': 'NB_INSUREES',
                    'value': '0',
                    'aggregations': [{
                        'label_name': 'ageGroup',
                        'label_value': '>50yo'
                    }, {
                        'label_name': 'sex',
                        'label_value': 'M'
                    }]
                }, {
                    'data_element': 'NB_INSUREES',
                    'value': '0',
                    'aggregations': [{
                        'label_name': 'ageGroup',
                        'label_value': '>50yo'
                    }, {
                        'label_name': 'sex',
                        'label_value': 'F'
                    }]
                }]
            }]}

        cls.EXPECTED_ADX_DICT_NO_CATEGORY = {
            'name': 'TEST_HF_ADX_DEFINITION',
            'groups': [{
                'org_unit': org_unit,
                'period': '2019-01-01/P2Y',
                'data_set': "HEALTHFACILITY",
                'comment': 'Test Comment',
                'data_values': [{
                    'data_element': 'NB_INSUREES',
                    'value': '3',
                    'aggregations': []
                }]
            }]
        }
        cls.EXPECTED_XML_DUMP = F'''<adx><group org_unit="{org_unit}" period="2019-01-01/P2Y" data_set="HEALTHFACILITY" comment="Test Comment"><dataValue data_element="NB_INSUREES" value="1" ageGroup="&lt;=50yo" sex="M" /><dataValue data_element="NB_INSUREES" value="2" ageGroup="&lt;=50yo" sex="F" /><dataValue data_element="NB_INSUREES" value="0" ageGroup="&gt;50yo" sex="M" /><dataValue data_element="NB_INSUREES" value="0" ageGroup="&gt;50yo" sex="F" /></group></adx>'''

    @classmethod
    def _create_test_insuree(cls, chfid: str, sex: str, dob: str, validity: str) -> List[Insuree]:
        return create_test_insuree(
            True,
            {'chf_id': chfid,
             'gender': Gender.objects.get(code=sex),
             'dob': dob,
             'health_facility': cls._TEST_HF,
             'validity_from': validity}
        )
