#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from dateutil.parser import parse
from dateutil.tz import tzutc
from datetime import datetime
import json
import unittest
from typing import Any
from unittest import mock

from click.testing import Result
import requests
from typer.testing import CliRunner

from asicverifier import (
    AsiceType,
    asicverifier,
    extract_subject_or_issuer,
    extract_asice,
    to_datetime
)
from asicverifier.__main__ import cli
from asicverifier.restful_api import RestfulApi


URL: str = 'https://bjb-security-server.access.digitalservice.id'
QUERY_ID: str = 'XROAD-DISKOMINFO-JABAR-d60266d4-f4d6-4ef9-b3ab-90f8c4196282'
X_ROAD_INSTANCE: str = 'XROAD-DISKOMINFO-JABAR'
MEMBER_CLASS: str = 'FIN'
MEMBER_CODE: str = 'bjb'
SUBSYSTEM_CODE: str = 'QRIS'
ASICE_TYPE: str = AsiceType.RESPONSE
DIRS: str = 'tests/data/'


def datetime_parser(data: dict) -> dict:
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = parse(value)
            except ValueError:
                pass

    return data


with open(f'{DIRS}/asicverifier.json') as json_file:
    ASIC_VERIFIER_RESPONSE: dict = json.loads(
        json_file.read(), object_hook=datetime_parser
    )


class MockResponse:
    def __init__(self, content: Any, status_code: int):
        self.content = content
        self.status_code = status_code
        self.text = None

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.HTTPError


def mocked_requests_get(*args, **kwargs) -> MockResponse:
    status_code: int = 200
    url: str = args[0]
    content: Any = None

    # verificationconf_url
    if url == f'{URL}/verificationconf':
        with open(f'{DIRS}/verificationconf.zip', 'rb') as zip_file:
            content = zip_file.read()
    # asice_url
    elif url == (
        f'{URL}/asic?unique&{ASICE_TYPE}Only&queryId={QUERY_ID}&'
        f'xRoadInstance={X_ROAD_INSTANCE}&memberClass={MEMBER_CLASS}&'
        f'memberCode={MEMBER_CODE}&subsystemCode={SUBSYSTEM_CODE}'
    ):
        with open(f'{DIRS}/request.asice', 'rb') as asice_file:
            content = asice_file.read()
    # for negetive test Zip File
    elif url == f"{URL.replace('https', 'http')}/verificationconf":
        status_code = 404
    # for negetive test Asice File
    elif url == (
        f'{URL}/asic?unique&{AsiceType.REQUEST}Only&queryId={QUERY_ID}&'
        f'xRoadInstance={X_ROAD_INSTANCE}&memberClass={MEMBER_CLASS}&'
        f'memberCode={MEMBER_CODE}&subsystemCode={SUBSYSTEM_CODE}'
    ):
        status_code = 404

    return MockResponse(content, status_code)


class TestAsicVerifier(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName)
        self.maxDiff = None

    def test_main(self):
        result: Result = CliRunner().invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(RestfulApi.run.__doc__, result.stdout)

    def test_to_datetime(self):
        self.assertEqual(
            to_datetime('Mon May 29 08:33:50 GMT 2023'),
            datetime(2023, 5, 29, 8, 33, 50, tzinfo=tzutc())
        )

    def test_extract_subject_or_issuer(self):
        self.assertDictEqual(
            extract_subject_or_issuer(
                'CN=tahura, O=COMMERCE, C=XROAD-DISKOMINFO-JABAR'
            ),
            {
                'C': 'XROAD-DISKOMINFO-JABAR',
                'CN': 'tahura',
                'O': 'COMMERCE'
            }
        )
        self.assertDictEqual(
            extract_subject_or_issuer(
                'CN=Diskominfo Jabar Test CA, O=X-Road Diskominfo Jabar Test '
                'CA'
            ),
            {
                'CN': 'Diskominfo Jabar Test CA',
                'O': 'X-Road Diskominfo Jabar Test CA'
            }
        )

    def test_extract_asice(self):
        with open(f'{DIRS}/asicverifier.log') as log_file:
            self.assertDictEqual(
                extract_asice(log_file.read()),
                ASIC_VERIFIER_RESPONSE
            )

    @mock.patch('asicverifier.requests.get', side_effect=mocked_requests_get)
    def test_asicverifier(self, _):
        self.assertDictEqual(
            asicverifier(
                URL,
                QUERY_ID,
                X_ROAD_INSTANCE,
                MEMBER_CLASS,
                MEMBER_CODE,
                SUBSYSTEM_CODE,
                ASICE_TYPE,
                True
            ),
            ASIC_VERIFIER_RESPONSE
        )
        self.assertDictEqual(
            asicverifier(
                URL,
                QUERY_ID,
                X_ROAD_INSTANCE,
                MEMBER_CLASS,
                MEMBER_CODE,
                SUBSYSTEM_CODE,
                ASICE_TYPE
            ),
            ASIC_VERIFIER_RESPONSE
        )

        with self.assertRaises(requests.exceptions.HTTPError):
            asicverifier(
                URL.replace('https', 'http'),
                QUERY_ID,
                X_ROAD_INSTANCE,
                MEMBER_CLASS,
                MEMBER_CODE,
                SUBSYSTEM_CODE,
                conf_refresh=True
            )

        with self.assertRaises(requests.exceptions.HTTPError):
            asicverifier(
                URL,
                QUERY_ID,
                X_ROAD_INSTANCE,
                MEMBER_CLASS,
                MEMBER_CODE,
                SUBSYSTEM_CODE
            )
