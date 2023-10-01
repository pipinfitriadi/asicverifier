#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

import unittest

from fastapi.testclient import TestClient

from . import (
    URL,
    QUERY_ID,
    X_ROAD_INSTANCE,
    MEMBER_CLASS,
    MEMBER_CODE,
    SUBSYSTEM_CODE,
    ASIC_TYPE,
    ASIC_VERIFIER_RESPONSE
)
from asicverifier.restful_api import RestfulApi


class TestRestfulApi(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName)
        self.maxDiff = None

    def test_app(self):
        client: TestClient = TestClient(RestfulApi.app())
        self.assertEqual(client.get('/docs').status_code, 200)
        self.assertDictEqual(
            client.get(
                '/',
                params={
                    'security_server_url': URL,
                    'query_id': QUERY_ID,
                    'x_road_instance': X_ROAD_INSTANCE,
                    'member_class': MEMBER_CLASS,
                    'member_code': MEMBER_CODE,
                    'subsystem_code': SUBSYSTEM_CODE,
                    'type': ASIC_TYPE.value
                }
            ).json(),
            ASIC_VERIFIER_RESPONSE
        )
