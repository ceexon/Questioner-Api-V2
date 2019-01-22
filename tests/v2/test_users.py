"""The user endpoints tests"""
import os
import unittest
import json
import psycopg2
from app.api.v2.models.db_connect import db_init, drop_tables, create_admin, connect_db, delete_dummy_user
from instance.config import app_config
from app import create_app
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
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.conn = connect_db()
        db_init(self.conn)
        create_admin(self.conn)

        self.client = self.app.test_client()

        self.success_signup = {
            "firstname": "HHHHH",
            "lastname": "Kurland",
            "othername": "missme",
            "username": "toovor",
            "email": "jjj@djjd.dd",
            "phone": "+09778789847",
            "password": "$$22BBkk"
        }

        self.delete_after_login = {
            "firstname": "HHHHH",
            "lastname": "Kurland",
            "othername": "missme",
            "username": "missme",
            "email": "missme@djjd.dd",
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

        self.meetup_to_delete = {
            "topic": "Formlessly",
            "location": "Nairobi Kenya",
            "happen_on": "09/04/2029/1600HRS",
            "tags": ["#meetme", "#works well"]
        }

        self.meetup_ok = {
            "topic": "Formless",
            "location": "Nairobi ",
            "happen_on": "09/04/2019/1600HRS",
            "tags": ["#meetme", "#works well"]
        }

        self.meetup_no_topic = {
            "location": "Nairobi ",
            "happen_on": "09/04/2019/1600HRS",
            "tags": ["#meetme", "#works well"]
        }

        self.question_ask = {
            "meetup": "2",
            "title": "my question",
            "body": "my description"
        }

    def tearDown(self):
        delete_dummy_user(self.conn)


class UserSignUp(BaseTest):

    def test_user_sign_up_success(self):
        """ test signup fail invalid names """
        self.success_signup["firstname"] = "j???202||"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["error"], 'invalid naming format')
        self.assertEqual(
            error_message["message"], 'first, last and other name can only contain letters')
        print(error_message)
        self.assertEqual(response.status_code, 422)

        """user signup success """
        self.success_signup["firstname"] = "working"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        """user signup empty json """
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps({}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 204)

        """user signup no data """
        response = self.client.post(
            "api/v2/auth/signup", content_type="application/json")
        self.assertEqual(response.status_code, 204)

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
        self.assertEqual(error_message["error"], 'email field(s) not found')

        """Test signupfail empty email"""
        fake = self.success_signup
        fake["username"] = "Bakari"
        fake["email"] = ""
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(fake),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        errorm = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(errorm["error"], "email field(s) can't be empty")

        """Test signupfail empty email"""
        fake = self.success_signup
        fake["username"] = "Bakari"
        fake["email"] = "jjj@djjd.dd"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(fake),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 409)
        errorm = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(errorm["error"], "user with email exists")

        """Test signupfail white_space email"""
        fake = self.success_signup
        fake["username"] = "Bakari"
        fake["email"] = "       "
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(fake),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        errorm = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            errorm["error"], "email field(s) can't be white space only")

        """Test signupfail bad email format """
        signup_email = self.success_signup
        signup_email["username"] = "varchar"
        signup_email["email"] = "...@...com"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(signup_email),
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
        self.success_signup["username"] = "jjjoonncom"
        self.success_signup["password"] = "jjjom"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(error_message["error"], 'invalid password')
        self.assertEqual(
            error_message["message"], 'lentgh less than 6, no digits, no uppercase letter, no symbol')

        """Test signupfail bad password """
        self.success_signup["username"] = "jjjoonncom"
        self.success_signup["password"] = "JJ$$14OI"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(error_message["error"], 'invalid password')
        self.assertEqual(
            error_message["message"], 'no lowercase letter')

        """Test signupfail bad phone invalid """
        self.success_signup["username"] = "jjjoonncom"
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
        self.success_signup["username"] = "jjjoonncom"
        self.success_signup["phone"] = "+737363663"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["message"], 'phone number length invalid(11-13)')

        """Test signupfail bad phone invalid alphas """
        self.success_signup["username"] = "jjjoonncom"
        self.success_signup["phone"] = "+737h636kk63"
        response = self.client.post("api/v2/auth/signup",
                                    data=json.dumps(self.success_signup),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 422)
        error_message = json.loads(response.data.decode("utf-8", secret))
        self.assertEqual(
            error_message["message"], "phone number can only be digits after '+'")

        """Test signupfail bad phone invalid """
        self.success_signup["username"] = "jjjoonncom"
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
