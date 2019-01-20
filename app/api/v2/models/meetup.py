""" db meetup models """
import datetime
from app.api.v2.models.db_connect import connect_db

conn = connect_db()
cur = conn.cursor()


class Meetup:
    """ manipulating meetup data """

    def __init__(self, topic, location, happen_on, tags, user_id):
        """ meetup variables mains """
        self.topic = topic
        self.happen_on = happen_on
        self.location = location
        self.tags = tags
        self.user_id = user_id
        self.created_on = datetime.datetime.now()

    def save_meetup(self):
        """
        saves new meetup to store
        """
        query = """
        INSERT INTO meetups(topic, location, happen_on, tags, created_on, user_id) VALUES(
            '{}', '{}', '{}', ARRAY{}, '{}', '{}'
        )""".format(self.topic, self.location, self.happen_on, self.tags, self.created_on, self.user_id)
        cur.execute(query)
        conn.commit()

    @staticmethod
    def get_all_meetups():
        """
        gets all meetups
        """
        query = """
        SELECT * FROM meetups
        """
        cur.execute(query)
        meetups = cur.fetchall()
        data = []
        for meet in meetups:
            meetup = Meetup.format_meet_info(meet)
            data.append(meetup)
        return data

    @staticmethod
    def format_meet_info(meet_tuple):
        a_meet = {
            "id": meet_tuple[0],
            "user_id": meet_tuple[1],
            "topic": meet_tuple[2],
            "location": meet_tuple[3],
            "happen_on": meet_tuple[4],
            "tags": meet_tuple[5],
            "created_on": meet_tuple[6]
        }

        return a_meet

    @staticmethod
    def get_meetup(meet_id, serach_by):
        """ get a specific meetup using its id """
        query = """
        SELECT * FROM meetups
        WHERE {} = '{}'""".format(serach_by, meet_id)

        cur.execute(query)
        meetup = cur.fetchone()
        return meetup

    @staticmethod
    def delete_meetup(meet_id):
        """ delete a specific meetup"""
        meetup = Meetup.get_meetup(meet_id, "id")

        if meetup:
            query = """
            DELETE FROM meetups
            WHERE meetups.id = '{}'""".format(meet_id)

            cur.execute(query)
            conn.commit()
            return True
        return False
