from flask import request
from datetime import date
from flask_restful import Resource
from app.models import OrderStatus, Order, MenuItem, Notification
from app.requests.orders import PostRequest, PutRequest
from app.middlewares.auth import user_auth, admin_auth
from app.utils import current_user
from app.middlewares.validation import validate
from app.utils import decoded_qs


class OrderResource(Resource):
    @user_auth
    def get(self, order_id):
        # exists? ...
        order = Order.query.get(order_id)
        if not order:
            return {
                'success': False,
                'message': 'Order not found.',
            }, 404

        fields = decoded_qs()
        if fields and fields.get('fields') is not None:
            fields = fields.get('fields').split(',')

        return {
            'success': True,
            'message': 'Order successfully retrieved.',
            'order': order.to_dict(fields=fields)
        }

    @user_auth
    @validate(PutRequest)
    def put(self, order_id):

        # exists? ...
        order = Order.query.get(order_id)
        if not order:
            return {
                'success': False,
                'message': 'Order not found.',
            }, 404

        # check user is authorized to update order
        user = current_user()
        if not user.is_admin() and user.id != order.user_id:
            return {
                'success': False,
                'message': 'Unauthorized access to this order.'
            }, 401

        if request.json.get('quantity'):
            # check that we have enough quantity...
            menu_item = MenuItem.query.get(request.json['menu_item_id'])
            available = order.quantity + menu_item.quantity
            if available < request.json['quantity']:
                message = None
                if menu_item.quantity > 0:
                    message = 'Only {} more meals are available.'.format(
                        menu_item.quantity)
                else:
                    message = 'No more orders can be made on this meal.'
                return {
                    'success': False,
                    'message': 'Validation error.',
                    'errors': {
                        'quantity': [message]
                    }
                }, 400

            # set the new quantity...
            menu_item.quantity = (
                menu_item.quantity - request.json['quantity'] + order.quantity)
            menu_item.save()

        # save status for comparison
        order_status = order.status

        # update...
        order.update(request.json)

        # for notification
        message = title = ''

        # check if order status has been changed by the admin
        if order_status != order.status:
            status = ''
            if order.status == OrderStatus.PENDING:
                status = 'Pending'
            elif order.status == OrderStatus.ACCEPTED:
                status = 'Accepted'
            else:
                status = 'Revoked'
            title = 'Order(#{}) status changed'.format(order.id)
            message = """Your order (#{}) for {} with {} items
            status has changed to {}.""".format(
                order.id, order.menu_item.meal.name, order.quantity, status)

        # use update their own order...
        else:
            title = 'Order(#{}) updated'.format(order.id)
            # save notification
            message = """You updated your order (#{}) for
            {} with {} items.""".format(order.id, order.menu_item.meal.name,
                                        order.quantity)

        # save notification
        Notification.create({
            'user_id': order.user_id,
            'title': title,
            'message': message
        })

        return {
            'success': True,
            'message': 'Order(#{}) successfully updated.'.format(order.id),
            'order': order.to_dict()
        }

    @user_auth
    def delete(self, order_id):
        # exists? ...
        order = Order.query.get(order_id)
        if not order:
            return {
                'success': False,
                'message': 'Order not found.',
            }, 404

        # check user can delete this order...
        user = current_user()
        if not user.is_admin() and user.id != order.user_id:
            return {
                'success': False,
                'message': 'Unauthorized access to this order.'
            }, 401

        # restore quantity...
        menu_item = MenuItem.query.get(order.menu_item_id)
        menu_item.quantity += order.quantity
        menu_item.save()

        # now delete...
        order.delete()

        if user.id == order.user_id:
            # save notification
            message = """You deleted your order (#{}) for
            {} with {} items.""".format(order.id, order.menu_item.meal.name,
                                        order.quantity)
            Notification.create({
                'user_id': user.id,
                'title': 'Order(#{}) deleted'.format(order.id),
                'message': message
            })

        return {
            'success': True,
            'message': 'Order successfully deleted.',
        }


class OrderListResource(Resource):
    @user_auth
    def get(self):

        # user should see his/her orders only...
        user = current_user()
        if user.is_admin():
            user_id = None
        else:
            user_id = user.id

        resp = Order.paginate(
            filters=decoded_qs(), user_id=user_id, name='orders')
        resp['message'] = 'Successfully retrieved orders.'
        resp['success'] = True
        return resp

    @user_auth
    @validate(PostRequest)
    def post(self):

        user = current_user()
        if not user.is_admin() and user.id != request.json['user_id']:
            return {
                'success': False,
                'message': 'Unauthorized to create this order.'
            }, 401

        # check we have enough quantity...
        menu_item = MenuItem.query.get(request.json['menu_item_id'])
        if menu_item.quantity < request.json['quantity']:
            message = None
            if menu_item.quantity > 0:
                message = 'Only {} meal(s) are available.'.format(
                    menu_item.quantity)
            else:
                message = 'No more orders can be made on this meal.'

            return {
                'success': False,
                'message': 'Validation error.',
                'errors': {
                    'quantity': [message]
                }
            }, 400

        # update quantity...
        menu_item.quantity -= request.json['quantity']
        menu_item.save()

        # create order...
        order = Order.create(request.json)

        message = """Your order (#{}) for
        {} with {} items was successfully received.""".format(
            order.id, order.menu_item.meal.name, order.quantity)

        # save notification
        Notification.create({
            'user_id': user.id,
            'title': 'Order(#{}) recieved'.format(order.id),
            'message': message
        })

        return {
            'success': True,
            'message': 'Successfully saved order.',
            'order': order.to_dict()
        }, 201
