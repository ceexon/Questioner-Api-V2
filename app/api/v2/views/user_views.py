"""contains all endpoints for user functions such as signup and login """

import os
import datetime
import jwt
from flask import Blueprint, request, jsonify, abort, make_response
from werkzeug.security import check_password_hash
from ..utils.base_vals import BaseValidation, token_required
from ..utils.user_vals import UserValidation
from ..models.user import User, LogoutBlacklist
from ..models.meetup import Rsvp
from ..models.question import Question, Voting
v2_blue = Blueprint("ap1v2", __name__)
KEY = os.getenv("SECRET")


@v2_blue.route("/signup", methods=["POST"])
def user_signup():
    """endpoint for user to create account """
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
                     password, phone, gender])
    new_user.create_new_user()
    return jsonify({
        "status": 201, "message": "user created successfully"}), 201


@v2_blue.route("/login", methods=['POST'])
def user_login():
    """endpoint for users to sign in """
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
    if not check_password_hash(user_found[-3], password):
        return jsonify({"status": 401, "error": "incorrect password"}), 401

    admin_status = user_found[-1]
    user_id = user_found[0]
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
    token = jwt.encode(
        {"username": username, 'exp': exp}, KEY,
        algorithm='HS256')

    return jsonify({"status": 200, "message": "logged in successfully",
                    "token": token.decode("utf-8", KEY),
                    "isAdmin": admin_status,
                    "userId": user_id}), 200


def catch_key_error(dictionary, value):
    try:
        if dictionary[value]:
            pass
    except KeyError:
        pass


@v2_blue.route("/update/user/<user_id>", methods=["PATCH"])
@token_required
def update_user(current_user, user_id):
    logged_user = User.query_username(current_user)
    required_field = ["original_password"]
    try:
        original_password = request.get_json()
        original_password = original_password["original password"]
    except Exception:
        return jsonify({
            "status": 400,
            "error": "original password field is required"
            })
    print(logged_user)
    return jsonify({"user": logged_user})


@v2_blue.route("/logout", methods=["POST", "GET"])
@token_required
def user_logout(current_user):
    logout_token = request.headers["x-access-token"]
    logged_user = User.query_username(current_user)
    user_id = logged_user[0]
    leftPage = LogoutBlacklist(user_id, logout_token)
    leftPage.add_to_blacklist()
    return jsonify({"status": 200, "message": "logged out successfully"}), 200


@v2_blue.route("/user/info", methods=["GET"])
@token_required
def user_details(current_user):
    logged_user = User.query_username(current_user)
    image = logged_user[-2]
    user_questions = Question.get_all_questions("questions", "user_id", logged_user[0])
    user_questions = len(user_questions)

    user_comments = Question.get_all_questions("comments", "user_id", logged_user[0])
    user_comments = len(user_comments)

    meetups_ravp_yes = Rsvp.get_all_rsvp_by("YES", logged_user[0], "value")
    all_yes_rsvps = []
    for rsvp in meetups_ravp_yes:
        all_yes_rsvps.append(rsvp[1])
    rsvp_count = len(meetups_ravp_yes)
    top_feeds = []
    previous_meetups = []
    for metup_id in all_yes_rsvps:
        meetup_questions = Question.get_all_by_meetup_id(metup_id)
        if len(meetup_questions) > 0:
            question = {}
            question["id"] = meetup_questions[0][0]
            question["meetup"] = meetup_questions[0][2]
            question["title"] = meetup_questions[0][3]
            question["body"] = meetup_questions[0][4]
            top_feeds.append(question)

    return jsonify({
        "status": 200,
        "username": current_user,
        "image": image,
        "questions": user_questions,
        "comments": user_comments,
        "rsvps": rsvp_count,
        "topQuestions": top_feeds
        }), 200


@v2_blue.route("/users/all")
@token_required
def all_users(current_user):
    logged_user = User.query_username(current_user)
    adminStatus = logged_user[-1]
    if not adminStatus:
        return jsonify({
            "status": 403,
            "error": "you canot access the meetups"}), 403
    all_users = User.get_all_users()
    serialized_users = []
    for user in all_users:
        single_user = {}
        single_user["id"] = user[0]
        single_user["first name"] = user[1]
        single_user["last name"] = user[2]
        single_user["gender"] = user[4]
        single_user["username"] = user[6]
        single_user["email"] = user[7]
        single_user["phone"] = user[8]
        single_user["isAdmin"] = user[-1]
        serialized_users.append(single_user)
    return jsonify({"users": serialized_users})