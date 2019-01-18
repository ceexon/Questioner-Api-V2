""" db meetup models """
import datetime
from .db_connect import query_db_no_return, select_from_db
from app.api.v2.models import db_connect


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
            '{}', '{}', '{}', '{}', '{}', '{}'
        )""".format(self.topic, self.location, self.happen_on, self.tags, self.created_on, self.user_id)

        db_connect.query_db_no_return(query)

    @staticmethod
    def get_all_meetups():
        """
        gets all meetups
        """
        query = """
        SELECT * FROM meetups
        """
        meetups = db_connect.select_from_db(query)
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
    def get_meetup(meet_id):
        """ get a specific meetup using its id """
        query = """
        SELECT meetup_id, topic, happen_on, meetup_location FROM meetups
        WHERE meetups.meetup_id = '{}'""".format(meet_id)

        meetup = db_connect.select_from_db(query)
        meetup = Meetup.format_meet_info(meetup)
        return meetup

    @staticmethod
    def delete_meetup(meet_id):
        """ delete a specific meetup"""
        meetup = Meetup.get_meetup(meet_id)

        if meetup:
            query = """
            DELETE FROM meetups
            WHERE meetups.meetup_id = '{}'""".format(meet_id)

            db_connect.query_db_no_return(query)
            return True
        return False
