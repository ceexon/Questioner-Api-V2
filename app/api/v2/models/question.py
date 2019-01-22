""" db question models """
import datetime
from app.api.v2.models.db_connect import connect_db

conn = connect_db()
cur = conn.cursor()


class Question:
    def __init__(self, user_id, meetup_id, quest_title, quest_body):
        self.user = user_id
        self.meeetup = meetup_id
        self.title = quest_title
        self.body = quest_body
        self.asked_at = datetime.datetime.utcnow()

    def post_a_question(self):
        query = """
        INSERT INTO questions(user_id,meetup_id,title,body,created_on)
        VALUES('{}','{}','{}','{}','{}')
        """.format(self.user, self.meeetup, self.title, self.body, self.asked_at)
        cur.execute(query)
        conn.commit()

    @staticmethod
    def get_by_(value, search_by):
        """ get a specific question using its <your choice> """
        query = """
        SELECT meetup_id,body FROM questions
        WHERE {} = '{}'""".format(search_by, value)

        cur.execute(query)
        meetup = cur.fetchall()
        return meetup
