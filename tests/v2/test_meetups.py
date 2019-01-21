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

    def sign_login_local(self):
        payload =  {
            "firstname": "burudi",
            "lastname": "zonecc",
            "othername": "BK",
	 		"username": "kurlandss",
            "email": "kurlandss@zonecc.bk",
            "phone": "+09778789847",
            "password": "$$22BBkk"
           }
        self.client.post("api/v2/auth/signup", data=json.dumps(payload), content_type="application/json")
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps({"username":"kurlandss","password":"$$22BBkk"}), content_type="application/json")
        fetch_local_token = json.loads(response.data.decode("utf-8", secret))
        local_token = fetch_local_token["token"]
        return local_token

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

        """ test success meetup forbidden"""
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(response.status_code, 201)

        """ test success meetup creation """
        local_token = self.sign_login_local()
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":local_token} ,content_type="application/json")
        not_created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(not_created["error"],"you cannot create a meetup")
        self.assertEqual(response.status_code, 403)

        """ test success meetup creation duplicate """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),headers={"x-access-token":admin_token} ,content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "You may be trying to duplicate a meetup, one with same time and location exists")
        self.assertEqual(response.status_code, 409)


    def test_get_meetup(self):
        """ test success get all meet records admin """
        admin_token = self.admin_login()
        response = self.client.get("api/v2/meetups",headers={"x-access-token":admin_token})
        self.assertEqual(response.status_code, 200)

        """ test success get all meet records admin """
        local_token = self.sign_login_local()
        response = self.client.get("api/v2/meetups",headers={"x-access-token":local_token})
        cannot = json.loads(response.data.decode("utf-8"))
        self.assertEqual(cannot["error"],"you canot access the meetups")
        self.assertEqual(response.status_code, 403)

        """ test success get ucoming meetups """
        response = self.client.get("api/v2/meetups/upcoming")
        self.assertEqual(response.status_code, 200)
