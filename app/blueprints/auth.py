"""This handles user authentication"""

import os
from app.utils import rand_string
from app.middlewares.validation import validate
from app.models import User, Blacklist, PasswordReset
from app.middlewares.auth import admin_auth, user_auth
from app.mail import email_verification_mail, password_reset_mail
from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                get_raw_jwt)
from app.requests.auth import (LoginRequest, RegisterRequest,
                               EmailVerificationRequest, PasswordResetRequest,
                               MakePasswordResetRequest)

auth = Blueprint('auth', __name__)


@auth.route('/api/v1/auth/signup', methods=['POST'])
@validate(RegisterRequest)
def register():
    """Register a user using their username, email and
    password"""

    user = User.create(request.json)
    user.token = str(user.id) + rand_string(size=60)
    user.save()

    env = current_app.config['ENV']
    resp = {
        'success':
        True,
        'user':
        user.to_dict(),
        'message': ('Successfully registered account.'
                    'Please verify your email to proceed.')
    }
    if env == 'production':
        try:
            email_verification_mail(token=user.token, recipient=user.email)
        except Exception:
            user.delete()
            return jsonify({
                'success': False,
                'message': 'Connection error. Please try again.',
            }), 400
        return jsonify(resp), 201
    elif env == 'development':
        resp['token'] = user.token
        return jsonify(resp), 201
    elif env == 'testing':
        user.token = ''
        user.save()
        return jsonify(resp), 201


@auth.route('/api/v1/auth/verify-email', methods=['POST'])
@validate(EmailVerificationRequest)
def verify():
    """Verifies email account used by user for registration"""

    # get user with this token
    user = User.query.filter_by(token=request.json['token']).first()
    # reclaim the token
    user.token = ''
    user.save()

    return jsonify({
        'success':
        True,
        'message':
        'Successfully verified email address. Proceed to login.',
    })


@auth.route('/api/v1/auth/password-reset', methods=['POST'])
@validate(MakePasswordResetRequest)
def make_password_reset():
    """Creates a password reset token"""
    email = request.json['email']
    user = User.query.filter_by(email=email).first()

    token = rand_string(size=60)
    data = {'token': token, 'user_id': user.id}

    PasswordReset.create(data)
    resp = {
        'success':
        True,
        'message': ('An email has been sent with the password reset link. '
                    'Please login to your email address to proceed.')
    }

    env = current_app.config['ENV']
    if env == 'production':
        try:
            password_reset_mail(token=token, recipient=email)
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Connection error. Please try again.'
            }), 400
        return jsonify(resp)
    else:
        resp['token'] = token
        resp['message'] = 'Password reset created.'
        return jsonify(resp)


@auth.route('/api/v1/auth/password-reset', methods=['PUT'])
@validate(PasswordResetRequest)
def password_reset():
    """Makes a password reset"""
    reset = PasswordReset.query.filter_by(token=request.json['token']).first()
    user = User.query.get(reset.user_id)
    if not user:
        return jsonify({
            'success': False,
            'message': 'Password reset request user not found.'
        }), 404

    user.update({'password': request.json['password']})
    reset.delete()
    return jsonify({
        'success':
        True,
        'message':
        'Password successfully reset. Please proceed to login.'
    })


@auth.route('/api/v1/auth/login', methods=['POST'])
@validate(LoginRequest)
def login():
    """Logs in a user using JwT and responds with an access token"""

    user = User.query.filter_by(email=request.json['email']).first()
    if not user or not user.validate_password(request.json['password']):
        return jsonify({
            'success': False,
            'message': 'Invalid credentials',
        }), 400

    env = current_app.config['ENV']
    if env in ['production', 'development'] and user.token != '':
        return jsonify({
            'success':
            False,
            'message': ('This account has not been verified.'
                        ' Please verify your email address')
        }), 400

    token = create_access_token(identity=request.json['email'])
    return jsonify({
        'success': True,
        'message': 'Successfully logged in',
        'access_token': token,
        'user': user.to_dict()
    })


@auth.route('/api/v1/auth', methods=['GET'])
@user_auth
def get_user():
    """Returns the authencicated users details"""

    user = User.query.filter_by(email=get_jwt_identity()).first()
    return jsonify({
        'success': True,
        'message': 'Successfully retrieved user',
        'user': user.to_dict()
    })


@auth.route('/api/v1/auth/logout', methods=['DELETE'])
@user_auth
def logout():
    """Logs out currently logged in user by adding the
    JWT to a blacklist"""

    jti = get_raw_jwt()['jti']
    blacklist = Blacklist(token=jti)
    blacklist.save()
    return jsonify({'success': True, 'message': 'Successfully logged out.'})
