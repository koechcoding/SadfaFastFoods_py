from functools import wraps
from app.utils import current_user
from flask import jsonify, make_response, abort
from flask_jwt_extended import jwt_required


def user_auth(fn):
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

def admin_auth(fn):
    @wraps(fn)
    @user_auth
    def wrapper(*args, **kwargs):
        if not current_user().is_admin():
            abort(
                make_response(
                    jsonify({'message': 'Unauthorized access to a non-admin'}),
                    401
                )
            )
        return fn(*args, **kwargs)
    return wrapper
