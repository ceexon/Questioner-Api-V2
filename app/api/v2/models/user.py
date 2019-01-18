""" user models """
import datetime
import psycopg2
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app.api.v2.models import db_connect

TIME_NOW = datetime.datetime.utcnow()


class User:
    """docstring for User"""

    def __init__(self, firstname=None, lastname=None, othername=None,
                 username=None, email=None, phone=None, password=None, isAdmin=False):

        self.fname = firstname
        self.lname = lastname
        self.other = othername
        self.uname = username
        self.email = email
        self.password = generate_password_hash(str(password))
        self.phone = phone
        self.publicId = str(uuid.uuid4())
        self.now = TIME_NOW
        self.isAdmin = isAdmin
        if self.uname == "admin":
            self.isAdmin = True

    def create_new_user(self):
        """ creates/adds a new user to the users table"""
        if not User.get_all_users():
            self.isAdmin = True
        query = """
			INSERT INTO users(firstname, lastname, othername, username, email, phone, password, publicId, register_date, isAdmin) VALUES(
			'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}')""".format(self.fname, self.lname, self.other, self.uname, self.email, self.phone, self.password, self.publicId, self.now, self.isAdmin)
        db_connect.query_db_no_return(query)

    @staticmethod
    def get_all_users():
        query = """ SELECT * FROM users """
        all_users = db_connect.select_from_db(query)
        if not all_users:
            return None

        list_of_all_users = []
        for user in all_users:
            a_user = User.format_user_info(user)
            list_of_all_users.append(a_user)
        return list_of_all_users

    @staticmethod
    def format_user_info(user_tuple):
        a_user = {
            "id": user_tuple[0],
            "firstname": user_tuple[1],
            "lastname": user_tuple[2],
            "othername": user_tuple[3],
            "username": user_tuple[4],
            "email": user_tuple[5],
            "phone": user_tuple[6],
            "password": user_tuple[7],
            "publicId": user_tuple[8],
            "isAdmin": user_tuple[9],
            "register_date": user_tuple[10]
        }

        return a_user

    @staticmethod
    def compare_the_hash(hashed, password):
        match = check_password_hash(hashed, str(password))
        return match

    def update_user_info(self, user_id):
        query = """ UPDATE users SET
			firstname = '{}',
			lastname = '{}',
			othername = '{}',
			username = '{}',
			email = '{}',
			password = '{}',
			phone = '{}',
			isAdmin = '{}'
			WHERE publicId = {}
		""".format(self.fname, self.lname, self.other, self.uname, self.email, self.password, self.phone, self.isAdmin, user_id)
        db_connect.query_db_no_return(query)

    def delete_user(self, p_id):
        query = """ DELETE FROM requests WHERE public_id='{}' """.format(p_id)
        db_connect.query_db_no_return(query)

    @staticmethod
    def query_username(username):
        """
        Query the users store for a user
        """
        query = """
        SELECT id, username, email, password, isAdmin FROM users
        WHERE users.username = '{}'""".format(username)
        here = db_connect.select_from_db(query)
        return here

    @staticmethod
    def create_admin_user():
        adm_pid = str(uuid.uuid4())
        query = """
        INSERT INTO users(firstname, lastname, othername, username, email, phone, password, publicId, register_date, isAdmin) VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}',"{}")
        """.format("adm", "super", "user", "admin", "adm@super.men", "0712345678", "llLL77**", adm_pid, datetime.datetime.now(), "True")
        print(query)
        db_connect.query_db_no_return(query)
