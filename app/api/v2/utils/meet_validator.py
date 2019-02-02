import datetime
import timestring
import psycopg2
from flask import abort, make_response, jsonify
from app.api.v2.utils.base_vals import BaseValidation
from ..models.meetup import Meetup


class MeetValid(BaseValidation):
    """ validating meetup data """
    required_meetup = ["topic", "location", "happen_on", "description"]

    def check_in_list(self, list_name, table_name):
        if len(list_name) == 1:
            if not list_name[0]:
                abort(make_response(jsonify({
                    "status": 400,
                    "error": "tags or image field is empty",
                    "message": "tags(#aTag) image(path url)"
                }), 422))

    def tags_and_image(self):
        if not self.data["tags"] or not self.data["image"]:
            abort(make_response(jsonify({
                "status": 400,
                "error": "tags or image field is empty",
                "message": "tags(#aTag) image(path url)"
            }), 422))

        self.check_in_list(self.data["tags"], "tags")
        self.check_in_list(self.data["image"], "image")

    @staticmethod
    def prevent_duplication(meetup):
        happen_on = meetup["happen_on"]
        existing = Meetup.get_all_meetups()
        if not existing:
            pass
        for meet in existing:
            if meet["location"] == meetup["location"] and meet["happen_on"] == happen_on:
                abort(make_response(jsonify({
                    "status": "409",
                    "error": "You may be trying to duplicate a meetup, one with same time and location exists"}),
                    409))

    @staticmethod
    def validate_meetup_date_input(date_string):
        """ Ensure date format is dd/mm/yyyy 1800"""
        try:
            input_date = timestring.Date(date_string)
        except Exception:
            abort(make_response(jsonify({
                "error": "invalid date format",
                "message": "use mm dd yyyy hr:min ",
                "status": 422}), 422))
        if input_date < datetime.datetime.now():
            abort(make_response(jsonify({
                "status": 422,
                "error": "Invalid date",
                "message": "enter a later date"
            })))

        return date_string
