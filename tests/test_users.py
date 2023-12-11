import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest


class TestUsers(BaseTest):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()

    def data(self):
        return json.dumps({
            'username': 'John',
            'email': 'john@doe.com',
            'password': 'secret',
            'password_confirmation': 'secret'
        })

    def test_can_create_user(self):
        res = self.client.post(
            'api/v1/users', data=self.data(), headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved user', res.data)

    def test_can_search_user_fields(self):
        res = self.client.get(
            'api/v1/users?search=mail',
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved users', res.data)

    def test_can_search_user_field(self):
        res = self.client.get(
            'api/v1/users?search=email:mail',
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved users', res.data)

    def test_can_filter_fields(self):
        res = self.client.get(
            'api/v1/users?fields=name,email',
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved users', res.data)

    def test_can_get_all_user(self):
        res = self.client.get('api/v1/users', headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved users', res.data)

    def test_can_get_one_user(self):
        res = self.client.get('api/v1/users/1', headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'User successfully retrieved', res.data)

    def test_can_update_user(self):
        res = self.client.put(
            'api/v1/users/1',
            data=self.data_with({
                'role': 1
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'User successfully updated', res.data)

    def test_can_delete_user(self):
        res = self.client.delete('api/v1/users/1', headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'User successfully deleted.', res.data)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
