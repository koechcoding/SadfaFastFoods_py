from .base import JsonRequest
from app.utils import current_user


class PostRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'quantity': 'required|integer|positive',
            'user_id': 'required|integer|positive|exists:User,id',
            'menu_item_id': 'required|integer|positive|exists:MenuItem,id',
        }


class PutRequest(JsonRequest):
    @staticmethod
    def rules():
        rules = {
            'quantity': 'integer|positive',
            'menu_item_id': 'integer|positive|exists:MenuItem,id',
        } 
        if current_user().is_admin():
            rules['status'] = 'integer|found_in:1,2,3'
        return rules
