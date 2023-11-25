from flask import request
from app.models import Notification
from flask_restful import Resource
from app.middlewares.validation import validate
from app.middlewares.auth import user_auth
from app.utils import decoded_qs, current_user


class NotificationResource(Resource):
    @user_auth
    def get(self, notification_id):
        # exists? ...
        notification = Notification.query.get(notification_id)
        if not notification:
            return {
                'success': False,
                'message': 'Notification not found.',
            }, 404

        user = current_user()
        if notification.user_id != user.id:
            return {
                'success': False,
                'message': 'Unauthorized to access this notification.',
            }, 401


        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'Notification successfully retrieved.',
            'notification': notification.to_dict(fields=fields)
        }

    @user_auth
    def delete(self, notification_id):
        # exists? ...
        notification = Notification.query.get(notification_id)
        if not notification:
            return {
                'success': False,
                'message': 'Notification not found.',
            }, 404

        user = current_user()
        if notification.user_id != user.id:
            return {
                'success': False,
                'message': 'Unauthorized to delete this notification.',
            }, 401
        notification.delete()
        return {
            'success': True,
            'message': 'Notification successfully deleted.',
        }


class NotificationListResource(Resource):
    @user_auth
    def get(self):
        resp = Notification.paginate(
            name='notifications',
            filters=decoded_qs(),
            user_id=current_user().id
        )
        resp['message'] = 'Successfully retrieved notifications.'
        resp['success'] = True
        return resp

    @user_auth
    def delete(self):
        user = current_user()
        notifications = Notification.query.filter_by(user_id=user.id).all()
        for notification in notifications:
            notification.delete()
        return {
            'success': True,
            'message': 'Successfully deleted all notifications.',
        }
