import string
import random
from datetime import date
from urllib import parse
from flask import request
from app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity


def current_user():
    user = User.query.filter_by(email=get_jwt_identity()).first()
    if not user:
        raise Exception('Authentication: current user not found')
    return user


def decoded_qs():
    query = {}
    for key, value in request.args.to_dict().items():
        query[key] = parse.unquote(value)
    if len(query):
        return query
    return None


def str_to_date(date_str):
    date_lst = date_str.split('-')
    if len(date_lst) == 3:
        try:
            year, month, day = [int(x) for x in date_lst]
            return date(year, month, day)
        except ValueError:
            return None
    return None


def rand_string(size=60):
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=size))
