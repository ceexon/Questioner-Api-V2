""" Test for questions """
import os
import unittest
import json
from tests.v2.test_users import BaseTest, secret
from tests.v2.test_meetups import MeetupTest


class TestQuestions(MeetupTest):
    def test_ask_question_comment_and_vote(self):
        """ test ask fails meetup id not found """
        self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok), headers={"x-access-token": self.admin_login()}, content_type="application/json")
        self.question_ask["id"] = 300
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.sign_login_local()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["error"], "Mettup with id 300 not found")

        """ test a successful post """
        self.question_ask["id"] = 3
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.sign_login_local()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ test a try to duplicate post """
        response = self.client.post("/api/v2/questions", data=json.dumps(self.question_ask), headers={
            "x-access-token": self.sign_login_local()}, content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["error"], "A similar question already exists")
