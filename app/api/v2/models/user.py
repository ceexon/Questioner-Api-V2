""" user models """
import datetime
import psycopg2
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app.api.v2.models.db_connect import connect_db

TIME_NOW = datetime.datetime.utcnow()

conn = connect_db()
cur = conn.cursor()


class User:
    """docstring for User"""

    def __init__(self, firstname=None, lastname=None, othername=None,
                 username=None, email=None, phone=None, password=None):

        self.fname = firstname
        self.lname = lastname
        self.other = othername
        self.uname = username
        self.email = email
        self.password = generate_password_hash(str(password))
        self.phone = phone
        self.publicId = str(uuid.uuid4())
        self.now = TIME_NOW

    def create_new_user(self):
        """ creates/adds a new user to the users table"""
        if not User.get_all_users():
            self.isAdmin = True
        query = """
			INSERT INTO users(firstname, lastname, othername, username, email, phone, password, publicId, register_date) VALUES(
			'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}')""".format(self.fname, self.lname, self.other, self.uname, self.email, self.phone, self.password, self.publicId, self.now)
        cur.execute(query)
        conn.commit()

    @staticmethod
    def get_all_users():
        query = """ SELECT * FROM users """
        all_users = cur.execute(query)
        all_users = cur.fetchall()
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
            "isAdmin": user_tuple[10],
            "register_date": user_tuple[9]
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
        cur.execute(query)
        conn.commit()

    def delete_user(self, p_id):
        query = """ DELETE FROM requests WHERE public_id='{}' """.format(p_id)
        cur.execute(query)
        conn.commit()

    @staticmethod
    def query_username(username):
        """
        Query the users store for a user
        """
        query = """
        SELECT id, username, email, password, isAdmin FROM users
        WHERE users.username = '{}'""".format(username)
        user = cur.execute(query)
        user = cur.fetchone()
        return user

    @staticmethod
    def query_email(email):
        """
        Query the users store for a user
        """
        query = """
        SELECT id, username, email, password, isAdmin FROM users
        WHERE users.email = '{}'""".format(email)
        the_user = cur.execute(query)
        the_user = cur.fetchone()
        return the_user
