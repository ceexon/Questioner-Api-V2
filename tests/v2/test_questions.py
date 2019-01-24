""" Test for questions """
import os
import unittest
import json
from tests.v2.test_users import BaseTest, secret


class TestQuestions(BaseTest):
    def admin_login(self):
        response = self.client.post(
            "api/v2/auth/login",
            data=json.dumps({"username": "admin", "password": "$$PAss12"}),
            content_type="application/json")
        fetch_adm_token = json.loads(response.data.decode("utf-8", secret))
        admin_token = fetch_adm_token["token"]
        return admin_token

    def sign_login_local(self):
        payload = {
            "firstname": "burudi",
            "lastname": "zonecc",
            "othername": "BK",
                        "username": "kurlandss",
            "email": "kurlandss@zonecc.bk",
            "phone": "+09778789847",
            "password": "$$22BBkk"
        }
        self.client.post(
            "api/v2/auth/signup",
            data=json.dumps(payload), content_type="application/json")
        response = self.client.post(
            "api/v2/auth/login",
            data=json.dumps({"username": "kurlandss", "password": "$$22BBkk"}),
            content_type="application/json")
        fetch_local_token = json.loads(response.data.decode("utf-8", secret))
        local_token = fetch_local_token["token"]
        return local_token

    def test_ask_question_comment_and_vote(self):
        """ test ask fails meetup id not found """
        self.client.post(
            "api/v2/meetups",
            data=json.dumps(self.meetup_ok),
            headers={"x-access-token": self.admin_login()},
            content_type="application/json")

        """ test a meetup id not found post """
        response = self.client.post(
            "/api/v2/questions",
            data=json.dumps(self.question_ask), headers={
                "x-access-token": self.admin_login()},
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(result["error"], "Mettup with id 3 not found")

        """ test a successful post """
        response = self.client.post(
            "/api/v2/questions",
            data=json.dumps(self.right_meetup_id_added), headers={
                "x-access-token": self.admin_login()},
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ test a try to duplicate post """
        response = self.client.post(
            "/api/v2/questions",
            data=json.dumps(self.right_meetup_id_added), headers={
                "x-access-token": self.admin_login()},
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["error"], "A similar question already exists")

        """ test voting for question """
        """ test upvote """
        response = self.client.patch(
            "/api/v2/questions/1/upvote",
            headers={
                "x-access-token": self.sign_login_local()})
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ test upvote again fail """
        response = self.client.patch(
            "/api/v2/questions/1/upvote",
            headers={
                "x-access-token": self.sign_login_local()})
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            result["error"], "You have already voted, try updating")

        """ test downvote fails after upvote same user """
        response = self.client.patch(
            "/api/v2/questions/1/downvote",
            headers={
                "x-access-token": self.sign_login_local()})
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            result["error"], "You have already voted, try updating")

        """ test downvote """
        response = self.client.patch(
            "/api/v2/questions/1/downvote",
            headers={
                "x-access-token": self.admin_login()})
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ test comment on question """
        """ comment successful """
        testComment = {"comment": "my comment"}
        response = self.client.post(
            "/api/v2/questions/1/comments",
            data=json.dumps(testComment),
            headers={"x-access-token": self.admin_login()},
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result["data"])

        """ comment unsuccessful no data"""
        response = self.client.post("/api/v2/questions/1/comments", headers={
            "x-access-token": self.admin_login()})
        self.assertEqual(response.status_code, 400)

        """ logging out """
        logoutToken = self.sign_login_local()
        response = self.client.post("api/v2/auth/logout", headers={
            "x-access-token": logoutToken})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/v2/questions/1/comments",
            data=json.dumps(testComment),
            headers={"x-access-token": logoutToken},
            content_type="application/json")
        result = json.loads(response.data.decode("utf-8"), secret)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["error"], "Token has already been used")
        self.assertEqual(result["message"], "please login again to continue")
