#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from datetime import datetime
import json
import unittest

from click.testing import Result
from typer.testing import CliRunner

from asicverifier import (
    AsicType,
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
ASIC_TYPE: str = AsicType.RESPONSE
ASIC_VERIFIER_RESPONSE: dict = {
    'verificationconf_url': f'{URL}/verificationconf',
    'asic_url': f'{URL}/asic?unique&{ASIC_TYPE}Only&queryId={QUERY_ID}&'
    f'xRoadInstance={X_ROAD_INSTANCE}&memberClass={MEMBER_CLASS}&'
    f'memberCode={MEMBER_CODE}&subsystemCode={SUBSYSTEM_CODE}'
}


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
            datetime(2023, 5, 29, 8, 33, 50)
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
        FILENAME: str = 'tests/data/asicverifier'

        def datetime_parser(data: dict) -> dict:
            for key, value in data.items():
                if isinstance(value, str):
                    try:
                        data[key] = datetime.strptime(
                            value, r'%Y-%m-%d %H:%M:%S'
                        )
                    except ValueError:
                        pass

            return data

        with open(f'{FILENAME}.log') as log_file, open(
                f'{FILENAME}.json') as json_file:
            self.assertDictEqual(
                extract_asice(log_file.read()),
                json.loads(json_file.read(), object_hook=datetime_parser)
            )

    def test_asicverifier(self):
        self.assertDictEqual(
            asicverifier(
                URL,
                QUERY_ID,
                X_ROAD_INSTANCE,
                MEMBER_CLASS,
                MEMBER_CODE,
                SUBSYSTEM_CODE,
                ASIC_TYPE
            ),
            ASIC_VERIFIER_RESPONSE
        )
