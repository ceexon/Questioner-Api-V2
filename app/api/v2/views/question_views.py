import datetime
import timestring
from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup
from ..models.user import User
from ..models.question import Question, Voting, Comment
from ..utils.base_vals import BaseValidation, token_required
from ..utils.question_vals import QuestionValid

q_blue = Blueprint("que_bl", __name__)


@q_blue.route('/questions', methods=["POST"])
@token_required
def ask_question(current_user):
    logged_user = User.query_username(current_user)
    try:
        que_data = request.get_json()

    except TypeError as error:
        return jsonify({"status": 400,
                        "message": "no data was found", "error": error}), 400
    valid_que = QuestionValid(que_data)
    valid_que.check_missing_fields(valid_que.question_required)
    valid_que.check_field_values_no_whitespace(valid_que.question_required)
    meet_id = que_data["meetup"]
    body = que_data["body"]
    meet_id = QuestionValid.confirm_ids(meet_id)
    meetup = Meetup.get_meetup(meet_id, "id")
    if not meetup:
        return jsonify({
            "status": 404,
            "error": "Mettup with id {} not found".format(meet_id)}), 404
    meetup_date = meetup[4]
    if timestring.Date(meetup_date) < datetime.datetime.now():
        return jsonify({
            "status": 400,
            "error": "this meetup has already been conducted"
        })
    exists = Question.get_by_(meetup[0], "meetup_id")
    if (meet_id, body) == exists:
        return jsonify({
            "status": 403,
            "error": "A similar question already exists"}), 403
    meetup = meetup[0]
    user_id = logged_user[0]
    quest_title = que_data["title"]
    quest_body = que_data["body"]
    new_question = Question([user_id, meetup, quest_title, quest_body])
    new_question.post_a_question()
    return jsonify({"status": 201,
                    "message": "question asked succssfully",
                    "data": {
                        "user": user_id,
                        "meetup": meetup,
                        "title": quest_title,
                        "body": quest_body
                    }}), 201


def voting_action(current_user, quiz_id, upvote, downvote):
    """ covers the etire voting process """
    logged_user = User.query_username(current_user)
    question_id = QuestionValid.confirm_ids(quiz_id)
    user_id = logged_user[0]
    voted = Voting.get_a_voted_user_(user_id)
    print("\n\n\n\n\n", voted, "\n\n\n")
    if voted:
        for vote in voted:
            if vote[0] == question_id:
                abort(make_response(
                    jsonify({
                        "status": 403,
                        "error": "You have already voted, try updating"}),
                    403))
    question = Voting.get_from_questions(question_id)
    if not question:
        abort(make_response(jsonify({
            "status": 404,
            "error": "Question with id {} not found".format(quiz_id)}), 400))
    meetup = question[2]
    title = question[3]
    body = question[4]
    downvote = downvote
    upvote = upvote
    user_id = user_id
    action = ""
    if upvote:
        action = "upvotes"
    if downvote:
        action = "downvotes"
    all_init_votes = Voting.get_all_up_down_votes(action, question_id)
    count_votes = 0
    for vote in all_init_votes:
        if vote[0] == 1:
            count_votes += 1

    if all_init_votes:
        all_init_votes = count_votes
    else:
        all_init_votes = 0
    new_vote = Voting([user_id, meetup, question_id,
                       upvote, downvote, all_init_votes])
    new_vote.update_to_votes()
    return [meetup, title, body, all_init_votes]


@q_blue.route('/questions/<quiz_id>/upvote', methods=["PATCH"])
@token_required
def upvote_question(current_user, quiz_id):
    upvoted = voting_action(current_user, quiz_id, 1, 0)
    return jsonify({"status": 201, "data": {
        "meetup": upvoted[0],
        "title": upvoted[1],
        "body": upvoted[2],
        "upvotes": str(upvoted[3]+1)
    }}), 201


@q_blue.route('/questions/<quiz_id>/downvote', methods=["PATCH"])
@token_required
def downvote_question(current_user, quiz_id):
    downvoted = voting_action(current_user, quiz_id, 0, 1)
    return jsonify({"status": 201, "data": {
        "meetup": downvoted[0],
        "title": downvoted[1],
        "body": downvoted[2],
        "downvotes": str(downvoted[3]+1)
    }}), 201


@q_blue.route('/questions/<quiz_id>/comments', methods=["POST"])
@token_required
def comment_on_question(current_user, quiz_id):
    logged_user = User.query_username(current_user)
    try:
        userComment = request.get_json()
        if not userComment:
            abort(make_response(
                jsonify({
                    "status": 400,
                    "error": "Missing comment data"}), 400))
        validate = BaseValidation(userComment)
        validate.check_missing_fields(["comment"])
        validate.check_field_values_no_whitespace(["comment"])
        comment = userComment["comment"]
    except Exception:
        abort(make_response(
            jsonify({
                "status": 400, "error": "comment data is required"}), 400))
    question_id = QuestionValid.confirm_ids(quiz_id)
    question = Voting.get_from_questions(question_id)
    if not question:
        abort(make_response(jsonify({
            "status": 404,
            "error": "Question with id {} not found".format(quiz_id)}), 404))
    user_id = logged_user[0]
    questionId = question[0]
    title = question[3]
    body = question[4]
    new_commment = Comment([user_id, questionId, title, body, comment])
    new_commment.post_a_comment()
    return jsonify({"status": 201, "data": {
        "question": questionId,
        "title": title,
        "body": body,
        "comment": comment
    }}), 201


@q_blue.route('/meetups/<meet_id>/questions', methods=["GET"])
@token_required
def get_questions_for_one_meetup(current_user, meet_id):
    logged_user = User.query_username(current_user)
    meet_id = BaseValidation.confirm_ids(meet_id)
    meetups = Meetup.get_all_meetups()
    current_meetup = {}
    for meetup in meetups:
        if meetup["id"] == meet_id:
            current_meetup = meetup
    all_meetup_questions = Question.get_all_by_meetup_id(meet_id)
    print(current_meetup)
    serialized_questions = []
    current_question = {}

    if not current_meetup:
        abort(make_response(jsonify({
            "status": 404,
            "error": "Meetup with id {} not found".format(meet_id)}), 404))

    for question in all_meetup_questions:
        if question:
            current_question["id"] = question[0]
            current_question["user id"] = question[1]
            current_question["meetup id"] = question[2]
            current_question["title"] = question[3]
            current_question["body"] = question[4]
            serialized_questions.append(current_question)

    if not all_meetup_questions:
        serialized_questions = ["NO questions asked yet"]
        return jsonify({
            "status": 404,
            "meetup": current_meetup,
            "questions": serialized_questions
        }), 404

    return jsonify({
        "status": 200,
        "meetup": current_meetup,
        "questions": serialized_questions
    }), 200
