from flask import request
from app.models import Menu
from flask_restful import Resource
from app.requests.menu import PostRequest, PutRequest
from app.middlewares.auth import user_auth, admin_auth
from app.middlewares.validation import validate
from app.utils import decoded_qs


class MenuResource(Resource):

    @user_auth
    def get(self, menu_id):
        # exists? ...
        menu = Menu.query.get(menu_id)
        if not menu:
            return {
                'success': False,
                'message': 'Menu not found.',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'Menu successfully retrieved.',
            'menu': menu.to_dict(fields=fields)
        }

    @admin_auth
    @validate(PutRequest)
    def put(self, menu_id):

        # check if another menu exists with new name...
        if request.json.get('name'):
            name = request.json['name']
            menu = Menu.query.filter_by(name=name).first()
            if menu and menu.name.lower() == name.lower() and \
                    menu.id != menu_id:
                return {
                    'success': False,
                    'message': 'Validation error.',
                    'errors': {
                        'name': ['Menu name must be unique.']
                    }
                }, 400

        # check exists? ...
        menu = Menu.query.get(menu_id)
        if not menu:
            return {
                'success': False,
                'message': 'Menu not found.',
            }, 404

        # now update...
        menu.update(request.json)
        return {
            'success': True,
            'message': 'Menu successfully updated.',
            'menu': menu.to_dict()
        }

    @admin_auth
    def delete(self, menu_id):
        # exists? ...
        menu = Menu.query.get(menu_id)
        if not menu:
            return {
                'success': False,
                'message': 'Menu not found.',
            }, 404

        menu.delete()
        return {
            'success': True,
            'message': 'Menu successfully deleted.',
        }


class MenuListResource(Resource):
    @user_auth
    def get(self):
        resp = Menu.paginate(
            filters=decoded_qs(),
            name='menus'
        )
        resp['message'] = 'Successfully retrieved menus.'
        resp['success'] = True
        return resp

    @admin_auth
    @validate(PostRequest)
    def post(self):
        menu = Menu.create(request.json)
        return {
            'success': True,
            'message': 'Successfully saved menu.',
            'menu': menu.to_dict()
        }, 201

