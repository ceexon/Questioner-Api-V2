""" user models """
import datetime
import psycopg2
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from.database import DatabaseConnection as db_conn

TIME_NOW = datetime.datetime.utcnow()


class User(db_conn):
    """docstring for User"""

    def __init__(self, userData, isAdmin=False):

        self.fname = userData[0]
        self.lname = userData[1]
        self.other = userData[2]
        self.uname = userData[3]
        self.email = userData[4]
        self.password = generate_password_hash(str(userData[5]))
        self.phone = userData[6]
        self.gender = userData[7]
        self.image = "url"
        self.publicId = str(uuid.uuid4())
        self.now = TIME_NOW
        self.isAdmin = isAdmin

    def create_new_user(self):
        """ creates/adds a new user to the users table"""
        query = """
        INSERT INTO users(firstname, lastname, othername, gender, image,
        username, email, phone, password, publicId,
        register_date) VALUES(
        '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}')
        """.format(self.fname, self.lname, self.other, self.gender,
                   self.image, self.uname,
                   self.email, self.phone, self.password,
                   self.publicId, self.now)
        self.save_incoming_data_or_updates(query)

    def get_all_users(self):
        query = """ SELECT * FROM users """
        all_users = self.fetch_all_tables_rows(query)
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
        """.format(self.fname, self.lname, self.other, self.uname,
                   self.email, self.password,
                   self.phone, self.isAdmin, user_id)
        self.save_incoming_data_or_updates(query)

    def delete_user(self, p_id):
        query = """ DELETE FROM requests WHERE public_id='{}' """.format(p_id)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def query_username(username):
        """
        Query the users store for a user
        """
        query = """
        SELECT id, username, email, password, isAdmin FROM users
        WHERE users.username = '{}'""".format(username)
        user = db_conn.fetch_single_data_row(
            db_conn, query)
        return user

    @staticmethod
    def query_email(email):
        """
        Query the users store for a user
        """
        query = """
        SELECT id, username, email, password, isAdmin FROM users
        WHERE users.email = '{}'""".format(email)
        the_user = db_conn.fetch_single_data_row(
            db_conn, query)
        return the_user


class LogoutBlacklist(db_conn):
    def __init__(self, user_id, token):
        self.user = user_id
        self.token = token

    def add_to_blacklist(self):
        query = """
        INSERT INTO blacklists(user_id, token)
        VALUES('{}','{}')""".format(self.user, self.token)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def get_blacklisted(token):
        query = """
        select * from blacklists where token = '{}'
        """.format(token)
        is_black = db_conn.fetch_single_data_row(db_conn, query)
        return is_black
