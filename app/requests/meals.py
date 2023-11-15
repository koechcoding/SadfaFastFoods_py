from .base import JsonRequest


class PostRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'name': 'required|alpha|unique:Meal,name',
            'cost': 'required|positive',
            'img_url': 'url',
        }


class PutRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'name': 'alpha',
            'cost': 'positive',
            'img_url': 'url',
        }
