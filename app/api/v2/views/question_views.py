import datetime
import timestring
from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup
from ..models.user import User
from ..models.question import Question, Voting, Comment
from ..utils.base_vals import BaseValidation, token_required
from ..utils.question_vals import QuestionValid

q_blue = Blueprint("que_bl", __name__)


@q_blue.route('/meetups/<meet_id>/questions', methods=["POST"])
@token_required
def ask_question(current_user, meet_id):
    logged_user = User.query_username(current_user)
    user_image = logged_user[-2]
    user_name = logged_user[1]
    try:
        que_data = request.get_json()

    except Exception as error:
        return jsonify({"status": 400,
                        "message": "no data was found", "error": error}), 400
    valid_que = QuestionValid(que_data)
    valid_que.check_missing_fields(valid_que.question_required)
    valid_que.check_field_values_no_whitespace(valid_que.question_required)
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
    exists = Question.get_by_(logged_user[0], "user_id", body)

    if exists:
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
                    },
                    "asker": {
                        "username": user_name,
                        "image": user_image
                    }}), 201


def voting_action(current_user, quiz_id, upvote, downvote):
    """ covers the etire voting process """
    logged_user = User.query_username(current_user)
    question_id = QuestionValid.confirm_ids(quiz_id)
    user_id = logged_user[0]
    question = Voting.get_from_questions(question_id)
    meetup = question[2]
    title = question[3]
    body = question[4]
    downvote = downvote
    upvote = upvote
    user_id = user_id
    print(user_id)

    if user_id == question[1]:
        abort(make_response(jsonify({
                            "status": 403,
                            "message": "you cannot vote on your question",
                            }), 403))

    voted_user = Voting.get_votes_by_user(logged_user[0], question_id)
    current_vote = (upvote, downvote)
    if current_vote in voted_user:
        abort(make_response(
            jsonify(
                {"status": 403,
                 "message": "you have already voted"}), 403))

    if not voted_user:
        vote_list = [user_id, meetup, question_id, upvote, downvote]
        new_vote = Voting(vote_list)
        new_vote.update_to_votes()

    else:
        all_upvotes = Voting.get_all_up_down_votes(question_id, "upvotes", 1)
        all_downvotes = Voting.get_all_up_down_votes(
            question_id, "downvotes", 1)
        current_votes = len(all_upvotes) - len(all_downvotes)
        if len(all_upvotes) > 0:
            first_upvoter = all_upvotes[0][1]
        if len(all_downvotes) > 0:
            first_downvoter = all_downvotes[0][1]
        if current_votes == 1 and user_id == first_upvoter:
            current_votes = current_votes - downvote - len(all_upvotes)
        elif current_votes == -1 and user_id == first_downvoter:
            current_votes = current_votes + len(all_downvotes) + upvote
        else:
            if upvote:
                current_votes = current_votes + upvote - \
                    len(all_upvotes) + len(all_downvotes)
            if downvote:
                current_votes = current_votes - downvote
        Voting.update_user_vote(user_id, question_id,
                                upvote, downvote)

    all_upvotes = len(Voting.get_all_up_down_votes(question_id, "upvotes", 1))
    all_downvotes = len(Voting.get_all_up_down_votes(
        question_id, "downvotes", 1))
    votes = all_upvotes - all_downvotes
    votes_data = [all_upvotes, all_downvotes, votes]
    return [meetup, title, body, votes_data]


@q_blue.route('/questions/<quiz_id>/upvote', methods=["PATCH"])
@token_required
def upvote_question(current_user, quiz_id):
    upvoted = voting_action(current_user, quiz_id, 1, 0)
    return jsonify({"status": 201, "data": {
        "meetup": upvoted[0],
        "title": upvoted[1],
        "body": upvoted[2]
    },
        "voting_stats": {
        "votes_data": {
            "upvotes": upvoted[3][0],
            "downvotes": upvoted[3][1],
            "voteDiff": upvoted[3][2]
        }
    }
    }), 201


