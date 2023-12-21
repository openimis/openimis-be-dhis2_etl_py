import datetime
from typing import List
from unittest import mock

from claim.test_helpers import create_test_claim
from django.test import TestCase
from insuree.models import Education, FamilyType, Gender, Insuree, Profession
from insuree.test_helpers import create_test_insuree
from medical.models import Diagnosis, Item, Service
from policy.test_helpers import create_test_policy2
from product.test_helpers import create_test_product

from dhis2_etl.builders.dhis2.ClaimConverter import ClaimConverter
from dhis2_etl.builders.dhis2.InsureeConverter import InsureeConverter
from dhis2_etl.builders.dhis2.OptionSetConverter import OptionSetConverter
from dhis2_etl.scheduled_tasks import SyncFunction
from dhis2_etl.scheduled_tasks.utils import (has_model_changed_in_timeframe,
                                             sync_optionset_if_changed,
                                             sync_product_if_changed)
from dhis2_etl.services.claimServices import syncClaim
from dhis2_etl.services.insureeServices import syncPolicy


class DailySyncTests(TestCase):
    def setUp(self) -> None:
        super(DailySyncTests, self).setUp()
        self.timeframe = (datetime.datetime(2018, 12, 10), datetime.datetime(2018, 12, 11))
        self.post_method_called_with = {}
        self.post_multiple_called_with = []

    def test_has_model_changed_in_timeframe(self):
        model = Insuree
        timeframe = self.timeframe
        self.__validate_timeframe(model, timeframe)
        self.assertFalse(has_model_changed_in_timeframe(model.objects, *timeframe))
        new_insuree1 = self._create_test_insuree('chft1', 'M', '1950-01-01', '2018-12-11T00:00:01')
        new_insuree2 = self._create_test_insuree('chft2', 'M', '1950-01-01', '2018-12-09T23:59:59')
        self.assertFalse(has_model_changed_in_timeframe(model.objects, *timeframe))
        new_insuree3 = self._create_test_insuree('chft3', 'M', '1950-01-01', '2018-12-10T00:00:01')
        self.assertTrue(has_model_changed_in_timeframe(model.objects, *timeframe))

    def test_claim_sync(self):
        sync_func = SyncFunction("claim", syncClaim, True)
        with mock.patch("dhis2_etl.services.claimServices.postMethod") as post_method:
            claim = create_test_claim({"status": 16, 'validity_from': datetime.datetime(2018, 12, 10, 5)})
            self._test_sync_func(sync_func, post_method, 'enrollments', ClaimConverter.to_enrollment_objs,
                                 [claim], {'event': True})

    def test_product_sync(self):
        sync_func = SyncFunction("product", sync_product_if_changed, True)
        with mock.patch("dhis2_etl.services.optionSetServices.postMethod") as post_method:
            product = create_test_product(
                "VIS1T", custom_props={"max_no_visits": 1, 'validity_from': datetime.datetime(2018, 12, 10, 5)})
            self._test_sync_func(sync_func, post_method, 'metadata', OptionSetConverter.to_optionsets_bundled,
                                 [product], {'optiontSetName': 'product', 'code': 'id'})

    def test_other_optionset_sync(self):
        sync_func = SyncFunction("other_optionset", sync_optionset_if_changed, True)
        o_s = {
            Gender: list(Gender.objects.all()),
            Profession: list(Profession.objects.all()),
            Education: list(Education.objects.all()),
            FamilyType: list(FamilyType.objects.all()),
        }
        for o in [Diagnosis, Item, Service]:
            o_s[o] = self._update_optionset_and_save(o)

        with mock.patch("dhis2_etl.services.optionSetServices.postMethod") as post_method_mock:
            expected_calls = [
                {'ressource': 'metadata', 'objs': o_s[Gender], 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'gender', 'code': 'code'}},
                {'ressource': 'metadata', 'objs': o_s[Profession],
                 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'profession', 'code': 'id'}},
                {'ressource': 'metadata', 'objs': o_s[FamilyType],
                 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'groupType', 'code': 'code'}},
                {'ressource': 'metadata', 'objs': o_s[Education], 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'education', 'code': 'id'}},
                {'ressource': 'metadata', 'objs': [o_s[Diagnosis]],
                 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'diagnosis', 'code': 'id'}},
                {'ressource': 'metadata', 'objs': [o_s[Item]], 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'item', 'code': 'id'}},
                {'ressource': 'metadata', 'objs': [o_s[Service]], 'convertor': OptionSetConverter.to_optionsets_bundled,
                 'kwargs': {'optiontSetName': 'service', 'code': 'id'}},
            ]
            post_method_mock.side_effect = self._post_multiple_side_effect
            sync_func.sync(*self.timeframe)
            post_method_mock.assert_called()
            for call in expected_calls:
                self.assertIn(call, self.post_multiple_called_with)

    def _update_optionset_and_save(self, model):
        obj_ = model.objects.filter(validity_to__isnull=True).first()
        obj_.validity_from = datetime.datetime(2018, 12, 10, 5)
        obj_.save()
        return obj_

    def test_policy_sync(self):
        sync_func = SyncFunction("policies", syncPolicy, True)
        with mock.patch("dhis2_etl.services.insureeServices.postMethod") as post_method:
            insuree = create_test_insuree()
            self.assertIsNotNone(insuree)
            product = create_test_product("VISIT", custom_props={"max_no_visits": 1})
            policy, insuree_policy = create_test_policy2(product, insuree,
                                                         custom_props={'expiry_date': datetime.datetime(2018, 12, 15),
                                                                       'validity_from': datetime.datetime(2018, 12, 10,
                                                                                                          5)})
            insuree_policy.validity_from = datetime.datetime(2018, 12, 10, 5)
            insuree_policy.expiry_date = datetime.datetime(2018, 12, 15, 5)
            insuree_policy.save()
            self._test_sync_func(sync_func, post_method, 'events', InsureeConverter.to_event_objs,
                                 [insuree_policy], {'page_size': 100})

    def _test_sync_func(self, sync_func: SyncFunction, post_method_mock,
                        expected_resource, expected_convertor, expected_objects, expected_kwargs):
        post_output = "testoutput"
        post_method_mock.side_effect = self._post_method_side_effect
        result = sync_func.sync(*self.timeframe)
        post_method_mock.assert_called()
        self.assertEqual(result, post_output)
        self.assertEqual(self.post_method_called_with['ressource'], expected_resource)
        self.assertEqual(self.post_method_called_with['convertor'], expected_convertor)
        self.assertEqual(self.post_method_called_with['kwargs'], expected_kwargs)
        self.assertEqual(list(self.post_method_called_with['objs']), expected_objects)

    def _post_method_side_effect(self, ressource, objs, convertor, **kwargs):
        self.post_method_called_with = {
            'ressource': ressource, 'objs': objs, 'convertor': convertor, 'kwargs': kwargs
        }
        return "testoutput"

    def _post_multiple_side_effect(self, ressource, objs, convertor, **kwargs):
        self.post_multiple_called_with.append({
            'ressource': ressource, 'objs': list(objs), 'convertor': convertor, 'kwargs': kwargs
        })

    def __validate_timeframe(self, model, timeframe):
        in_timeframe = model.objects.filter(legacy_id__isnull=True) \
            .filter(validity_from__lte=timeframe[1]) \
            .filter(validity_from__gte=timeframe[0]) \
            .count()
        if in_timeframe > 0:
            raise ValueError(f"Test setup failed, there are unexpected entries added between {timeframe}")

    @classmethod
    def _create_test_insuree(cls, chfid: str, sex: str, dob: str, validity: str) -> List[Insuree]:
        return create_test_insuree(
            True,
            custom_props={'chf_id': chfid,
                          'gender': Gender.objects.get(code=sex),
                          'dob': dob,
                          'validity_from': validity}
        )
