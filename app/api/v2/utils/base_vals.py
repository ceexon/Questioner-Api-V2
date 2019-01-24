""" Thos are unversal actions for modesls """
import os
import re
from functools import wraps
import jwt
from flask import jsonify, abort, make_response, request
from ..models import db_connect
from ..models.user import LogoutBlacklist

KEY = os.getenv("SECRET")


class BaseValidation:
    """  validation for all data collected as raw json """

    def __init__(self, data):
        self.data = data

    @staticmethod
    def confirm_ids(an_id):
        try:
            to_int = int(an_id)
            return to_int
        except (TypeError, ValueError):
            abort(make_response(
                jsonify({"status": 400, "error": "invalid id, use integer"}), 400))

    def check_missing_fields(self, required_fields):
        missing = []
        available = [key for key in self.data.keys()]
        for key in required_fields:
            if key not in available:
                missing.append(key)

        if missing:
            missing = ", ".join(missing)
            abort(make_response(
                jsonify({"status": 404, "error": missing+" field(s) not found"}), 404))

    def null_field_check(self, req_fields):
        empty = []
        for field in req_fields:
            if not self.data[field]:
                empty.append(field)
        if empty:
            empty = ", ".join(empty)
            abort(make_response(
                jsonify({"status": 422, "message": empty+" field(s) can't be empty"}), 422))

    def check_field_values_no_whitespace(self, req_fields):
        self.null_field_check(req_fields)
        white_space = []
        for field in req_fields:
            if not self.data[field].strip():
                white_space.append(field)
        if white_space:
            white_space = ", ".join(white_space)
            abort(make_response(jsonify({
                "status": 422,
                "message": white_space+" field(s) can't be white space only"}),
                422))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers['x-access-token']
            used_token = LogoutBlacklist.get_blacklisted(token)
            if used_token:
                abort(make_response(jsonify({
                    "status": 403,
                    "error": "Token has already been used",
                    "message": "please login again to continue"}), 403))
        else:
            abort(make_response(jsonify({"error": "Token is missing"}), 401))
        try:
            data = jwt.decode(token, KEY, algorithms="HS256")
            current_user = data["username"]

        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, TypeError):
            return jsonify({"error": "Token is invalid or expired"}), 401
        return f(current_user, *args, **kwargs)
    return decorated
