from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup
from ..models.user import User
from ..models.question import Question, Voting
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
        return jsonify({"status": 400, "message": "no data was found", "error": error}), 400
    valid_que = QuestionValid(que_data)
    valid_que.check_missing_fields(valid_que.question_required)
    valid_que.check_field_values_no_whitespace(valid_que.question_required)
    meet_id = que_data["meetup"]
    body = que_data["body"]
    meet_id = QuestionValid.confirm_ids(meet_id)
    meetup = Meetup.get_meetup(meet_id, "id")
    if not meetup:
        return jsonify({"status": 404, "error": "Mettup with id {} not found".format(meet_id)}), 404
    exists = Question.get_by_(meetup[0], "meetup_id")
    if (meet_id, body) == exists:
        return jsonify({"status": 403, "error": "A similar question already exists"}), 403
    meetup = meetup[0]
    user_id = logged_user[0]
    quest_title = que_data["title"]
    quest_body = que_data["body"]
    new_question = Question(user_id, meetup, quest_title, quest_body)
    new_question.post_a_question()
    return jsonify({"status": 201, "message": "question asked succssfully", "data": {
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
    if voted and voted[0] == question_id:
        abort(make_response(
            jsonify({"status": 403, "error": "You have already voted, try updating"}), 403))
    question = Voting.get_from_questions(question_id)
    meetup = question[2]
    title = question[3]
    body = question[4]
    downvote = downvote
    upvote = upvote
    user_id = user_id
    all_init_votes = Voting.get_initial_vote_count(question_id)
    print(all_init_votes)
    if all_init_votes:
        all_init_votes = all_init_votes[0]
    else:
        all_init_votes = all_init_votes
    new_vote = Voting(user_id, meetup, question_id,
                      upvote, downvote, all_init_votes)
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
        "votes": str(upvoted[3]) + " + 1"
    }}), 201


@q_blue.route('/questions/<quiz_id>/downvote', methods=["PATCH"])
@token_required
def downvote_question(current_user, quiz_id):
    downvoted = voting_action(current_user, quiz_id, 0, 1)
    return jsonify({"status": 201, "data": {
        "meetup": downvoted[0],
        "title": downvoted[1],
        "body": downvoted[2],
        "votes": str(downvoted[3]) + " - 1"
    }}), 201
