from .base import JsonRequest


class PostRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'email': 'required|email|unique:User,email',
            'password': 'required|string|confirmed|least_string:6',
            'username': 'required|alpha|least_string:3',
            'role': 'integer|positive|found_in:1,2',
        }


class PutRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'password': 'string|confirmed|least_string:6',
            'username': 'alpha|least_string:3',
            'role': 'integer|positive|found_in:1,2',
        }
