from .base import JsonRequest


class PostRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'quantity': 'required|integer|positive',
            'meal_id': 'required|integer|positive|exists:Meal,id',
            'menu_id': 'required|integer|positive|exists:Menu,id',
        }


class PutRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'quantity': 'integer|positive',
            'meal_id': 'integer|positive|exists:Meal,id',
            'menu_id': 'integer|positive|exists:Menu,id',
        }
