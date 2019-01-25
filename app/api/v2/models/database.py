"""" Main connection to the postgres database """
import psycopg2
from flask import abort, make_response, jsonify
from .db_connect import set_up_tables, create_admin, drop_table_if_exists


class DatabaseConnection:
    """ Handles the main connection to the database of the app setting """

    def __init__(self, db_url):
        """ initialize the class instance to take a database url as a parameter"""
        try:
            global conn, cur
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
        except Exception as error:
            print('Unable to connect to database:', error)

    def create_tables_and_admin(self):
        """ creates all tables """
        all_tables_to_create = set_up_tables()
        for query in all_tables_to_create:
            cur.execute(query)
            conn.commit()

        create_admin(conn)

    def drop_all_tables(self):
        """ Deletes all tables in the app """
        tables_to_drop = drop_table_if_exists()
        for query in tables_to_drop:
            cur.execute(query)
            conn.commit

    def fetch_single_data_row(self, query):
        """ retreives a single row of data from a table """
        cur.execute(query)
        fetchedRow = cur.fetchone()
        return fetchedRow

    def save_incoming_data_or_updates(self, query):
        """ saves data passed as a query to the stated table """
        cur.execute(query)
        conn.commit()

    def fetch_all_tables_rows(self, query):
        """ fetches all rows of data store """
        cur.execute(query)
        all_data_rows = cur.fetchall()
        return all_data_rows

    def fetch_all_if_exists(self, table_name, column_name, column_value):
        """ gets all details from a table with suggessted property """
        query = """
            SELECT * FROM {} where {} = '{}'
        """.format(table_name, column_name, column_value)
        cur.execute(query)
        result = cur.fetchall()
        if not result:
            abort(make_response(jsonify({
                "status": 404,
                "message": "{} with {} '{}' not found".format(
                    table_name[0:-1], column_name, column_value),
                "error": "data not found"})))
        return result
