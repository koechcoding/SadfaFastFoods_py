from .base import JsonRequest


class PostRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'name': 'required|alpha|unique:Menu,name',
        }


class PutRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'name': 'required|alpha',
        }
