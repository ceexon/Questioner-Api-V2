from app.api.v2.utils.base_vals import BaseValidation


class MeetValid(BaseValidation):
    """ validating meetup data """
    required_meetup = ["topic", "location", "happen_on", ""]
