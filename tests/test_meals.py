import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest


class TestMeals(BaseTest):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()

    def data(self):
        return json.dumps({'name': 'ugali', 'cost': 30.0})

    def test_can_create_meal(self):
        res = self.client.post(
            'api/v1/meals', data=self.data(), headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved meal', res.data)

    def test_cannot_create_meal_without_cost(self):
        res = self.client.post(
            'api/v1/meals',
            data=self.data_without(['cost']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'cost field is required', res.data)

    def test_cannot_create_meal_without_name(self):
        res = self.client.post(
            'api/v1/meals',
            data=self.data_without(['name']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'name field is required', res.data)

    def test_cannot_create_meal_without_numeric_cost(self):
        res = self.client.post(
            'api/v1/meals',
            data=self.data_with({
                'cost': 'abc'
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'cost must be a positive number', res.data)

    def test_cannot_create_meal_without_positive_cost(self):
        res = self.client.post(
            'api/v1/meals',
            data=self.data_with({
                'cost': -20
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'cost must be a positive number', res.data)

    def test_cannot_create_meal_without_unique_name(self):
        json_res = self.create_meal(self.data())
        res = self.client.post(
            'api/v1/meals',
            data=self.data_with({
                'name': json_res['meal']['name'].upper()
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'The name is already taken', res.data)

    def test_can_get_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.get(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data(),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'ugali', res.data)

    def test_cannot_get_nonexistant_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.get(
            'api/v1/meals/1000',
            data=self.data(),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Meal not found', res.data)

    def test_can_update_meal(self):
        json_res = self.create_meal(self.data())

        # update without change
        res = self.client.put(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'ugali', res.data)

        # update with different data
        res = self.client.put(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data_with({
                'name': 'beef'
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'beef', res.data)

        # update without data
        res = self.client.put(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data_without(['name', 'cost']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'beef', res.data)

    def test_user_cannot_update_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.put(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data(),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Unauthorized access', res.data)

    def test_cannot_update_nonexistant_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.put(
            'api/v1/meals/1000',
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Meal not found', res.data)

    def test_cannot_update_meal_without_unique_name(self):
        self.create_meal(self.data_with({'name': 'ugali'}))
        json_res = self.create_meal(self.data_with({'name': 'beef'}))
        res = self.client.put(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data_with({
                'name': 'ugali'
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'Meal name must be unique', res.data)

    def test_can_get_paginated_meals(self):
        self.create_meal(self.data_with({'name': 'beef'}))
        self.create_meal(self.data_with({'name': 'ugali'}))
        res = self.client.get(
            'api/v1/meals', data=self.data(), headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved meals', res.data)

    def test_can_delete_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.delete(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Meal successfully deleted', res.data)
        res = self.client.get(
            'api/v1/meals/{}'.format(json_res['meal']['id']),
            data=self.data(),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Meal not found', res.data)

    def test_cannot_delete_nonexistant_meal(self):
        json_res = self.create_meal(self.data())
        res = self.client.delete(
            'api/v1/meals/1000',
            data=self.data(),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Meal not found', res.data)

    def create_meal(self, data):
        res = self.client.post(
            'api/v1/meals', data=data, headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved meal', res.data)
        return self.to_dict(res)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
