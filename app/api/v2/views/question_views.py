from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup
from ..models.user import User
from ..models.question import Question
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
    if (meet_id, body) in exists:
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
    }})
