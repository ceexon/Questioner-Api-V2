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
    logged_user = User.query_username(current_user)
    adminStatus = logged_user[-1]
    if not adminStatus:
        return jsonify({"status": 403, "error": "you cannot create a meetup"}), 403

    try:
        meetup_data = request.get_json()
        topic = meetup_data['topic']
        happen_on = meetup_data['happen_on']
        location = meetup_data['location']
        tags = meetup_data['tags']

    except KeyError:
        return jsonify({
            'status': 400,
            'error': 'missing either (topic,happen_on,location or tags)'}), 400

    validate = BaseValidation(meetup_data)
    validate.check_field_values_no_whitespace(
        ["topic", "happen_on", "location"])

    if not tags:
        abort(make_response(jsonify({
            'status': 400,
            'error': 'tags field is required'}), 400))

    MeetValid.prevent_duplication(meetup_data)
    user_id = logged_user[0]
    meetup = Meetup(topic, location, happen_on, tags, user_id)
    meetup.save_meetup()

    return jsonify({"status": 201,
                    "data": [{"topic": topic,
                              "location": location,
                              "meetup_date": happen_on,
                              "tags": tags}]}), 201

@v_blue.route("/meetups", methods=["GET"])
@token_required
def get_all_meets_admin(current_user):
    """ Fetches all meetups """
    logged_user = User.query_username(current_user)
    adminStatus = logged_user[-1]
    if not adminStatus:
        return jsonify({"status": 403, "error": "you canot access the meetups"}), 403
    meetups = Meetup.get_all_meetups()
    if not meetups:
        abort(make_response(jsonify({
            "status": 404,
            "data": "no meetups scheduled yet"
        }), 404))
    return jsonify({"status": 200, "data": meetups}), 200


@v_blue.route("/meetups/upcoming", methods=["GET"])
def get_all_upcoming():
    """ Fetches all meetups """
    meetups = Meetup.get_all_meetups()
    if not meetups:
        abort(make_response(jsonify({
            "status": 404,
            "data": "no meetups scheduled yet"
        }), 404))
    return jsonify({"status": 200, "data": meetups}), 200
