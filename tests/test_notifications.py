import json
from app import create_app, db
from app.models import Notification
from .base import BaseTest


class NotificationTest(BaseTest):
    """This will test authentication endpoints"""

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        self.headers = {'Content-Type' : 'application/json'}
        with self.app.app_context():
            db.create_all()
            self.setUpAuth()
            Notification.create({
                'user_id': self.user['id'],
                'title': 'Test Notification',
                'message': 'Hi there user, we are testing this.'
            })
            Notification.create({
                'user_id': self.admin['id'],
                'title': 'Admin notification',
                'message': 'Hi there user, we are testing this.'
            })

    def test_can_get_notification(self):
        """Test user can register"""
        res = self.client.get(
            'api/v1/notifications/1',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Notification successfully retrieved', res.data)

    def test_can_get_all_notifications(self):
        res = self.client.get(
            'api/v1/notifications',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully retrieved notifications', res.data)

    def test_can_delete_one_notification(self):
        res = self.client.delete(
            'api/v1/notifications/1',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Notification successfully deleted', res.data)
        res = self.client.get(
            'api/v1/notifications/1',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 404)

    def test_can_delete_all_notifications(self):
        res = self.client.delete(
            'api/v1/notifications',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully deleted', res.data)
        res = self.client.get(
            'api/v1/notifications/1',
            headers=self.user_headers
        )
        print(res.data)
        self.assertEqual(res.status_code, 404)

    def test_cannot_delete_other_users_notification(self):
        res = self.client.delete(
            'api/v1/notifications/2',
            headers=self.user_headers
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Unauthorized to delete this notification', res.data)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
