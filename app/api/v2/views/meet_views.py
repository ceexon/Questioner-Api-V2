from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup
from ..models.user import User
from ..utils.base_vals import BaseValidation, token_required
from ..utils.meet_validator import MeetValid

v_blue = Blueprint("ap1vv", __name__)


@v_blue.route("/meetups", methods=["POST"])
@token_required
def create_meetup(current_user):
    """create a meetup"""
    try:
        meetup_data = request.get_json()
        topic = meetup_data['topic']
        happen_on = meetup_data['happen_on']
        location = meetup_data['location']
        tags = ", ".join(meetup_data['tags'])

    except KeyError:
        return jsonify({
            'status': 404,
            'error': 'missing either (topic,happen_on,location or tags)'}), 404

    validate = BaseValidation(meetup_data)
    validate.check_field_values_no_whitespace(
        ["topic", "happen_on", "location"])

    if not tags:
        abort(make_response(jsonify({
            'status': 400,
            'error': 'tags field is required'}), 400))

    logged_user = User.query_username(current_user)
    print(logged_user)
    if not logged_user or not logged_user[-1]:
        return jsonify({"status": 401, "error": "you canot create a meetup"}), 401

    user_id = logged_user[0][0]
    meetup = Meetup(topic, location, happen_on, tags, user_id)
    meetup.save_meetup()

    return jsonify({"status": 201,
                    "data": [{"topic": topic,
                              "location": location,
                              "meetup_date": happen_on,
                              "tags": tags}]}), 201
