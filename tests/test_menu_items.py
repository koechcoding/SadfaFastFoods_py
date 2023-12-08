import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest


class MenuItemTests(BaseTest):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()

    def data(self):
        return json.dumps({
            'quantity': 30,
            'meal_id': self.create_meal()['meal']['id'],
            'menu_id': self.create_menu()['menu']['id'],
        })

    def test_can_create_menu_item(self):
        res = self.client.post(
            'api/v1/menu-items', data=self.data(), headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu item', res.data)

    def test_cannot_create_menu_item_without_quantity(self):
        res = self.client.post(
            'api/v1/menu-items',
            data=self.data_without(['quantity']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'quantity field is required', res.data)

    def test_cannot_create_menu_item_without_menu_id(self):
        res = self.client.post(
            'api/v1/menu-items',
            data=self.data_without(['menu_id']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'id field is required', res.data)

    def test_cannot_create_menu_item_without_meal_id(self):
        res = self.client.post(
            'api/v1/menu-items',
            data=self.data_without(['meal_id']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'id field is required', res.data)

    def test_cannot_create_menu_item_with_nonexistant_meal_id(self):
        res = self.client.post(
            'api/v1/menu-items',
            data=self.data_with({
                'meal_id': 300
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'The selected meal id is invalid', res.data)

    def test_cannot_create_menu_item_with_nonexistant_menu_id(self):
        res = self.client.post(
            'api/v1/menu-items',
            data=self.data_with({
                'menu_id': 300
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'The selected menu id is invalid', res.data)

    def test_can_update_menu_item(self):
        menu_item = self.create_menu_item(self.data())
        meal_id = self.create_meal(name='beef')['meal']['id']
        res = self.client.put(
            'api/v1/menu-items/{}'.format(menu_item['menu_item']['id']),
            data=json.dumps({
                'meal_id': meal_id
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Menu item successfully updated', res.data)

    def test_cannot_update_menu_item_without_being_unique(self):
        # create a menu item
        menu_item = self.create_menu_item(self.data())['menu_item']
        meal_id = menu_item['meal']['id']
        menu_id = menu_item['menu']['id']

        # create another menu item
        new_meal_id = self.create_meal(name='beef')['meal']['id']
        new_menu_item = self.create_menu_item(
            json.dumps({
                'quantity': 30,
                'menu_id': menu_id,
                'meal_id': new_meal_id,
            }))
        # try to update the first one with the second's values
        res = self.client.put(
            'api/v1/menu-items/{}'.format(new_menu_item['menu_item']['id']),
            data=json.dumps({
                'meal_id': meal_id,
                'menu_id': 2,
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'is invalid', res.data)

    def test_can_get_menu_item(self):
        menu_item = self.create_menu_item(self.data())
        res = self.client.get(
            'api/v1/menu-items/{}'.format(menu_item['menu_item']['id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'successfully retrieved', res.data)

    def test_can_get_many_menu_items_history(self):
        self.create_menu_item(self.data())
        res = self.client.get(
            'api/v1/menu-items?history=1', headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved', res.data)

    def test_can_get_many_menu_items(self):
        self.create_menu_item(self.data())
        res = self.client.get('api/v1/menu-items', headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved', res.data)

    def test_can_delete_menu_item(self):
        menu_item = self.create_menu_item(self.data())
        res = self.client.delete(
            'api/v1/menu-items/{}'.format(menu_item['menu_item']['id']),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Menu item successfully deleted', res.data)

    def create_menu_item(self, data):
        res = self.client.post(
            'api/v1/menu-items', data=data, headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu item', res.data)
        return self.to_dict(res)

    def create_meal(self, name='ugali'):
        res = self.client.post(
            'api/v1/meals',
            data=json.dumps({
                'name': name,
                'cost': 30,
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved meal', res.data)
        return self.to_dict(res)

    def create_menu(self, name='Lunch'):
        res = self.client.post(
            'api/v1/menus',
            data=json.dumps({
                'name': name,
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu', res.data)
        return self.to_dict(res)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
