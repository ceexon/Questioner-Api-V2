"""" Main connection to the postgres database """
import psycopg2
from .db_connect import set_up_tables, create_admin, drop_table_if_exists


class DatabaseConnection:
    """ Handles the main connection to the database of the app setting """

    def __init__(self, db_url):
        """ initialize the class instance to take a database url as a parameter"""
        try:
            self.conn = psycopg2.connect(db_url)
        except Exception as error:
            print('Unable to connect to database:', error)
        self.cur = self.conn.cursor()

    def create_tables_and_admin(self):
        """ creates all tables """
        all_tables_to_create = set_up_tables()
        for query in all_tables_to_create:
            self.cur.execute(query)
            self.conn.commit()

        create_admin(self.conn)

    def drop_all_tables(self):
        """ Deletes all tables in the app """
        tables_to_drop = drop_table_if_exists()
        for query in tables_to_drop:
            self.cur.execute(query)
            self.conn.commit
        self.conn.close()

    def fetch_single_data_row(self, query):
        """ retreives a single row of data from a table """
        self.cur.execute(query)
        fetchedRow = self.cur.fetchone()
        return fetchedRow

    def save_incoming_data(self, query):
        """ saves data passed as a query to the stated table """
        self.cur.execute(query)
        self.conn.commit()

    def fetch_all_tables_rows(self, query):
        """ fetches all rows of data store """
        self.cur.execute(query)
        all_data_rows = self.cur.fetch_all
        return all_data_rows
