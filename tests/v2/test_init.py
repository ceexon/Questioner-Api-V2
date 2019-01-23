import json
import unittest
from tests.v2.test_users import BaseTest
from app.api.v2.models import db_connect


class TestInitApp(BaseTest):
    def test_wromg_init_methods(self):
        """user signup wrong url """
        response = self.client.post(
            "api/v2/auth/signup/name",
            data=json.dumps(self.success_signup),
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(result["error"], "Url not found")
        self.assertEqual(response.status_code, 404)

        """user signup method not allowed """
        response = self.client.get(
            "api/v2/auth/signup",
            data=json.dumps(self.success_signup),
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(result["error"], "Method not allowed")
        self.assertEqual(response.status_code, 405)

        """ Test db_connect drop tables if exist"""
        result = db_connect.drop_table_if_exists()
        self.assertTrue(result)

        """ Test db_connect set_up_tables """
        result = db_connect.set_up_tables()
        self.assertTrue(result)
