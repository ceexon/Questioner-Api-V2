""" db question models """
import datetime
from app.api.v2.models.database import DatabaseConnection as db_conn


class Question(db_conn):
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
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def get_by_(value, search_by):
        """ get a specific question using its <your choice> """
        query = """
        SELECT meetup_id,body FROM questions
        WHERE {} = '{}'""".format(search_by, value)
        meetup = db_conn.fetch_single_data_row(db_conn, query)
        return meetup


class Voting(db_conn):
    def __init__(self, user_id, meetup_id, question_id, upvote, downvote, init_votes):
        self.user = user_id
        self.meetup = meetup_id
        self.question = question_id
        self.upvote = upvote
        self.downvote = downvote
        self.votes = init_votes + upvote - downvote
        self.voted_at = datetime.datetime.utcnow()

    def update_to_votes(self):
        query = """
        INSERT INTO votes (user_id, meetup_id, question_id, upvotes, downvotes, votes, voted_at)
        VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')
        """.format(self.user, self.meetup, self.question, self.upvote, self.downvote, self.votes, self.voted_at)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def get_initial_vote_count(question_id):
        """ get votes to a given question """
        query = """
        SELECT votes FROM votes
        WHERE question_id = '{}'""".format(question_id)
        all_voted_user_count = db_conn.fetch_all_tables_rows(db_conn, query)
        if all_voted_user_count:
            return all_voted_user_count[-1]
        else:
            return 0

    @staticmethod
    def get_from_questions(que_id):
        """ get a specific question using its id """
        query = """
        SELECT * FROM questions
        WHERE id = '{}'""".format(que_id)
        question = db_conn.fetch_single_data_row(db_conn, query)
        return question

    @staticmethod
    def get_a_voted_user_(user_id):
        """ get a specific question using user id voted-user """
        query = """
        SELECT question_id FROM votes
        WHERE user_id = '{}'""".format(user_id)
        questionId = db_conn.fetch_single_data_row(db_conn, query)
        return questionId
