from flask import request
from app.models import User, UserType
from flask_restful import Resource
from app.requests.users import PostRequest, PutRequest
from app.middlewares.validation import validate
from app.middlewares.auth import user_auth, admin_auth
from app.utils import decoded_qs


class UserResource(Resource):
    @admin_auth
    def get(self, user_id):
        # exists? ...
        user = User.query.get(user_id)

        if not user:
            return {
                'success': False,
                'message': 'User not found.',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'User successfully retrieved.',
            'user': user.to_dict(fields=fields)
        }

    @admin_auth
    @validate(PutRequest)
    def put(self, user_id):
        # check exists? ...
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')


        role = request.json.get('role')
        if role and role == UserType.SUPER_ADMIN:
            return {
                'success': False,
                'message': 'Only one super admin is allowed',
            }, 400
            

        # now update...
        user.update(request.json)
        return {
            'success': True,
            'message': 'User successfully updated.',
            'user': user.to_dict(fields=fields)
        }

    @admin_auth
    def delete(self, user_id):
        # exists? ...
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found.',
            }, 404

        if user.is_super_admin():
            return {
                'success': False,
                'message': 'You cannot delete this users account.',
            }, 401

        user.delete()
        return {
            'success': True,
            'message': 'User successfully deleted.',
        }


class UserListResource(Resource):
    @admin_auth
    def get(self):
        resp = User.paginate(
            filters=decoded_qs(),
            name='users'
        )
        resp['message'] = 'Successfully retrieved users.'
        resp['success'] = True
        return resp

    @admin_auth
    @validate(PostRequest)
    def post(self):
        user = User.create(request.json)
        return {
            'success': True,
            'message': 'Successfully saved user.',
            'user': user.to_dict()
        }, 201
