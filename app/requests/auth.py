from .base import JsonRequest


class RegisterRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'email': 'required|email|unique:User,email',
            'password': 'required|string|confirmed|least_string:6',
            'username': 'required|alpha|least_string:3',
        }


class LoginRequest(JsonRequest):
    @staticmethod
    def rules():
        return {'email': 'required|email', 'password': 'required|string'}


class EmailVerificationRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'token': 'required|string|exists:User,token',
        }


class MakePasswordResetRequest(JsonRequest):
    @staticmethod
    def rules():
        return { 'email': 'required|string|email|exists:User,email' }

class PasswordResetRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'token': 'required|string|exists:PasswordReset,token',
            'password': 'required|string|confirmed|least_string:6'
        }
