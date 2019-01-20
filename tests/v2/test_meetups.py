""" Test for meetups """
import os
import unittest
import json
from tests.v2.test_users import BaseTest, secret

class MeetupTest(BaseTest):
    def admin_login(self):
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps({"username":"admin","password":"$$PAss12"}), content_type="application/json")
        fetch_adm_token = json.loads(response.data.decode("utf-8", secret))
        admin_token = fetch_adm_token["token"]
        return admin_token

    def test_meetups_creation(self):
        admin_token = self.admin_login()
        """ test when token is missing """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok), content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "Token is missing")
        self.assertEqual(response.status_code, 401)

        """ test when token is invalid """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":"bacneuk,kcn,cnj,ncaacba"} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "Token is invalid or expired")
        self.assertEqual(response.status_code, 401)

        """ test when topic is missing """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_no_topic),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "missing either (topic,happen_on,location or tags)")
        self.assertEqual(response.status_code, 400)

        """ test when tags is empty """
        self.meetup_no_topic["topic"] = "some radom topic"
        self.meetup_no_topic["tags"] = []
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_no_topic),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "tags field is required")
        self.assertEqual(response.status_code, 400)

        """ test success meetup creation """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(response.status_code, 201)

        """ test success meetup creation duplicate """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "You may be trying to duplicate a meetup, one with same time and location exists")
        self.assertEqual(response.status_code, 409)
