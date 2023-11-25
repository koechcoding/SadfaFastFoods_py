from flask import request
from datetime import date
from app.models import MenuItem
from flask_restful import Resource
from app.requests.menu_items import PostRequest, PutRequest
from app.middlewares.auth import user_auth, admin_auth
from app.middlewares.validation import validate
from app.utils import decoded_qs
from sqlalchemy import cast, DATE


class MenuItemResource(Resource):
    @user_auth
    def get(self, menu_item_id):
        # exists? ...
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {
                'success': False,
                'message': 'Menu item not found.',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'Menu item successfully retrieved.',
            'menu_item': menu_item.to_dict(fields=fields)
        }

    @admin_auth
    @validate(PutRequest)
    def put(self, menu_item_id):

        # check exists? ...
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {
                'success': False,
                'message': 'Menu item not found.',
            }, 404

        # for uniqueness check...
        meal_id = request.json.get('meal_id') or menu_item.meal_id
        menu_id = request.json.get('menu_id') or menu_item.menu_id

        # check if another menu item exists with same values today
        timestamp = cast(MenuItem.created_at, DATE)
        existing = MenuItem.query.filter(timestamp == date.today()).filter_by(
            meal_id=meal_id, menu_id=menu_id
        ).first()
        if existing and existing.id != menu_item_id:
            return {
                'success': False,
                'message': 'Validation error.',
                'errors': {
                    'ids': ['Menu item must be unique.']
                }
            }, 400

        # now update...
        menu_item.update(request.json)
        return {
            'success': True,
            'message': 'Menu item successfully updated.',
            'menu_item': menu_item.to_dict()
        }

    @admin_auth
    def delete(self, menu_item_id):
        # exists? ...
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {
                'success': False,
                'message': 'Menu item not found.',
            }, 404

        menu_item.delete()
        return {
            'success': True,
            'message': 'Menu item successfully deleted.',
        }


class MenuItemListResource(Resource):
    @user_auth
    def get(self):
        resp = MenuItem.paginate(
            filters=decoded_qs(),
            name='menu_items'
        )
        resp['message'] = 'Successfully retrieved menu items.'
        resp['success'] = True
        return resp

    @admin_auth
    @validate(PostRequest)
    def post(self):

        # ensure uniqueness
        meal_id = request.json['meal_id']
        menu_id = request.json['menu_id']

        # check if another menu item exists with same values today
        timestamp = cast(MenuItem.created_at, DATE)
        menu_item = MenuItem.query.filter(timestamp == date.today()).filter_by(
            meal_id=meal_id, menu_id=menu_id
        ).first()
        if menu_item:
            return {
                'success': False,
                'message': 'Validation error.',
                'errors': {
                    'ids': ['Menu item must be unique.']
                }
            }, 400

        menu_item = MenuItem.create(request.json)
        return {
            'success': True,
            'message': 'Successfully saved menu item.',
            'menu_item': menu_item.to_dict()
        }, 201
