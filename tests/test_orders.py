import json
from app import create_app, db
from app.models import User, UserType
from .base import BaseTest


class TestOrders(BaseTest):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()

    def data(self):
        return json.dumps({
            'quantity': 2,
            'user_id': self.user['id'],
            'menu_item_id': self.create_menu_item()['menu_item']['id']
        })

    def test_can_create_order(self):
        res = self.client.post(
            'api/v1/orders', data=self.data(), headers=self.user_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved order', res.data)

    def test_cannot_create_order_without_user_id(self):
        res = self.client.post(
            'api/v1/orders',
            data=self.data_without(['user_id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'user id field is required', res.data)

    def test_cannot_create_order_without_quantity(self):
        res = self.client.post(
            'api/v1/orders',
            data=self.data_without(['quantity']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'quantity field is required', res.data)

    def test_cannot_create_order_without_menu_item_id(self):
        res = self.client.post(
            'api/v1/orders',
            data=self.data_without(['menu_item_id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'menu item id field is required', res.data)

    def test_cannot_create_order_with_quantity_than_available(self):
        res = self.client.post(
            'api/v1/orders',
            data=self.data_with({
                'quantity': 1000
            }),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'meal(s) are available', res.data)

    def test_can_update_order(self):
        json_res = self.create_order()
        res = self.client.put(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            data=json.dumps({
                'quantity': 20,
                'menu_item_id': json_res['order']['menu_item_id'],
            }),
            headers=self.user_headers)
        json_res = self.to_dict(res)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_res['order']['quantity'], 20)
        self.assertIn(b'successfully updated', res.data)

    def test_admin_can_update_order(self):
        json_res = self.create_order()
        res = self.client.put(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            data=json.dumps({
                'quantity': 20,
                'menu_item_id': json_res['order']['menu_item_id'],
            }),
            headers=self.admin_headers)
        json_res = self.to_dict(res)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_res['order']['quantity'], 20)
        self.assertIn(b'successfully updated', res.data)

    def test_cannot_update_another_users_order(self):
        json_res = self.create_order()
        user, headers = self.authUser(email='other@mail.com')
        res = self.client.put(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            data=json.dumps({
                'quantity': 20,
                'menu_item_id': json_res['order']['menu_item_id'],
            }),
            headers=headers)
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Unauthorized access', res.data)

    def test_can_get_order(self):
        json_res = self.create_order()
        res = self.client.get(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'successfully retrieved', res.data)

    def test_can_get_many_orders(self):
        json_res = self.create_order()
        res = self.client.get(
            'api/v1/orders',
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved orders', res.data)

    def test_can_get_many_orders_history(self):
        json_res = self.create_order()
        res = self.client.get(
            'api/v1/orders?history=1',
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved orders', res.data)

    def test_can_delete_order(self):
        json_res = self.create_order()
        res = self.client.delete(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'successfully deleted', res.data)
        res = self.client.get(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            headers=self.user_headers)
        self.assertEqual(res.status_code, 404)

    def test_cannot_delete_another_users_order(self):
        json_res = self.create_order()
        user, headers = self.authUser(email='other@mail.com')
        res = self.client.delete(
            'api/v1/orders/{}'.format(json_res['order']['id']),
            headers=headers)
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Unauthorized access', res.data)

    def create_order(self):
        res = self.client.post(
            'api/v1/orders', data=self.data(), headers=self.user_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved order', res.data)
        return self.to_dict(res)

    def create_menu_item(self):
        # create a meal
        res = self.client.post(
            'api/v1/meals',
            data=json.dumps({
                'name': 'ugali',
                'cost': 30,
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved meal', res.data)
        meal_id = self.to_dict(res)['meal']['id']

        # now create a menu
        res = self.client.post(
            'api/v1/menus',
            data=json.dumps({
                'name': 'Lunch'
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu', res.data)
        menu_id = self.to_dict(res)['menu']['id']

        # finally create a menu item
        res = self.client.post(
            'api/v1/menu-items',
            data=json.dumps({
                'quantity': 100,
                'menu_id': menu_id,
                'meal_id': meal_id
            }),
            headers=self.admin_headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn(b'Successfully saved menu item', res.data)
        return self.to_dict(res)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
