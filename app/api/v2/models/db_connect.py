import os
import sys
import datetime
import uuid
from flask import abort, make_response, jsonify
from werkzeug.security import generate_password_hash
import psycopg2
from instance.config import app_config

db_config_name = os.getenv("APP_SETTING")
config = app_config[db_config_name]


def connect_db():
    """ Function to initialize db connection """
    db_url = config.Database_Url
    DSN = db_url
    try:
        conn = psycopg2.connect(DSN)

    except Exception as error:
        print('Unable to connect to database:', error)
        sys.exit(1)
    return conn


def drop_table_if_exists():
    """ Removes all tables on app start so as to start working with no data """
    drop_users = """ DROP TABLE IF EXISTS users """
    drop_meetups = """ DROP TABLE IF EXISTS meetups """
    drop_questions = """ DROP TABLE IF EXISTS questions """
    drop_comments = """ DROP TABLE IF EXISTS comments """
    drop_rsvp = """ DROP TABLE IF EXISTS rsvp """
    drop_votes = """ DROP TABLE IF EXISTS votes """

    return [drop_votes, drop_rsvp, drop_comments, drop_meetups, drop_questions, drop_users]


def set_up_tables():
    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
        id serial PRIMARY KEY,
        firstname VARCHAR(30) NOT NULL,
        lastname VARCHAR(30) NOT NULL,
        othername VARCHAR(30),
        username VARCHAR(40) NOT NULL UNIQUE,
        email VARCHAR(60) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL,
        password VARCHAR(200) NOT NULL,
        publicId VARCHAR(50) NOT NULL,
        register_date TIMESTAMP,
        isAdmin BOOLEAN DEFAULT False);"""

    create_meetups_table = """
          CREATE TABLE IF NOT EXISTS meetups (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          topic VARCHAR(100) NOT NULL,
          location VARCHAR(200) NOT NULL,
          happen_on VARCHAR(20) NOT NULL,
          tags VARCHAR(200) NOT NULL,
          created_on TIMESTAMP);"""

    create_questions_table = """
          CREATE TABLE IF NOT EXISTS questions (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          title VARCHAR(100) NOT NULL,
          body VARCHAR(200) NOT NULL,
          created_on TIMESTAMP);"""

    create_comment_table = """
          CREATE TABLE IF NOT EXISTS comments (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          question_id INTEGER NOT NULL,
          question_title Varchar(100),
          question_body Varchar(200),
          comment VARCHAR(300) NOT NULL,
          comment_at TIMESTAMP);"""

    create_rsvp_table = """
          CREATE TABLE IF NOT EXISTS rsvp (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          meetup_topic Varchar(200) NOT NULL,
          value VARCHAR(20) NOT NULL,
          responded_at TIMESTAMP);"""

    create_votes_table = """
          CREATE TABLE IF NOT EXISTS votes (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          question_id INTEGER NOT NULL,
          upvotes INTEGER NOT NULL DEFAULT 0,
          downvotes INTEGER NOT NULL DEFAULT 0,
          votes INTEGER NOT NULL DEFAULT 0,
          voted_at TIMESTAMP);"""
    return [create_comment_table, create_meetups_table, create_questions_table, create_rsvp_table, create_users_table, create_votes_table]


def create_admin(connect):
    query = """
    INSERT INTO users(firstname, lastname, othername, username, email, phone, password, publicId, register_date, isAdmin) VALUES('{}','{}','{}','admin','admin@admin.dns','0791000000','{}','{}','{}',True)""".format('admin', 'super', 'admin', generate_password_hash("$$PAss12"), str(uuid.uuid4()), datetime.datetime.utcnow())
    get_admin = """SELECT * from users WHERE username = 'admin'"""
    cur = connect.cursor()
    get_admin = cur.execute(get_admin)
    get_admin = cur.fetchone()
    if get_admin:
        return 0
    cur.execute(query)
    connect.commit()

def delete_dummy_user(connect):
    query = """
        DELETE FROM users WHERE username = 'toovor';
        DELETE FROM meetups WHERE topic = 'Formless';
    """
    cur = connect.cursor()
    cur.execute(query)
    connect.commit()


def db_init(connect):
    """
        Initialize db connection
    """
    cur = connect.cursor()
    for table in set_up_tables():
        cur.execute(table)
    connect.commit()


def drop_tables(connect):
    queries = drop_table_if_exists()
    cur = connect.cursor()
    for query in queries:
        cur.execute(query)
    connect.commit()
