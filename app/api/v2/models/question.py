""" db question models """
import datetime
from app.api.v2.models.database import DatabaseConnection as db_conn


class Question(db_conn):
    def __init__(self, theQuestion):
        self.user = theQuestion[0]
        self.meeetup = theQuestion[1]
        self.title = theQuestion[2]
        self.body = theQuestion[3]
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
    def __init__(self, voteCast):
        self.user = voteCast[0]
        self.meetup = voteCast[1]
        self.question = voteCast[2]
        self.upvote = voteCast[3]
        self.downvote = voteCast[4]
        self.votes = voteCast[5] + self.upvote - self.downvote
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
    def get_from_questions(quiz_id):
        """ get a specific question using its id """
        query = """
        SELECT * FROM questions
        WHERE id = '{}'""".format(quiz_id)
        print(query)
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


class Comment(db_conn):
    def __init__(self, newComment):
        self.user = newComment[0]
        self.question = newComment[1]
        self.title = newComment[2]
        self.body = newComment[3]
        self.comment = newComment[4]
        self.comment_at = datetime.datetime.utcnow()

    def post_a_comment(self):
        query = """
        INSERT INTO comments (user_id, question_id, question_title, question_body, comment, comment_at)
        VALUES('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(self.user, self.question, self.title, self.body, self.comment, self.comment_at)
        self.save_incoming_data_or_updates(query)
