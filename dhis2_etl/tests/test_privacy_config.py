import hashlib
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from insuree.test_helpers import create_test_insuree

import dhis2_etl
from dhis2_etl.apps import DEFAULT_CFG
from dhis2_etl.builders.dhis2.InsureeConverter import InsureeConverter, insureeProgram
from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.strategy import dhis2_client

CONFIGURED_DHIS2 = {"host": "https://dhis2.example.org", "username": "etl", "password": "secret"}
UNCONFIGURED_DHIS2 = {"host": "", "username": "", "password": ""}


class DefaultConfigurationTest(TestCase):
    """OP-3322: no public DHIS2 instance, credentials or salt by default."""

    def test_no_default_connection_or_salt(self):
        self.assertEqual(DEFAULT_CFG["dhis2"], UNCONFIGURED_DHIS2)
        self.assertFalse(DEFAULT_CFG["salt"])
        self.assertFalse(DEFAULT_CFG["export_names"])

    def test_missing_settings_are_listed(self):
        with mock.patch.object(dhis2_etl, "dhis2", UNCONFIGURED_DHIS2, create=True), \
                mock.patch.object(dhis2_etl, "salt", "", create=True):
            self.assertEqual(
                GeneralConfiguration.missing_settings(),
                ["dhis2.host", "dhis2.username", "dhis2.password", "salt"],
            )
        with mock.patch.object(dhis2_etl, "dhis2", CONFIGURED_DHIS2, create=True), \
                mock.patch.object(dhis2_etl, "salt", "deployment-secret", create=True):
            self.assertEqual(GeneralConfiguration.missing_settings(), [])

    def test_connection_must_be_configured(self):
        with mock.patch.object(dhis2_etl, "dhis2", {**CONFIGURED_DHIS2, "password": ""}, create=True):
            with self.assertRaises(ImproperlyConfigured):
                GeneralConfiguration.get_dhis2_connection()
        with mock.patch.object(dhis2_etl, "dhis2", CONFIGURED_DHIS2, create=True):
            self.assertEqual(GeneralConfiguration.get_dhis2_connection(), CONFIGURED_DHIS2)

    def test_api_is_not_created_without_connection(self):
        with mock.patch.object(dhis2_etl, "dhis2", UNCONFIGURED_DHIS2, create=True), \
                mock.patch.object(dhis2_client, "_api", None):
            with self.assertRaises(ImproperlyConfigured):
                dhis2_client.get_api()

    def test_salt_must_be_configured(self):
        for salt in ("", None):
            with self.subTest(salt=salt), mock.patch.object(dhis2_etl, "salt", salt, create=True):
                with self.assertRaises(ImproperlyConfigured):
                    GeneralConfiguration.get_salt()


class InsureeExportPrivacyTest(TestCase):
    """OP-3322: names are not exported by default; identifiers keep their hashing."""

    attributes = insureeProgram["attributes"]

    @classmethod
    def setUpTestData(cls):
        cls.insuree = create_test_insuree(
            with_family=True, custom_props={"chf_id": "OP3322001", "last_name": "Doe", "other_names": "Jane"}
        )

    def _attributes(self, export_names, salt="deployment-secret"):
        with mock.patch.object(dhis2_etl, "salt", salt, create=True), \
                mock.patch.object(dhis2_etl, "export_names", export_names, create=True):
            enrollment = InsureeConverter.to_enrollment_obj(self.insuree)
            tei = InsureeConverter.to_tei_obj(self.insuree)
        return (
            {a.attribute: a.value for a in enrollment.attributes},
            {a.attribute: a.value for a in tei.attributes},
        )

    def test_names_not_exported_by_default(self):
        for exported in self._attributes(export_names=False):
            self.assertNotIn(self.attributes["firstName"], exported)
            self.assertNotIn(self.attributes["lastName"], exported)

    def test_names_exported_when_enabled(self):
        enrollment, tei = self._attributes(export_names=True)
        for exported in (enrollment, tei):
            self.assertEqual(exported[self.attributes["firstName"]], "Jane")
            self.assertEqual(exported[self.attributes["lastName"]], "Doe")

    def test_identifier_hash_is_unchanged(self):
        # same algorithm as before, so the values already in DHIS2 stay valid
        enrollment, _ = self._attributes(export_names=False, salt="LeSalt")
        expected = hashlib.md5(("LeSalt" + "OP3322001").encode("utf-8")).hexdigest()
        self.assertEqual(enrollment[self.attributes["insuranceId"]], expected)
        self.assertEqual(enrollment[self.attributes["CHFId"]], expected)

    def test_export_without_salt_fails(self):
        with mock.patch.object(dhis2_etl, "salt", "", create=True):
            with self.assertRaises(ImproperlyConfigured):
                InsureeConverter.to_enrollment_obj(self.insuree)
