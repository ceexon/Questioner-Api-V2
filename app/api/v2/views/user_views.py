""" contains all endpoints for user functions such as signup and login """

import os
import datetime
import jwt
from flask import Blueprint, request, jsonify, abort, make_response
from werkzeug.security import check_password_hash
from ..utils.base_vals import BaseValidation, token_required
from ..utils.user_vals import UserValidation
from ..models.user import User, LogoutBlacklist
v2_blue = Blueprint("ap1v2", __name__)
KEY = os.getenv("SECRET")


@v2_blue.route("/signup", methods=["POST"])
def user_signup():
    """ endpoint for user to create account """
    try:
        user_data = request.get_json()
        if not user_data:
            raise ValueError("Missing signup data")
    except Exception:
        return jsonify({"status": 204, "error": "No data was given"}), 204
    valid_user = UserValidation(user_data)
    valid_user.check_missing_fields(valid_user.signup_required)
    firstname = user_data["firstname"].strip()
    lastname = user_data["lastname"].strip()
    othername = user_data["othername"].strip()
    phone = user_data["phone"].strip()
    email = user_data["email"].strip()
    username = user_data["username"].strip()
    password = user_data["password"].strip()
    username_taken = User.query_username(username)
    email_taken = User.query_email(email)
    if username_taken:
        return jsonify({
            "status": 409, "error": "user with username exists"}), 409
    if email_taken:
        return jsonify({
            "status": 409, "error": "user with email exists"}), 409
    valid_user.check_field_values_no_whitespace(valid_user.signup_required)
    valid_user.valid_username()
    valid_user.validate_email()
    valid_user.validate_password()
    valid_user.validate_phone()
    valid_user.validate_names()
    gender = valid_user.accept_gender()
    othername = valid_user.check_othername()
    new_user = User([firstname, lastname, othername, username, email,
                     password, phone])
    new_user.create_new_user()
    return jsonify({
        "status": 201, "message": "user created successfully"}), 201


@v2_blue.route("/login", methods=['POST'])
def user_login():
    """ endpoint for users to sign in """
    try:
        log_data = request.get_json()

    except Exception:
        return jsonify({
            "status": 417, "error": "Expecting Login data!!"}), 417

    valid_login = UserValidation(log_data)
    valid_login.check_missing_fields(["username", "password"])
    valid_login.check_field_values_no_whitespace(["username", "password"])
    username = log_data["username"]
    password = log_data["password"]
    user_found = User.query_username(username)
    if not user_found:
        return jsonify({"status": 401, "error": "unregistered username"}), 401
    if not check_password_hash(user_found[-2], password):
        return jsonify({"status": 401, "error": "incorrect password"}), 401

    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
    token = jwt.encode(
        {"username": username, 'exp': exp}, KEY,
        algorithm='HS256')

    return jsonify({"status": 200, "message": "logged in successfully",
                    "token": token.decode("utf-8", KEY)}), 200


def catch_key_error(dictionary, value):
    try:
        if dictionary[value]:
            pass
    except KeyError:
        pass


@v2_blue.route("/reset-profile", methods=["PATCH"])
@token_required
def reset_profile(current_user):
    try:
        date_to_update = request.get_json()
    except Exception:
        abort(make_response(jsonify({
            "status": 200,
            "message": "NO changes made"}), 200))

    valid_user = UserWarning(date_to_update)
    unchangable = valid_user.unchangable
    for value in unchangable:
        if date_to_update[value].strip():
            return jsonify({
                "status": 403,
                "error": "You cannot change " + value,
                "unchangable": "firstname, lastname,othername, gender"}, 403)

    # changable = valid_user.changable
    # for value in changable:
    #     catch_key_error()


@v2_blue.route("/logout", methods=["POST"])
@token_required
def user_logout(current_user):
    logout_token = request.headers["x-access-token"]
    logged_user = User.query_username(current_user)
    user_id = logged_user[0]
    leftPage = LogoutBlacklist(user_id, logout_token)
    leftPage.add_to_blacklist()
    return jsonify({"status": 200, "message": "logged out successfully"}), 200
