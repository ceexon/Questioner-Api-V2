import os
import sys
import datetime
import uuid
from flask import abort, make_response, jsonify
from werkzeug.security import generate_password_hash
import psycopg2


def connect_to_and_query_db(query=None, db_url=None):
    """ connecting and querying the db """
    conn = None
    cursor = None
    if db_url is None:
        db_url = os.getenv('DB_URL')
    try:
        conn = psycopg2.connect(db_url)
        # print("\n\nConnected {}\n".format(conn.get_dsn_parameters()))
        cursor = conn.cursor()
        if query:
            cursor.execute(query)
            conn.commit()
    except(Exception,
           psycopg2.DatabaseError,
           psycopg2.ProgrammingError) as error:
        print("DB ERROR: {}".format(error))
    return conn, cursor


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
          value VARCHAR(20) NOT NULL DEFAULT 0,
          comment_at TIMESTAMP);"""

    create_rsvp_table = """
          CREATE TABLE IF NOT EXISTS rsvp (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          value VARCHAR(20) NOT NULL,
          responded_at TIMESTAMP);"""

    create_votes_table = """
          CREATE TABLE IF NOT EXISTS votes (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          question_id INTEGER NOT NULL,
          voted_at TIMESTAMP);"""

    return [create_comment_table, create_meetups_table, create_questions_table, create_rsvp_table, create_users_table, create_votes_table]


def db_init(db_url=None):
    """
        Initialize db connection
    """
    try:
        conn, cursor = connect_to_and_query_db()
        all_init_queries = drop_table_if_exists() + set_up_tables()
        i = 0
        while i != len(all_init_queries):
            query = all_init_queries[i]
            cursor.execute(query)
            conn.commit()
            i += 1
        print("--"*50)
        conn.close()

    except Exception as error:
        print("\nQuery not executed : {} \n".format(error))


def query_db_no_return(query):
    try:
        conn = connect_to_and_query_db(query)[0]
        conn.close()
    except psycopg2.Error as error:
        print(error)
        sys.exit(1)


def select_from_db(query):
    rows = None
    conn, cursor = connect_to_and_query_db(query)
    if conn:
        rows = cursor.fetchall()
        conn.close()

    return rows


if __name__ == '__main__':
    db_init()
    connect_to_and_query_db()
