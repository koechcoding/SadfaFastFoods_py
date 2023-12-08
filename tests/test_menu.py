import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest

class TestMenu(BaseTest):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()

    def data(self):
        return json.dumps({
            'name': 'Lunch'
        })

    def test_can_create_menu(self):
        res = self.client.post(
            'api/v1/menus',
            data=self.data(),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu', res.data)

    def test_cannot_create_menu_without_name(self):
        res = self.client.post(
            'api/v1/menus',
            data=self.data_without(['name']),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'name field is required', res.data)

    def test_cannot_create_menu_without_unique_name(self):
        json_res = self.create_menu(self.data())
        res = self.client.post(
            'api/v1/menus',
            data=self.data(),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'name is already taken', res.data)

    def test_can_get_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.get(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Lunch', res.data)

    def test_can_get_all_menus(self):
        self.create_menu(self.data())
        res = self.client.get(
            'api/v1/menus',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Lunch', res.data)

    def test_cannot_get_nonexistant_menu(self):
        self.create_menu(self.data())
        res = self.client.get(
            'api/v1/menus/1000',
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Menu not found', res.data)

    def test_can_delete_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.delete(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Menu successfully deleted', res.data)
        res = self.client.get(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'not found', res.data)

    def test_cannot_delete_nonexistant_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.delete(
            'api/v1/menus/1000',
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Menu not found', res.data)

    def test_can_update_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.put(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            data=self.data_with({'name': 'Supper'}),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Menu successfully updated', res.data)

    def test_user_cannot_update_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.put(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            data=self.data_with({'name': 'Supper'}),
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Unauthorized access', res.data)

    def test_cannot_update_nonexistant_menu(self):
        json_res = self.create_menu(self.data())
        res = self.client.put(
            'api/v1/menus/1000',
            data=self.data_with({'name': 'Supper'}),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Menu not found', res.data)

    def test_can_update_menu_with_same_data(self):
        json_res = self.create_menu(self.data())
        res = self.client.put(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            data=self.data_with({'name': 'Lunch'}),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Menu successfully updated', res.data)

    def test_cannot_update_menu_without_unique_name(self):
        self.create_menu(self.data_with({'name': 'Lunch'}))
        json_res = self.create_menu(self.data_with({'name': 'Breakfast'}))
        res = self.client.put(
            'api/v1/menus/{}'.format(json_res['menu']['id']),
            data=self.data_with({'name': 'Lunch'}),
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'must be unique', res.data)

    def create_menu(self, data):
        res = self.client.post(
            'api/v1/menus',
            data=data,
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu', res.data)
        return self.to_dict(res)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

