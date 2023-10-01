#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

import unittest

from fastapi.testclient import TestClient

from asicverifier.restful_api import RestfulApi


class TestRestfulApi(unittest.TestCase):
    def test_app(self):
        client: TestClient = TestClient(RestfulApi.app())
        self.assertEqual(client.get('/docs').status_code, 200)