@q_blue.route('/questions/<quiz_id>/downvote', methods=["PATCH"])
@token_required
def downvote_question(current_user, quiz_id):
    downvoted = voting_action(current_user, quiz_id, 0, 1)
    return jsonify({"status": 201, "data": {
        "meetup": downvoted[0],
        "title": downvoted[1],
        "body": downvoted[2]
    },
        "voting_stats": {
        "votes_data": {
            "upvotes": downvoted[3][0],
            "downvotes": downvoted[3][1],
            "voteDiff": downvoted[3][2]
        }
    }}), 201


@q_blue.route('/questions/<quiz_id>/comments', methods=["POST"])
@token_required
def comment_on_question(current_user, quiz_id):
    logged_user = User.query_username(current_user)
    try:
        user_comment = request.get_json()
        if not user_comment:
            abort(make_response(
                jsonify({
                    "status": 400,
                    "error": "Missing comment data"}), 400))
        validate = BaseValidation(user_comment)
        validate.check_missing_fields(["comment"])
        validate.check_field_values_no_whitespace(["comment"])
        comment = user_comment["comment"]
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
    current_user = User.query_by_id(user_id)
    user_data = {}
    user_data["username"] = current_user[0]
    user_data["image"] = current_user[1]
    questionId = question[0]
    title = question[3]
    body = question[4]
    new_commment = Comment([user_id, questionId, title, body, comment])
    new_commment.post_a_comment()
    return jsonify({"status": 201, "data": {
        "question": questionId,
        "title": title,
        "body": body,
        "comment": comment,
        "user": user_data
    }}), 201


@q_blue.route('/meetups/<meet_id>/questions', methods=["GET"])
def get_questions_for_one_meetup(meet_id):
    meet_id = BaseValidation.confirm_ids(meet_id)
    meetups = Meetup.get_all_meetups()
    current_meetup = {}
    for meetup in meetups:
        if meetup["id"] == meet_id:
            current_meetup = meetup
    all_meetup_questions = Question.get_all_by_meetup_id(meet_id)
    serialized_questions = []

    if not current_meetup:
        abort(make_response(jsonify({
            "status": 404,
            "error": "Meetup with id {} not found".format(meet_id)}), 404))
    if not all_meetup_questions:
        serialized_questions = ["NO questions asked yet"]
        return jsonify({
            "status": 404,
            "meetup": current_meetup,
            "questions": serialized_questions
        }), 404

    for index, question in enumerate(all_meetup_questions):
        current_question = {}
        current_question["id"] = question[0]
        all_upvotes = len(Voting.get_all_up_down_votes(
            question[0], "upvotes", 1))
        all_downvotes = len(Voting.get_all_up_down_votes(
            question[0], "downvotes", 1))
        comments = Comment.get_all_question_comments_number(question[0])
        current_question["user id"] = question[1]
        current_user = User.query_by_id(question[1])
        user_data = {}
        user_data["username"] = current_user[0]
        user_data["image"] = current_user[1]
        current_question["meetup id"] = question[2]
        current_question["title"] = question[3]
        current_question["body"] = question[4]
        current_question["asker"] = user_data
        current_question["votes"] = {
            "upvotes": all_upvotes,
            "downvotes": all_downvotes,
            "voteDiff": all_upvotes - all_downvotes
        }
        current_question["comments"] = comments
        serialized_questions.append(current_question)
    return jsonify({
        "status": 200,
        "meetup": current_meetup,
        "questions": serialized_questions
    }), 200


@q_blue.route('/questions/<quiz_id>/comments', methods=["GET"])
def get_all_comments_on_question(quiz_id):
    quiz_id = BaseValidation.confirm_ids(quiz_id)
    the_question = Question.fetch_all_if_exists(
        Question, 'comments', 'question_id', quiz_id)
    comments = Question.fetch_all_if_exists(
        Question, 'comments', 'question_id', quiz_id)
    the_question = Question.serialize_a_question(the_question)
    comments = Comment.serialize_a_comment(comments)
    for index,comment in enumerate(comments):
        print(index, "--------"*20,"\n",comment, "\n", "--------"*20)
        comment_user = list(User.query_by_id(comment["User"]))
        user_id = comment["User"]
        comment_user = {
            "id" : comment["User"],
            "username" : comment_user[0],
            "image" : comment_user[1]
        }
        comment["user"] = comment_user
        print(comment)

    return jsonify({
        "status": 200,
        "asked_question": the_question[0],
        "comments": comments
    }), 200
