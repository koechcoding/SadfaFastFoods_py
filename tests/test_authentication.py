import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest


class AuthenticationTestCase(BaseTest):
    """This will test authentication endpoints"""

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        self.headers = {'Content-Type' : 'application/json'}
        with self.app.app_context():
            db.create_all()

    def data(self):
        return json.dumps({
            'username': 'John',
            'email': 'john@doe.com',
            'password': 'secret',
            'password_confirmation': 'secret'
        })

    def test_can_register(self):
        """Test user can register"""
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data(),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully registered account', res.data)

    def test_cannot_register_without_email(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_without(['email']),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'email field is required', res.data)

    def test_cannot_register_with_invalid_email(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_with({'email': 'hi'}),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'email must be a valid email address', res.data)

    def test_cannot_register_without_username(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_without(['username']),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'username field is required', res.data)

    def test_cannot_register_without_password(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_without(['password']),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'password field is required', res.data)

    def test_cannot_register_without_password_confirmation(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_without(['password_confirmation']),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'confirmation does not match', res.data)

    def test_cannot_register_without_password_confirmation_matching(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_with({'password_confirmation': 'hi'}),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'confirmation does not match', res.data)

    def test_cannot_register_without_long_password(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_with({
                'password': 'hi',
                'password_confirmation': 'hi'
            }),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'password must be at least', res.data)

    def test_cannot_register_without_string_username(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data_with({'username': 12}),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'username may contain only letters', res.data)

    def test_can_login(self):
        """Test user can login"""
        user, headers = self.authUser()
        res = self.client.post(
            'api/v1/auth/login',
            data=json.dumps({
                'email': user['email'],
                'password': 'secret'
            }),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully logged in', res.data)

    def test_cannot_login_without_email(self):
        """Test user can login"""
        user, headers = self.authUser()
        res = self.client.post(
            'api/v1/auth/login',
            data=json.dumps({
                'password': 'secret'
            }),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'email field is required', res.data)

    def test_cannot_login_without_password(self):
        """Test user can login"""
        user, headers = self.authUser()
        res = self.client.post(
            'api/v1/auth/login',
            data=json.dumps({
                'email': user['email'],
            }),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'password field is required', res.data)

    def test_can_get_user(self):
        """Test user can login"""
        user, headers = self.authUser()
        res = self.client.get(
            'api/v1/auth',
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved user', res.data)

    def test_can_logout(self):
        """Test user can logout"""
        user, headers = self.authUser()
        res = self.client.delete(
            'api/v1/auth/logout',
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully logged out', res.data)

    def test_can_request_password_reset(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data(),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 201)
        res = self.client.post(
            'api/v1/auth/password-reset',
            data=self.data(),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password reset created', res.data)

    def test_can_make_password_reset(self):
        res = self.client.post(
            'api/v1/auth/signup',
            data=self.data(),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 201)
        res = self.client.post(
            'api/v1/auth/password-reset',
            data=self.data(),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password reset created', res.data)
        json_res = self.to_dict(res)
        res = self.client.put(
            'api/v1/auth/password-reset',
            data=json.dumps({
                'token': json_res['token'],
                'password': 'secret2',
                'password_confirmation': 'secret2'
            }),
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password successfully reset', res.data)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
