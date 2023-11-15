from flask import request
from app.validation.validator import Validator
from app.exceptions import ValidationException
from app.middlewares.clean_request import clean_json_request


class JsonRequest:

    @clean_json_request
    def __init__(self):

        # ensure we only pass registered fields..
        unrequired = []
        rules = self.rules()
        for field, values in request.json.items():
            if field not in rules and not field.endswith('_confirmation'):
                unrequired.append(field)

        for field in unrequired:
            del request.json[field]
        
        self.validator = Validator(
            rules=self.rules(),
            request=request.json
        )

    def validate(self):
        if self.validator.fails():
            raise ValidationException(self.validator.errors())

    @staticmethod
    def rules():
        return {}
