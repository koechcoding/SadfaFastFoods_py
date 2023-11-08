import re
from flask import request
from functools import wraps
from app.exceptions import ValidationException


def clean_json_request(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            raise ValidationException({'request':
                                       ['Request must be valid JSON']})

        # empty string fields...
        to_delete = []
        for field, value in request.json.items():
            # if field is string...
            if isinstance(value, str):
                # subtstitute spaces with one space and trim.
                request.json[field] = re.sub('\s+', ' ', value).strip()
                if value == '':
                    to_delete.append(field)

        # delete empty strings...
        for field in to_delete:
            del request.json[field]

        return fn(*args, **kwargs)
    return wrapper
