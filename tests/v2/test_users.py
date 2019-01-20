"""The user endpoints tests"""
from app.api.v2.models.db_connect import db_init
from instance.config import app_config
from app import create_app
import os
import unittest
import json
secret = os.getenv("SECRET")


class BaseTest(unittest.TestCase):
    """
    The base class for seeting up the user tests and tearing down
    """

    def setUp(self):
        """
        set the variables before each test
        """
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.db_url = app_config['DB_TEST']
        db_init(self.db_url)

        self.success_signup = {
            "firstname": "HHHHH",
            "lastname": "Kurland",
            "othername": "missme",
            "username": "toovor",
            "email": "jjj@djjd.dd",
            "phone": "+09778789847",
            "password": "$$22BBkk"
        }

        self.miss_signup = {
            "firstname": "HHHHH",
            "lastname": "Kurland",
            "othername": "missme",
            "username": "toovor",
            "phone": "+09778789847",
            "password": "$$22BBkk"
        }

    def tearDown(self):
        self.app.testing = False
        db_init(self.db_url)


class UserSignUp(BaseTest):

    def test_user_sign_up(self):
        """user signup success """
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        """Test username taken """
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 409)
        exists = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(exists["error"], "user with username exists")

        """Test signupfail no email"""
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.miss_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 404)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(error_message["message"], 'email field(s) not found')

        """Test signupfail empty email"""
        self.success_signup["email"] = ""
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        errorm = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(errorm["message"], "email field(s) can't be empty")

        """Test signupfail bad email format """
        self.success_signup["email"] = "...@...com"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["error"], 'invalid email format!! -> (example@mail.com)')

        """Test signupfail bad username """
        self.success_signup["email"] = "jjj@nnn.com"
        self.success_signup["username"] = "jjj@nnn.com"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["error"], 'username can only be a letter, digit or _')

        """Test signupfail bad password """
        self.success_signup["username"] = "jjjnncom"
        self.success_signup["password"] = "jjjom"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(error_message["error"], 'invalid password')
        self.assertEqual(
            error_message["message"], 'lentgh less than 6, no digits, no uppercase letter, no symbol')

        """Test signupfail bad phone invalid """
        self.success_signup["password"] = "jjjomKK**56"
        self.success_signup["phone"] = "jjjomKK**56"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["message"], "phone number can start with '+' and have digits")

        """Test signupfail bad phone invalid """
        self.success_signup["phone"] = "+737363663"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["message"], 'phone number length invalid(11-13)')

        """Test signupfail bad phone invalid """
        self.success_signup["phone"] = "3363663"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["message"], 'phone number length invalid(10)')


class TestUserLogin(BaseTest):
    def test_successful_login(self):
        """ tests succesful login """
        self.client.post("api/v2/auth/signup", data=json.dumps(
            self.success_signup), content_type="application/json")
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps(self.success_signup), content_type="application/json")
        result = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result["token"])

        """registered username but wrong password"""
        self.success_signup["password"] = "toovor"
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps(self.success_signup), content_type="application/json")
        result = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(result["error"], "incorrect password")
        self.assertEqual(response.status_code, 401)

        """unregistered username"""
        self.success_signup["username"] = "somename"
        response = self.client.post(
            "api/v2/auth/login", data=json.dumps(self.success_signup), content_type="application/json")
        result = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(result["error"], "unregistered username")
        self.assertEqual(response.status_code, 401)
