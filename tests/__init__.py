#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from datetime import datetime
import json
import unittest

from asicverifier import extract_subject_or_issuer, extract_asic, to_datetime


class TestAsicVerifier(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName)
        self.maxDiff = None

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

    def test_extract_asic(self):
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
                extract_asic(log_file.read()),
                json.loads(json_file.read(), object_hook=datetime_parser)
            )
