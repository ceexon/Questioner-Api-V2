""" db meetup models """
import datetime
import json
from app.api.v2.models.database import DatabaseConnection as db_conn


class Meetup(db_conn):
    """ manipulating meetup data """

    def __init__(self, theMeetup):
        """ meetup variables mains """
        self.topic = theMeetup[0]
        self.happen_on = theMeetup[1]
        self.location = theMeetup[2]
        self.tags = json.dumps(theMeetup[3])
        self.user_id = theMeetup[4]
        self.image = json.dumps(theMeetup[5])
        self.desc = theMeetup[6]
        self.created_on = datetime.datetime.now()

    def save_meetup(self):
        """
        saves new meetup to store
        """
        query = """
        INSERT INTO meetups(topic, location, happen_on, tags, created_on,
         user_id, image, description) VALUES(
            '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}'
        )""".format(self.topic, self.location, self.happen_on,
                    self.tags, self.created_on, self.user_id, self.image,
                    self.desc)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def get_all_meetups():
        """
        gets all meetups
        """
        query = """
        SELECT * FROM meetups
        """

        meetups = db_conn.fetch_all_tables_rows(db_conn, query)
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
            "tags": json.loads(meet_tuple[5]),
            "description": meet_tuple[6],
            "image": json.loads(meet_tuple[7]),
            "created_on": meet_tuple[8]
        }

        return a_meet

    @staticmethod
    def get_meetup(meet_id, serach_by):
        """ get a specific meetup using its id """
        query = """
        SELECT * FROM meetups
        WHERE {} = '{}'""".format(serach_by, meet_id)

        meetup = db_conn.fetch_single_data_row(db_conn, query)
        return meetup

    @staticmethod
    def delete_meetup(meet_id):
        """ delete a specific meetup"""
        meetup = Meetup.get_meetup(meet_id, "id")

        if meetup:
            query = """
            DELETE FROM meetups
            WHERE meetups.id = '{}'""".format(meet_id)
            db_conn.save_incoming_data_or_updates(db_conn, query)
            return True
        return False


class Rsvp(Meetup):
    def __init__(self, rsvpToPost):
        self.user = rsvpToPost[0]
        self.meet = rsvpToPost[1]
        self.topic = rsvpToPost[2]
        self.status = rsvpToPost[3]
        self.responded_at = datetime.datetime.utcnow()

    @staticmethod
    def get_rsvps_count(value, meetup_id):
        """ get rsvps to specific meetup by value """
        print("rsvps out")
        query = """
            SELECT * FROM rsvp WHERE meetup_id = '{}' AND value = '{}'
        """.format(meetup_id, value)
        print(query)
        rsvps = db_conn.fetch_all_tables_rows(db_conn, query)
        print("rsvps result")
        rsvp_count = len(rsvps)
        return rsvp_count

    def save_rsvp(self):
        query = """
            INSERT INTO rsvp(user_id,meetup_id,meetup_topic,value,responded_at)
            values('{}','{}','{}','{}','{}')
        """.format(self.user, self.meet, self.topic, self.status,
                   self.responded_at)
        self.save_incoming_data_or_updates(query)

    def format_rsvp(self, rsvp_tuple):
        rsvp = {
            "id": rsvp_tuple[0],
            "user_id": rsvp_tuple[1],
            "meetup_id": rsvp_tuple[2],
            "topic": rsvp_tuple[3],
            "status": rsvp_tuple[4],
            "responded_at": rsvp_tuple[5]
        }
        return rsvp

    @staticmethod
    def get_rsvp_by(meet_id, user_id, search_by):
        """ get a specific rsvp meetup using its id """
        query = """
        SELECT user_id,meetup_id,value FROM rsvp
        WHERE {} = '{}' AND user_id = '{}'""".format(search_by, meet_id,
                                                     user_id)

        meetup = db_conn.fetch_single_data_row(db_conn, query)
        return meetup

    @staticmethod
    def update_rsvp_value(user_id, meet_id, value):
        """ update user rsvp value """
        query = """
        UPDATE rsvp SET value = '{}' WHERE user_id = '{}' AND meetup_id = '{}'
        """.format(value, user_id, meet_id)
        db_conn.save_incoming_data_or_updates(db_conn, query)
