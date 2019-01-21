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

class Rsvp(Meetup):
    def __init__(self, user_id, meet_id, meet_topic, rsvp_status):
        self.user = user_id
        self.meet = meet_id
        self.topic = meet_topic
        self.status = rsvp_status
        self.responded_at = datetime.datetime.utcnow()

    def save_rsvp(self):
        query = """
            INSERT INTO rsvp(user_id,meetup_id,meetup_topic,value,responded_at)
            values('{}','{}','{}','{}','{}')
        """.format(self.user, self.meet, self.topic, self.status, self.responded_at)
        cur.execute(query)
        conn.commit()

    def update_rsvp(self):
        pass

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
    def get_rsvp_by(meet_id, search_by):
        """ get a specific rsvp meetup using its id """
        query = """
        SELECT user_id FROM rsvp
        WHERE {} = '{}'""".format(search_by, meet_id)

        cur.execute(query)
        meetup = cur.fetchall()
        return meetup
