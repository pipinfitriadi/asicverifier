#!/usr/bin/env python3

# Copyright (C) Free Software Foundation, Inc. All rights reserved.
# Licensed under the AGPL-3.0-only License. See LICENSE in the project root
# for license information.

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from . import (
    URL,
    QUERY_ID,
    X_ROAD_INSTANCE,
    MEMBER_CLASS,
    MEMBER_CODE,
    SUBSYSTEM_CODE,
    ASICE_TYPE,
    ASIC_VERIFIER_RESPONSE,
    datetime_parser,
    mocked_requests_get
)
from asicverifier.restful_api import RestfulApi


class TestRestfulApi(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName)
        self.maxDiff = None

    @mock.patch('asicverifier.requests.get', side_effect=mocked_requests_get)
    def test_app(self, _):
        client: TestClient = TestClient(RestfulApi.app())
        self.assertEqual(client.get('/').status_code, 200)
        self.assertDictEqual(
            client.post(
                '/',
                params={'conf_refresh': True, 'type': ASICE_TYPE.value},
                json={
                    'securityServerUrl': URL,
                    'queryId': QUERY_ID,
                    'xRoadInstance': X_ROAD_INSTANCE,
                    'memberClass': MEMBER_CLASS,
                    'memberCode': MEMBER_CODE,
                    'subsystemCode': SUBSYSTEM_CODE
                }
            ).json(object_hook=datetime_parser),
            ASIC_VERIFIER_RESPONSE
        )

        with self.assertRaises(AttributeError):
            self.assertEqual(
                client.post(
                    '/',
                    params={'conf_refresh': True, 'type': ASICE_TYPE.value},
                    json={
                        'securityServerUrl': URL.replace('https', 'http'),
                        'queryId': QUERY_ID,
                        'xRoadInstance': X_ROAD_INSTANCE,
                        'memberClass': MEMBER_CLASS,
                        'memberCode': MEMBER_CODE,
                        'subsystemCode': SUBSYSTEM_CODE
                    }
                ).status_code
            )
