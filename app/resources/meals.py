from flask import request
from app.models import Meal
from flask_restful import Resource
from app.requests.meals import PostRequest, PutRequest
from app.middlewares.validation import validate
from app.middlewares.auth import user_auth, admin_auth
from app.utils import decoded_qs


class MealResource(Resource):
    @user_auth
    def get(self, meal_id):
        # exists? ...
        meal = Meal.query.get(meal_id)

        if not meal:
            return {
                'success': False,
                'message': 'Meal not found.',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'Meal successfully retrieved.',
            'meal': meal.to_dict(fields=fields)
        }

    @admin_auth
    @validate(PutRequest)
    def put(self, meal_id):
        # check exists? ...
        meal = Meal.query.get(meal_id)
        if not meal:
            return {
                'success': False,
                'message': 'Meal not found',
            }, 404

        # check if another meal exists with new name...
        if request.json.get('name'):
            name = request.json['name']
            new_meal = Meal.query.filter(Meal.name.ilike(name)).first()
            if new_meal and new_meal.name.lower() == name.lower() and \
                    new_meal.id != meal_id:
                return {
                    'success': False,
                    'message': 'Validation error.',
                    'errors': {
                        'name': ['Meal name must be unique.']
                    }
                }, 400

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        # now update...
        meal.update(request.json)
        return {
            'success': True,
            'message': 'Meal successfully updated.',
            'meal': meal.to_dict(fields=fields)
        }

    @admin_auth
    def delete(self, meal_id):
        # exists? ...
        meal = Meal.query.get(meal_id)
        if not meal:
            return {
                'success': False,
                'message': 'Meal not found.',
            }, 404

        meal.delete()
        return {
            'success': True,
            'message': 'Meal successfully deleted.',
        }


class MealListResource(Resource):
    @user_auth
    def get(self):
        resp = Meal.paginate(
            filters=decoded_qs(),
            name='meals'
        )
        resp['message'] = 'Successfully retrieved meals.'
        resp['success'] = True
        return resp

    @admin_auth
    @validate(PostRequest)
    def post(self):
        meal = Meal.create(request.json)
        return {
            'success': True,
            'message': 'Successfully saved meal.',
            'meal': meal.to_dict()
        }, 201
