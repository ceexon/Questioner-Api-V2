import psycopg2
from flask import abort, make_response, jsonify
from app.api.v2.utils.base_vals import BaseValidation
from ..models.meetup import Meetup


class MeetValid(BaseValidation):
    """ validating meetup data """
    required_meetup = ["topic", "location", "happen_on", ""]

    @staticmethod
    def prevent_duplication(meetup):
        happen_on = meetup["happen_on"]
        existing = Meetup.get_all_meetups()
        if not existing:
            pass
        for meet in existing:
            if meet["location"] == meetup["location"] and meet["happen_on"] == happen_on:
                abort(make_response(jsonify({"status": "409",
                                             "error": "You may be trying to duplicate a meetup, one with same time and location exists"}), 409))
        pass
