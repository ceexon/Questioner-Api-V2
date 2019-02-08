"""  Validating user data """
import re
from flask import abort, jsonify, make_response
from app.api.v2.utils.base_vals import BaseValidation

EMAIL_REGEX = re.compile(r'(\w+[.|\w])*@(\w+[.])*\w+')


class UserValidation(BaseValidation):
    """docstring for  UserValidation"""
    signup_required = ["firstname", "lastname", "gender",
                       "phone", "email", "password", "username"]
    optional_field = ["othername"]
    unchangable = ["firstname", "lastname", "othername", "gender"]
    changable = ["phone", "email", "password", "username", "image"]

    def check_othername(self):
        try:
            other = self.data["othername"]

        except KeyError:
            pass

        if not other:
            return 0

        other = other.strip()
        if not other:
            other = ""
            return 0

        if not other.isalpha():
            abort(make_response(jsonify({
                "status": 422,
                "message": "other name can only be letters",
                "error": "invalid naming format"
            }),422))

        return other

    def accept_gender(self):
        gender = self.data["gender"].strip().lower()
        set_gender = ""
        if gender == "m" or gender == "male":
            set_gender = "M"
        elif gender == "f" or gender == "female":
            set_gender = "F"
        else:
            abort(make_response(jsonify({
                "error": "select a valid gender",
                "message": "Male(m) or Female(f)",
                "status": 422
            }), 422))
        return set_gender

    def validate_names(self):
        fname = self.data["firstname"].strip()
        lname = self.data["lastname"].strip()

        if not fname.isalpha() or not lname.isalpha():
            abort(make_response(jsonify({
                "status": 422,
                "message": "first and last name can only contain letters",
                "error": "invalid naming format"}), 422))

    def check_phone_length(self):
        phone = self.data["phone"].strip()
        if phone[0] == "+" and not len(phone) in range(11, 14):
            abort(make_response(
                jsonify({
                    "status": 422,
                    "message": "phone number length invalid(11-13)",
                    "error": "invalid phone number"}), 422))
        elif phone[0].isdigit() and phone.isdigit():
            if not len(phone) == 10:
                abort(make_response(
                    jsonify({
                        "status": 422,
                        "message": "phone number length invalid(10)",
                        "error": "invalid phone number"}), 422))

    def validate_phone(self):
        phone = self.data["phone"].strip()
        self.check_phone_length()
        if phone[0] == "+" and not phone[1:].isdigit():
            abort(make_response(jsonify({
                "status": 422,
                "message": "phone number can only be digits after '+'",
                "error": "invalid phone number"}), 422))
        elif (phone[0] == "+" and phone[1:].isdigit()) or phone.isdigit():
            phone = True
        elif not phone[0].isdigit() or not phone[0] == "+":
            abort(make_response(jsonify({
                "status": 422,
                "message": "phone number can start with '+' and have digits",
                "error": "invalid phone number"}),
                422))

    def valid_username(self):
        """ validates the username parsed """
        username = self.data["username"].strip()
        if re.search("[!@#$%^&*-/\\')(;\"`<>?:|}{~ ]", username):
            abort(make_response(
                jsonify({
                    "status": 422,
                    "error": "username can only be a letter, digit or _"}),
                422))

    def validate_password(self):
        pwd = phone = self.data["password"].strip()
        symbols = '$!#$@*'
        missing = []
        error = ""
        if len(pwd) < 6:
            error = "lentgh less than 6"
            missing.append(error)
        if not any(c.isdigit() for c in pwd):
            error = "no digits"
            missing.append(error)
        if not any(c.isupper() for c in pwd):
            error = "no uppercase letter"
            missing.append(error)
        if not any(c.islower() for c in pwd):
            error = "no lowercase letter"
            missing.append(error)
        if not any(c in symbols for c in pwd):
            error = "no symbol"
            missing.append(error)
        if missing:
            missing = ', '.join(missing)
            abort(make_response(jsonify({
                "status": 422, "error": "invalid password",
                "message": missing}), 422))

    def validate_email(self):
        email = phone = self.data["email"].strip()
        if not EMAIL_REGEX.match(email):
            abort(make_response(jsonify({
                "status": 422,
                "error": "invalid email format!! -> (example@mail.com)",
                "message": "bad email format"}),
                422))
