""" Test for meetups """
import os
import unittest
import json
from tests.v2.test_users import BaseTest, secret


class MeetupTest(BaseTest):
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
            "password": "$$22BBkk",
            "gender": "m"
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

    def test_meetups(self):
        admin_token = self.admin_login()
        """ test fail to get all meet records not found """
        admin_token = self.admin_login()
        response = self.client.get(
            "api/v2/meetups", headers={"x-access-token": admin_token})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            "api/v2/meetups/upcoming", headers={"x-access-token": admin_token})
        self.assertEqual(response.status_code, 404)

        """ test fail to get meet record by id """
        admin_token = self.admin_login()
        response = self.client.get("api/v2/meetups/1738")
        not_found = json.loads(response.data.decode("utf-8"))
        self.assertEqual(not_found["error"], "Mettup with id 1738 not found")
        self.assertEqual(response.status_code, 404)

        """ test when token is missing """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "Token is missing")
        self.assertEqual(response.status_code, 401)

        """ test when token is invalid """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            headers={"x-access-token": "bacneuk,kcn,cnj,ncaacba"},
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "Token is invalid or expired")
        self.assertEqual(response.status_code, 401)

        """ test when topic is missing """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_no_topic),
            headers={"x-access-token": admin_token},
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            created["error"],
            "missing either (topic,happen_on,location, image or tags)")
        self.assertEqual(response.status_code, 400)

        """ test when tags is empty """
        self.meetup_no_topic["topic"] = "some radom topic"
        self.meetup_no_topic["tags"] = []
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_no_topic),
            headers={"x-access-token": admin_token},
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(created["error"], "tags field is required")
        self.assertEqual(response.status_code, 400)

        """ test success meetup creation"""
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            headers={"x-access-token": admin_token},
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(response.status_code, 201)

        """ testforbidden meetup creation """
        local_token = self.sign_login_local()
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            headers={"x-access-token": local_token},
            content_type="application/json")
        not_created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(not_created["error"], "you cannot create a meetup")
        self.assertEqual(response.status_code, 403)

        """ test meetup creation attempt to duplicate """
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            headers={"x-access-token": admin_token},
            content_type="application/json")
        created = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            created["error"],
            "You may be trying to duplicate a meetup, one with same time and location exists")
        self.assertEqual(response.status_code, 409)

        """ test success get all meet records admin """
        admin_token = self.admin_login()
        response = self.client.get(
            "api/v2/meetups", headers={"x-access-token": admin_token})
        self.assertEqual(response.status_code, 200)

        """ test success get all meet records admin """
        local_token = self.sign_login_local()
        response = self.client.get(
            "api/v2/meetups", headers={"x-access-token": local_token})
        cannot = json.loads(response.data.decode("utf-8"))
        self.assertEqual(cannot["error"], "you canot access the meetups")
        self.assertEqual(response.status_code, 403)

        """ test success get ucoming meetups """
        response = self.client.get("api/v2/meetups/upcoming")
        self.assertEqual(response.status_code, 200)

        """ test success get one record failed """
        admin_token = self.admin_login()
        response = self.client.get("api/v2/meetups/y0y0")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["error"], "invalid id, use integer")
        self.assertEqual(response.status_code, 400)

        """ test delete meetup """
        self.client.post(
            "api/v2/meetups",
            data=json.dumps(self.meetup_to_delete),
            headers={"x-access-token": admin_token},
            content_type="application/json")

        """ delete forbidden """
        response = self.client.delete(
            "/api/v2/meetups/2",  headers={"x-access-token": local_token})
        deleted = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(deleted["error"], "you canot delete a meetup")
        self.assertEqual(response.status_code, 403)

        """ delete id out of range or invalid """
        response = self.client.delete(
            "/api/v2/meetups/20",  headers={"x-access-token": admin_token})
        deleted = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(deleted["error"], "Mettup with id 20 not found")
        self.assertEqual(response.status_code, 404)

        """ delete successful """
        response = self.client.delete(
            "/api/v2/meetups/2",  headers={"x-access-token": admin_token})
        deleted = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(deleted["message"], "meetup deleted successfully")
        self.assertEqual(response.status_code, 200)

    def test_meetup_rsvp(self):
        """ create meetup """
        admin_token = self.admin_login()
        response = self.client.post(
            "api/v2/meetups", data=json.dumps(self.meetup_ok),
            headers={"x-access-token": admin_token},
            content_type="application/json")

        """ test fail no token """
        admin_token = self.admin_login()
        response = self.client.post(
            "api/v2/meetups/1/rsvp")
        missingToken = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(missingToken["error"], "Token is missing")

        """ test success get one record"""
        admin_token = self.admin_login()
        response = self.client.get(
            "api/v2/meetups/1", headers={"x-access-token": admin_token})

        dat_error = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        """ test rsvp no status """
        response = self.client.post(
            "api/v2/meetups/1/rsvp",
            headers={"x-access-token": admin_token},
            data=json.dumps({"mangos": "fruit"}),
            content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["error"], "Rsvp info is Missing")
        self.assertEqual(response.status_code, 400)

        """ test invalid meetup rsvp response"""
        response = self.client.post(
            "api/v2/meetups/1/rsvp",
            headers={"x-access-token": admin_token},
            data=json.dumps({"status": "fruit"}),
            content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(
            error_message["error"],
            "invalid choice. Status response is limited to 'yes/maybe/no'")
        self.assertEqual(response.status_code, 400)

        """ test invalid meetup id"""
        response = self.client.post(
            "api/v2/meetups/89/rsvp", headers={"x-access-token": admin_token},
            data=json.dumps({"status": "y"}), content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["error"], "Mettup with id 89 not found")
        self.assertEqual(response.status_code, 404)

        """ test rsvp meetup success """
        response = self.client.post(
            "api/v2/meetups/1/rsvp",
            headers={"x-access-token": admin_token},
            data=json.dumps({"status": "y"}), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        """ test try to rsv again yes"""
        response = self.client.post(
            "api/v2/meetups/1/rsvp", headers={"x-access-token": admin_token},
            data=json.dumps({"status": "y"}), content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["error"],
                         "RSVP is only once, try updating status")
        self.assertEqual(response.status_code, 403)

        """ test try to rsv again no"""
        response = self.client.post(
            "api/v2/meetups/1/rsvp", headers={"x-access-token": admin_token},
            data=json.dumps({"status": "n"}), content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["message"],
                         "response received")
        self.assertEqual(response.status_code, 201)

        """ test try to rsv again maybe"""
        response = self.client.post(
            "api/v2/meetups/1/rsvp", headers={"x-access-token": admin_token},
            data=json.dumps({"status": "maybe"}), content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8"))
        self.assertEqual(error_message["message"],
                         "response received")
        self.assertEqual(response.status_code, 201)
