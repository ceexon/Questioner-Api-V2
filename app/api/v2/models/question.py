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
        """.format(self.user, self.meeetup, self.title,
                   self.body, self.asked_at)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def serialize_a_question(question_list):
        serial_question = {}
        serial_question_list = []
        for question in question_list:
            if question:
                serial_question["Id"] = question[0]
                serial_question["User"] = question[1]
                serial_question["Meetup"] = question[2]
                serial_question["Quiz Title"] = question[3]
                serial_question["Quiz Body"] = question[4]
                serial_question["Asked on"] = question[5]
                serial_question_list.append(serial_question)

        return serial_question_list

    @staticmethod
    def get_by_(value, search_by, question_body):
        """ get a specific question using its <your choice> """
        query = """
        SELECT meetup_id,body FROM questions
        WHERE {} = '{}' AND body = '{}'
        """.format(search_by, value, question_body)
        question = db_conn.fetch_single_data_row(db_conn, query)
        return question

    @staticmethod
    def get_all_by_meetup_id(value):
        """ get all questions from a specific meetup """
        query = """
        SELECT * FROM questions
        WHERE meetup_id = '{}'""".format(value)
        meetups = db_conn.fetch_all_tables_rows(db_conn, query)
        return meetups


class Voting(db_conn):
    def __init__(self, voteCast):
        self.user = voteCast[0]
        self.meetup = voteCast[1]
        self.question = voteCast[2]
        self.upvote = voteCast[3]
        self.downvote = voteCast[4]
        self.voted_at = datetime.datetime.utcnow()

    def update_to_votes(self):
        query = """
        INSERT INTO votes (user_id, meetup_id, question_id,
         upvotes, downvotes, voted_at)
        VALUES('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(self.user, self.meetup, self.question, self.upvote,
                   self.downvote, self.voted_at)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def get_from_questions(quiz_id):
        """ get a specific question using its id """
        query = """
        SELECT * FROM questions
        WHERE id = '{}'""".format(quiz_id)
        question = db_conn.fetch_single_data_row(db_conn, query)
        return question

    @staticmethod
    def get_votes_by_user(user_id, question_id):
        """ get a specific question using user id voted-user """
        query = """
        SELECT upvotes,downvotes FROM votes
        WHERE user_id='{}' AND question_id='{}'""".format(user_id, question_id)
        user_vote = db_conn.fetch_all_tables_rows(db_conn, query)
        return user_vote

    @staticmethod
    def update_user_vote(user_id, question_id, upvote, downvote):
        """ Update vote """
        query = """
            UPDATE 
            votes SET 
            upvotes='{}',
            downvotes='{}'
            WHERE user_id='{}' and question_id='{}'
        """.format(upvote, downvote, user_id, question_id)
        db_conn.save_incoming_data_or_updates(db_conn, query)

    @staticmethod
    def get_all_up_down_votes(question_id, fetch_by, vote_value):
        """ pick all upvotes or downvotes from a question """
        query = """
        SELECT * from votes WHERE question_id = {} AND {}='{}'
        """.format(question_id, fetch_by, vote_value)
        votes = db_conn.fetch_all_tables_rows(db_conn, query)
        return votes


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
        INSERT INTO comments(user_id, question_id, question_title, 
        question_body, comment, comment_at)
        VALUES('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(self.user, self.question, self.title, self.body,
                   self.comment, self.comment_at)
        self.save_incoming_data_or_updates(query)

    @staticmethod
    def serialize_a_comment(comment_list):
        serial_comment = {}
        serial_comment_list = []
        for comment in comment_list:
            if comment:
                serial_comment["Id"] = comment[0]
                serial_comment["User"] = comment[1]
                serial_comment["Question"] = comment[2]
                serial_comment["Quiz Title"] = comment[3]
                serial_comment["Quiz Body"] = comment[4]
                serial_comment["comment"] = comment[5]
                serial_comment["comment at"] = comment[6]
                serial_comment_list.append(serial_comment)

        return serial_comment_list
