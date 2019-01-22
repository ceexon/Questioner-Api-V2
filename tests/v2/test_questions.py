""" Test for questions """
import os
import unittest
import json
from tests.v2.test_users import BaseTest, secret


class TestQuestions(BaseTest):
    def admin_login(self):
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps({"username": "admin", "password": "$$PAss12"}), content_type="application/json")
        fetch_adm_token = json.loads(response.data.decode("utf-8", secret))
        admin_token = fetch_adm_token["token"]
        return admin_token

    def test_ask_question_comment_and_vote(self):
        """ test ask fails meetup id not found """
        meetup = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok), headers={"x-access-token": self.admin_login()}, content_type="application/json")
        get_meetup = json.loads(meetup.data.decode("utf-8"))
        self.question_ask["id"] = 50
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.admin_login()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["error"], "Mettup with id 50 not found")

        """ test a successful post """
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.admin_login()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ test a try to duplicate post """
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.admin_login()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["error"], "A similar question already exists")
