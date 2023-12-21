import datetime
from dataclasses import asdict
from typing import List
from xml.etree import ElementTree

from dhis2_etl.builders.adx import ADXBuilder
from dhis2_etl.serializers.adx import XMLFormatter, remove_namespace
from dhis2_etl.models.adx.definition import (ADXCategoryOptionDefinition,
                                             ADXMappingCategoryDefinition,
                                             ADXMappingCubeDefinition,
                                             ADXMappingDataValueDefinition,
                                             ADXMappingGroupDefinition)
from dhis2_etl.models.adx.time_period import (ISOFormatPeriodType,
                                              PeriodParsingException)
from dhis2_etl.utils import build_dhis2_id
from django.test import TestCase
from django.db.models import Q, Count
from insuree.models import Gender, Insuree
from insuree.test_helpers import create_test_insuree
from location.models import HealthFacility, Location
from location.test_helpers import create_test_health_facility


class ADXTests(TestCase):
    _50_YEARS_AGO = datetime.datetime(2022, 7, 1) - datetime.timedelta(days=365 * 50)
    AGE_CATEGORY_DEFINITION = ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=[
            ADXCategoryOptionDefinition(
                code="<=50yo",
                name="<=50yo",
                filter= Q(dob__gte=_50_YEARS_AGO)),
            ADXCategoryOptionDefinition(
                code=">50yo",name=">50yo",
                filter=Q(dob__lt=_50_YEARS_AGO))
        ]
    )
    SEX_CATEGORY_DEFINITION = ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M",name="M", filter=Q(gender__code='M')),
            ADXCategoryOptionDefinition(
                code="F",name="F", filter=Q(gender__code='F')),
            ADXCategoryOptionDefinition(
                code="O",name="O", is_default = True)
        ]
    )

    TEST_ADX_DEFINITION = ADXMappingCubeDefinition(
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                data_set='TEST_HF_ADX_DEFINITION',
                org_unit_type=HealthFacility,
                to_org_unit_code_func=lambda hf: build_dhis2_id(hf.uuid),
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        dataset_from_orgunit_func=lambda hf: hf.insurees,
                        aggregation_func=Count('id'),
                        period_filter_func=lambda qs, period: qs.filter(validity_from__gte=period.from_date,
                                                                        validity_from__lte=period.to_date),
                        categories=[AGE_CATEGORY_DEFINITION, SEX_CATEGORY_DEFINITION]
                    )
                ]
            )
        ]
    )

    TEST_ADX_DEFINITION_NO_CAT = ADXMappingCubeDefinition(
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                data_set='TEST_HF_ADX_DEFINITION',
                org_unit_type=HealthFacility,
                to_org_unit_code_func=lambda hf: build_dhis2_id(hf.uuid),
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        dataset_from_orgunit_func=lambda hf: hf.insurees,
                        aggregation_func=Count('id'),
                        period_filter_func=lambda qs, period: qs.filter(validity_from__gte=period.from_date,
                                                                        validity_from__lte=period.to_date),
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

    def is_same_aggregation(self, dv_g, dv_e):
        is_same = True
        # true if not cat
        if not 'aggregations' in dv_g:
            if not 'aggregations' in dv_e:
                return True
            else:
                return False
        
        for ag_g in dv_g['aggregations']:
            found = False
            #if no agg on expected not the same as generated
            if not 'aggregations' in dv_e:
                return False
            for ag_e in dv_e['aggregations']:
                if str(ag_g) == str(ag_e):
                    found = True
            if not found:
                return False
        return True


    def _test_datavalue(self,adx_generated, adx_expected):
        for dv_g in adx_generated['groups'][0]['data_values'] :
            for dv_e in adx_expected['groups'][0]['data_values']:
                if self.is_same_aggregation(dv_g, dv_e):
                    self.assertEqual(dv_g,dv_e )

    def test_adx_mapping(self):
        adx_format = self._create_test_adx()
        #self.assertEqual(asdict(adx_format)['name'], self.EXPECTED_ADX_DICT['name'])
        self._test_datavalue( asdict(adx_format), self.EXPECTED_ADX_DICT)
        

    def test_adx_mapping_no_category(self):
        adx_format = self._create_test_adx(test_definition=self.TEST_ADX_DEFINITION_NO_CAT)
        #self.assertEqual(asdict(adx_format)['name'], self.EXPECTED_ADX_DICT_NO_CATEGORY['name'])
        self._test_datavalue( asdict(adx_format), self.EXPECTED_ADX_DICT_NO_CATEGORY)

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
        remove_namespace(expected)
        #FIXME Name space issue
        #self.assertEqual(ElementTree.tostring(expected), ElementTree.tostring(xml_format))

    def _create_test_adx(self, test_period=VALID_TEST_PERIOD, test_definition=TEST_ADX_DEFINITION):
        builder = ADXBuilder(test_definition)
        org_units = [self._TEST_HF]
        return builder.create_adx_cube(test_period, org_units)

    @classmethod
    def _create_test_organization_unit(cls):
        dateTest = datetime.datetime.now() 
        # First valid district
        district = Location.objects.filter(type='D', validity_to__isnull=True).first()
        cls._TEST_HF = create_test_health_facility('HFT', district.id)
        cls._TEST_INSUREES = [
            cls._create_test_insuree('chft1', 'M', '1950-01-01', '2018-12-01'),
            cls._create_test_insuree('chft2', 'M', '2000-01-01', '2020-01-01'),
            cls._create_test_insuree('chft3', 'F', '2000-01-01', '2020-02-01'),
            cls._create_test_insuree('chft4', 'F', '2000-01-01', '2020-02-01'),
            cls._create_test_insuree('chft5', 'F', '1950-01-01', '2022-01-01'), # should not be in the tests
            cls._create_test_insuree('chft6', 'O', '2000-01-01', '2020-02-01'),
        ]

        org_unit = build_dhis2_id(cls._TEST_HF.uuid)
        cls.EXPECTED_ADX_DICT = {
            'name': 'TEST_HF_ADX_DEFINITION',
            'exported': dateTest,
            'groups': [{
                'complete_date':dateTest.strftime('%Y-%m-%d'),
                'org_unit': org_unit,
                'period': '2019-01-01/P2Y',
                'data_set': "TEST_HF_ADX_DEFINITION",
                'comment': 'Test Comment',
                'data_values': [{
                    'data_element': 'NB_INSUREES',
                    'value': '1',
                    'aggregations': [{
                        'label_name': 'AGEGROUP',
                        'label_value': '<=50yo'
                    }, {
                        'label_name': 'SEX',
                        'label_value': 'M'
                    }]
                }, {
                    'data_element': 'NB_INSUREES',
                    'value': '2',
                    'aggregations': [{
                        'label_name': 'AGEGROUP',
                        'label_value': '<=50yo'
                    }, {
                        'label_name': 'SEX',
                        'label_value': 'F'
                    }]
                },{
                    'data_element': 'NB_INSUREES',
                    'value': '1',
                    'aggregations': [{
                        'label_name': 'AGEGROUP',
                        'label_value': '<=50yo'
                    }, {
                        'label_name': 'SEX',
                        'label_value': 'O'
                    }]
                }, {
                    'data_element': 'NB_INSUREES',
                    'value': '1',
                    'aggregations': [{
                        'label_name': 'AGEGROUP',
                        'label_value': '>50yo'
                    }, {
                        'label_name': 'SEX',
                        'label_value': 'M'
                    }]
                }]
            }]}

        cls.EXPECTED_ADX_DICT_NO_CATEGORY = {
            'name': 'TEST_HF_ADX_DEFINITION',
            'exported':dateTest,  
            'groups': [{
                'complete_date':dateTest.strftime('%Y-%m-%d'),
                'org_unit': org_unit,
                'period': '2019-01-01/P2Y',
                'data_set': "TEST_HF_ADX_DEFINITION",
                'comment': 'Test Comment',
                'data_values': [{
                    'aggregations': [],
                    'data_element': 'NB_INSUREES',
                    'value': '4',
                }]
            }]
        }
        cls.EXPECTED_XML_DUMP = F'''<adx xmlns="urn:ihe:qrph:adx:2015" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ihe:qrph:adx:2015 ../schema/adx_loose.xsd"><group orgUnit="{org_unit}" period="2019-01-01/P2Y" dataSet="TEST_HF_ADX_DEFINITION" comment="Test Comment"><dataValue dataElement="NB_INSUREES" value="1" AGEGROUP="&lt;=50yo" SEX="M" /><dataValue dataElement="NB_INSUREES" value="2" AGEGROUP="&lt;=50yo" SEX="F" /><dataValue dataElement="NB_INSUREES" value="1" AGEGROUP="&gt;50yo" SEX="M" /><dataValue dataElement="NB_INSUREES" value="1" AGEGROUP="&gt;50yo" SEX="F" /></group></adx>'''

    @classmethod
    def _create_test_insuree(cls, chfid: str, sex: str, dob: str, validity: str) -> List[Insuree]:
        return create_test_insuree(
            True,
            custom_props={'chf_id': chfid,
                          'gender': Gender.objects.get(code=sex),
                          'dob': dob,
                          'health_facility': cls._TEST_HF,
                          'validity_from': validity}
        )
