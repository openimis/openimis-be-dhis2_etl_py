import datetime

from django.test import TestCase
from django_adx.builders.adx import ADXBuilder
from django_adx.models.adx.definition import (
    ADXMappingDefinition,
    ADXMappingGroupDefinition,
)
from django_adx.models.adx.time_period import ISOFormatPeriodType
from insuree.models import Insuree, InsureePolicy
from insuree.test_helpers import create_test_gender, create_test_insuree
from policy.models import Policy
from policy.test_helpers import create_test_policy2
from product.test_helpers import create_test_product

from dhis2_etl.services.adx.categories import get_policy_status_categories
from dhis2_etl.services.adx.data_values import get_location_insuree_number_dv
from dhis2_etl.services.adx.utils import get_policy_status_annotation, valid_policy
from dhis2_etl.utils import clean_code


class PolicyStatusTests(TestCase):
    PERIOD = ISOFormatPeriodType().build_period("2026-03-01/P1M")

    @classmethod
    def setUpTestData(cls):
        create_test_gender()
        cls.product = create_test_product("PSTAT")
        cls.active = cls._insuree_with_policy(
            Policy.STATUS_ACTIVE, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
        )
        cls.idle = cls._insuree_with_policy(
            Policy.STATUS_IDLE, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31),
            effective_date=None,
        )
        cls.expired = cls._insuree_with_policy(
            Policy.STATUS_ACTIVE, datetime.date(2025, 1, 1), datetime.date(2025, 12, 31)
        )
        cls.future = cls._insuree_with_policy(
            Policy.STATUS_ACTIVE, datetime.date(2026, 6, 1), datetime.date(2027, 5, 31)
        )
        cls.no_policy = create_test_insuree(is_head=True)

    @classmethod
    def _insuree_with_policy(cls, status, start_date, expiry_date, effective_date=...):
        insuree = create_test_insuree(is_head=True)
        policy, insuree_policy = create_test_policy2(cls.product, insuree)
        if effective_date is ...:
            effective_date = start_date
        dates = dict(
            start_date=start_date,
            effective_date=effective_date,
            expiry_date=expiry_date,
        )
        Policy.objects.filter(id=policy.id).update(
            status=status, enroll_date=start_date, **dates
        )
        InsureePolicy.objects.filter(id=insuree_policy.id).update(**dates)
        return insuree

    def _statuses(self, insuree_level):
        return dict(
            Insuree.objects.annotate(
                policy_status=get_policy_status_annotation(
                    self.PERIOD, insuree_level=insuree_level
                )
            ).values_list("id", "policy_status")
        )

    def _assert_statuses(self, statuses):
        self.assertEqual(statuses[self.active.id], "ACTIVE")
        self.assertEqual(statuses[self.idle.id], "IDLE")
        self.assertEqual(statuses[self.expired.id], "EXPIRED")
        self.assertEqual(statuses[self.future.id], "NO_POLICY")
        self.assertEqual(statuses[self.no_policy.id], "NO_POLICY")

    def test_family_policy_status(self):
        self._assert_statuses(self._statuses(insuree_level=False))

    def test_insuree_policy_status(self):
        self._assert_statuses(self._statuses(insuree_level=True))

    def test_insuree_without_individual_coverage_is_not_active(self):
        InsureePolicy.objects.filter(insuree=self.active).update(effective_date=None)
        statuses = self._statuses(insuree_level=True)
        self.assertEqual(statuses[self.active.id], "EXPIRED")
        # family level still sees the active family policy
        self.assertEqual(self._statuses(insuree_level=False)[self.active.id], "ACTIVE")

    def test_category_codes(self):
        category = get_policy_status_categories()
        codes = [o.code for o in category.category_options]
        self.assertEqual(
            codes,
            ["POL_ACTIVE", "POL_SUSPENDED", "POL_IDLE", "POL_READY", "POL_EXPIRED", "POL_NONE"],
        )

    def test_valid_policy_overlaps_period(self):
        ids = set(
            Insuree.objects.filter(valid_policy(self.PERIOD)).values_list("id", flat=True)
        )
        self.assertIn(self.active.id, ids)
        self.assertIn(self.idle.id, ids)
        self.assertNotIn(self.expired.id, ids)
        self.assertNotIn(self.future.id, ids)

    def test_insuree_number_cube_has_policy_status(self):
        location = self.active.family.location.parent
        definition = ADXMappingDefinition(
            period_type=ISOFormatPeriodType(),
            groups=[
                ADXMappingGroupDefinition(
                    comment="test",
                    data_set="ENROLMENT",
                    org_unit_type=type(location),
                    to_org_unit_code_func=lambda loc: clean_code(loc.uuid),
                    data_values=[get_location_insuree_number_dv(self.PERIOD)],
                )
            ],
        )
        cube = ADXBuilder(definition).create_adx_cube("2026-03-01/P1M", [location])
        data_values = cube.groups[0].data_values
        statuses = [
            agg.label_value
            for dv in data_values
            for agg in dv.aggregations
            if agg.label_name.lower() == "policy_status"
        ]
        self.assertIn("POL_ACTIVE", statuses)
        self.assertEqual(sum(int(dv.value) for dv in data_values), 1)
