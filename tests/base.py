import json
import unittest
from app.models import User, UserType


class BaseTest(unittest.TestCase):
    """This will hold the basic methods required by other tests, for
    example authentication in order to test guarded endpoints
    """

    def setUpAuth(self):
        """Setup user authentication headers for use during tests"""
        self.user, self.user_headers = self.authUser()
        self.admin, self.admin_headers = self.authAdmin()

    def authAdmin(self, email='admin@mail.com'):
        """Create and authenticate an admin user"""
        admin = self._createUser(email=email, role=UserType.ADMIN)
        return admin, self._authenticate(admin)

    def authUser(self, email='user@mail.com'):
        """Create and authenticate a normal user"""
        user = self._createUser(email=email, role=UserType.USER)
        return user, self._authenticate(user)

    def data(self):
        """Test model data"""
        return json.dumps({})

    def data_only(self, fields):
        """Specify the only fields you need for the request"""
        only = {}
        data = json.loads(self.data())
        for field, value in data.items():
            if field in fields:
                only[field] = value
        return json.dumps(only)

    def data_with(self, fields):
        """Modify default data fields"""
        with_fields = json.loads(self.data())
        for field, value in fields.items():
            with_fields[field] = value
        return json.dumps(with_fields)

    def data_without(self, fields):
        """Specify data fields not to include on the request"""
        without = {}
        data = json.loads(self.data())
        for field, value in data.items():
            if field not in fields:
                without[field] = value
        return json.dumps(without)

    def to_dict(self, res):
        return json.loads(res.get_data(as_text=True))

    def to_json(self, json_res):
        return json.dumps(json_res)

    def _createUser(self, email, role):
        """Creates a user with given mail and role"""
        with self.app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username='John', email=email, password='secret', role=role)
                user.save()
            return user.to_dict()

    def _authenticate(self, user):
        """Authenticates a user and returns the auth headers"""
        res = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': user['email'],
                'password': 'secret'
            }),
            headers={'Content-Type': 'application/json'})
        result = json.loads(res.get_data(as_text=True))
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(result['access_token'])
        }
