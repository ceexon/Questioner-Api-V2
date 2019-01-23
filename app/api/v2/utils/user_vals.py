"""  Validating user data """
import re
from flask import abort, jsonify, make_response
from app.api.v2.utils.base_vals import BaseValidation

EMAIL_REGEX = re.compile(r'(\w+[.|\w])*@(\w+[.])*\w+')


class UserValidation(BaseValidation):
    """docstring for  UserValidation"""
    signup_required = ["firstname", "lastname",
                       "othername", "phone", "email", "password", "username"]

    def validate_names(self):
        fname = self.data["firstname"]
        lname = self.data["lastname"]
        other = self.data["othername"]

        if not fname.isalpha() or not lname.isalpha() or not other.isalpha():
            abort(make_response(jsonify({"status": 422, "message": "first, last and other name can only contain letters",
                                         "error": "invalid naming format"}), 422))

    def check_phone_length(self):
        phone = self.data["phone"]
        if phone[0] == "+" and not len(phone) in range(11, 14):
            abort(make_response(
                jsonify({"status": 422, "message": "phone number length invalid(11-13)"}), 422))
        elif phone[0].isdigit() and phone.isdigit():
            if not len(phone) == 10:
                abort(make_response(
                    jsonify({"status": 422, "message": "phone number length invalid(10)"}), 422))

    def validate_phone(self):
        phone = self.data["phone"]
        self.check_phone_length()
        if phone[0] == "+" and not phone[1:].isdigit():
            abort(make_response(jsonify({"status": 422,
                                         "message": "phone number can only be digits after '+'"}), 422))
        elif (phone[0] == "+" and phone[1:].isdigit()) or phone.isdigit():
            phone = True
        elif not phone[0].isdigit() or not phone[0] == "+":
            abort(make_response(jsonify({"status": 422,
                                         "message": "phone number can start with '+' and have digits"}), 422))

    def valid_username(self):
        """ validates the username parsed """
        if re.search("[!@#$%^&*-/\\')(;\"`<>?:|}{~ ]", self.data["username"]):
            abort(make_response(
                jsonify({"status": 400, "error": "username can only be a letter, digit or _"}), 400))

    def validate_password(self):
        pwd = self.data["password"]
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
            abort(make_response(jsonify({"status": 422, "error": "invalid password",
                                         "message": missing}), 422))

    def validate_email(self):
        if not EMAIL_REGEX.match(self.data["email"]):
            abort(make_response(jsonify({"status": 422,
                                         "error": "invalid email format!! -> (example@mail.com)"}), 422))
