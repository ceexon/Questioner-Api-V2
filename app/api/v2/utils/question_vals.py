from flask import jsonify, abort, make_response
from.base_vals import BaseValidation


class QuestionValid(BaseValidation):
    """ validate user question input """

    question_required = ["title", "body"]
