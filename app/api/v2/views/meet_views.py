from flask import Blueprint, request, jsonify, abort, make_response
from ..models.meetup import Meetup, Rsvp
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
    meetup = Meetup([topic, happen_on, location, tags, user_id])
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


@v_blue.route("/meetups/<m_id>", methods=["GET"])
def get_by_id(m_id):
    m_id = BaseValidation.confirm_ids(m_id)
    meetup = Meetup.get_meetup(m_id, "id")
    if meetup:
        meetup = Meetup.format_meet_info(meetup)
        return jsonify({"status": 200, "data": meetup}), 200
    return jsonify({"status": 404, "error": "Mettup with id {} not found".format(m_id)}), 404


@v_blue.route("/meetups/<m_id>/rsvp", methods=["POST"])
@token_required
def meetup_rsvp(current_user, m_id):
    logged_user = User.query_username(current_user)
    if not logged_user:
        return jsonify({"status": 401, "error": "unregistered user.Plase signin first"}), 401
    user_id = logged_user[0]

    try:
        status_info = request.get_json()
        status = status_info["status"]
    except (Exception, ValueError, KeyError):
        return jsonify({"status": 400, "error": "Rsvp info is Missing"}), 400
    meet_id = BaseValidation.confirm_ids(m_id)
    meetup = Meetup.get_meetup(meet_id, "id")
    if not meetup:
        return jsonify({"status": 404, "error": "Mettup with id {} not found".format(m_id)}), 404
    validate = BaseValidation(status_info)
    validate.check_missing_fields(["status"])
    validate.check_field_values_no_whitespace(["status"])
    response = status.lower()
    if response == "n" or response == "no":
        response = "NO"
    elif response == "yes" or response == "y":
        response = "YES"
    elif response == "maybe":
        response = "MAYBE"
    else:
        return jsonify({"status": 400, "error": "invalid choice. Status response is limited to 'yes/maybe/no'"}), 400
    rsvped = Rsvp.get_rsvp_by(meet_id, "meetup_id")
    if (user_id,) in rsvped:
        return jsonify({"status": 403, "error": "RSVP is only once, try updating status"}), 403
    meetup = Meetup.format_meet_info(meetup)
    topic = meetup["topic"]
    rsvp = Rsvp([user_id, meet_id, topic, status])
    rsvp.save_rsvp()
    return jsonify({"status": 201, "message": "response received", "data": {
        "meetup": meet_id,
        "topic": topic,
        "status": response
    }}), 201


@v_blue.route("/meetups/<m_id>", methods=["DELETE"])
@token_required
def delete_by_id(current_user, m_id):
    logged_user = User.query_username(current_user)
    adminStatus = logged_user[-1]
    if not adminStatus:
        return jsonify({"status": 403, "error": "you canot delete a meetup"}), 403
    meet_id = BaseValidation.confirm_ids(m_id)
    meetup = Meetup.delete_meetup(meet_id)
    if meetup:
        return jsonify({"status": 200, "message": "meetup deleted successfully"}), 200
    return jsonify({"status": 404, "error": "Mettup with id {} not found".format(m_id)}), 404
