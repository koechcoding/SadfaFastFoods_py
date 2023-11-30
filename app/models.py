"""Contains the application's database models"""

import json
from app import db
from passlib.hash import bcrypt
from datetime import datetime, date
from sqlalchemy import cast, or_


class BaseModel:

    _fields = []
    _hidden = []
    _timestamps = True

    @classmethod
    def make(cls, data):
        instance = cls()
        instance.from_dict(data)
        return instance

    @classmethod
    def create(cls, data):
        instance = cls()
        instance.from_dict(data)
        instance.save()
        return instance

    def update(self, data):
        self.from_dict(data)
        self.save()
        return self

    def save(self):
        """Save current model"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete current model"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def _apply_db_filters(cls, query, filters):
        # if no filter query...
        if not filters:
            return query

        if 'search' in filters:
            # if the column has been specified...
            if ':' in filters['search']:
                # get column name and the value to match against
                column, value = filters['search'].split(':')

                # pattern to match against
                pattern = '%{}%'.format(value)
                try:
                    # cast to compare as string
                    column = cast(getattr(cls, column), db.String)
                    # now make the filter
                    query = query.filter(column.ilike(pattern))
                except AttributeError:
                    pass
            else:
                # comparison rules
                predicates = []

                # pattern to match against
                pattern = '%{}%'.format(filters['search'])

                # for all columns in this model...
                for column in cls._fields:
                    # cast this column to compare as string
                    column = cast(getattr(cls, column), db.String)
                    # add comparsion rule
                    predicates.append(column.ilike(pattern))

                # unpack all comparison rules using *or* rule
                query = query.filter(or_(*predicates))

        return query

    @classmethod
    def _apply_data_filters(cls, items, filters):
        if not filters:
            return [item.to_dict() for item in items]

        if 'fields' in filters:
            fields = filters['fields'].split(',')
            dict_items = [item.to_dict(fields=fields) for item in items]
        else:
            dict_items = [item.to_dict() for item in items]

        fields = None
        if 'related' in filters:
            # split the required related models
            related_models = filters['related'].split('|')

            # for all request models...
            for model in related_models:
                # if relation fields are specified...
                if ':' in model:
                    # get relation name and required fields
                    model_name, fields = model.split(':')
                    fields = fields.split(',')
                else:
                    model_name = model

                for item, dict_item in zip(items, dict_items):
                    #try:
                    dict_item[model_name] = getattr(
                        item, model_name).to_dict(fields=fields)
                    #except AttributeError:
                        #break
        return dict_items

    @classmethod
    def paginate(cls, filters=None, query=None, name='data'):
        # default query passed?
        if not query:
            query = cls.query
            # new first...
            query = query.order_by(cls.id.desc())
            # query with filters
            query = cls._apply_db_filters(query, filters)

        paginated = query.paginate(error_out=False)
        return {
            'pages': paginated.pages,
            'total': paginated.total,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'per_page': paginated.per_page,
            'next_page': paginated.next_num,
            'prev_page': paginated.prev_num,
            'current_count': len(paginated.items),
            name: cls._apply_data_filters(paginated.items, filters)
        }

    def from_dict(self, data):
        for field in self._fields:
            if field in data:
                setattr(self, field, data[field])
        return self

    def to_dict(self, fields=None):
        dict_repr = {}

        # if no fields specified, include all..
        if not fields or len(fields) == 0:
            fields = self._fields
            fields.extend(['id', 'created_at', 'updated_at'])

        if 'id' in fields:
            try:
                dict_repr['id'] = getattr(self, 'id')
            except AttributeError:
                pass

        # check if timestamps enabled and feed the results
        if self._timestamps:
            if 'created_at' in fields:
                try:
                    dict_repr['created_at'] = str(getattr(self, 'created_at'))
                except AttributeError:
                    pass
            if 'updated_at' in fields:
                try:
                    dict_repr['updated_at'] = str(getattr(self, 'updated_at'))
                except AttributeError:
                    pass

        # for every field declared...
        for field in fields:
            # if field is not hidden...
            if field not in self._hidden:
                try:
                    value = getattr(self, field)
                except AttributeError:
                    continue
                if isinstance(value, datetime) or isinstance(value, date):
                    dict_repr[field] = str(value)
                else:
                    dict_repr[field] = value
        return dict_repr

    def to_json(self, fields=None):
        return json.dumps(self.to_dict(fields=include))


class Blacklist(db.Model, BaseModel):
    """Holds JWT tokens revoked through user signing out"""

    __tablename__ = 'blacklist'
    _fields = ['token']

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, token=None):
        """Initialiaze the blacklist record"""
        self.token = token


class PasswordReset(db.Model, BaseModel):
    """Holds tokens for requested password resets"""

    __tablename__ = 'password_resets'
    _fields = ['token', 'user_id']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    token = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship(
        'User', backref=db.backref('password_resets', lazy='dynamic'))

    def __init__(self, token=None, user_id=None):
        """Initialiaze the blacklist record"""
        self.token = token
        self.user_id = user_id


class UserType:
    """Users roles"""
    SUPER_ADMIN = 0
    ADMIN = 1
    USER = 2

class User(db.Model, BaseModel):
    """This will have application's users details"""

    __tablename__ = 'users'
    _hidden = ['password', 'token']
    _fields = ['username', 'email', 'password', 'token', 'role']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256))
    email = db.Column(db.String(1024), unique=True)
    password = db.Column(db.String(256))
    token = db.Column(db.String(1024))
    role = db.Column(db.Integer, default=UserType.USER)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self,
                 username=None,
                 email=None,
                 token=None,
                 password=None,
                 role=UserType.USER):
        """Initialize the user"""
        self.email = email
        self.role = role
        self.username = username
        self.token = token
        if password:
            self.password = bcrypt.encrypt(password)

    def from_dict(self, data):
        for field in self._fields:
            if field in data:
                if field == 'password':
                    self.password = bcrypt.encrypt(data[field])
                else:
                    setattr(self, field, data[field])

    def validate_password(self, password):
        """Checks the password is correct against the password hash"""
        return bcrypt.verify(password, self.password)

    def is_admin(self):
        """Checks if current user is a caterer"""
        return self.role in [UserType.ADMIN, UserType.SUPER_ADMIN]

    def is_super_admin(self):
        """Checks if current user is a caterer"""
        return self.role == UserType.SUPER_ADMIN



class Menu(db.Model, BaseModel):
    """Holds the menus"""

    __tablename__ = 'menus'
    _fields = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name=None):
        """Initialize the menu"""
        self.name = name

    @classmethod
    def _apply_data_filters(cls, items, filters):
        # first apply default filters
        dict_items = BaseModel._apply_data_filters(items, filters)

        # compare as dates
        timestamp = cast(cls.created_at, db.DATE)

        date_filter = None
        # time specified for menu items
        if filters and 'time' in filters:
            time = filters['time']
            # history menu items...
            if time == 'history':
                date_filter = timestamp < date.today()

            # today's menu items...
            elif time == 'today':
                date_filter = timestamp == date.today()

            # menu items date specified...
            elif time != 'all':
                from app.utils import str_to_date
                time = str_to_date(time)
                if time is not None:
                    date_filter = timestamp == time

        # default is today's
        else:
            date_filter = timestamp == date.today()

        # for every menu, feed menu items...
        for item, dict_item in zip(items, dict_items):
            if date_filter is not None:
                menu_items = item.menu_items.filter(date_filter).all()
            else:
                menu_items = item.menu_items.all()

            result = []
            for menu_item in menu_items:
                dict_repr = menu_item.to_dict()
                del dict_repr['menu']
                result.append(dict_repr)
            dict_item['menu_items'] = result
        return dict_items


class MenuItem(db.Model, BaseModel):
    """Holds the menu item of the application"""

    __tablename__ = 'menu_items'
    _fields = ['menu_id', 'meal_id', 'quantity']

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE'))
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    # relationship with the menu
    menu = db.relationship(
        'Menu', backref=db.backref('menu_items', lazy='dynamic'))

    # relationship with the meal
    meal = db.relationship(
        'Meal', backref=db.backref('menu_items', lazy='dynamic'))

    def __init__(self, menu_id=None, meal_id=None, quantity=1):
        """Initialize a meal item"""
        self.menu_id = menu_id
        self.meal_id = meal_id
        self.quantity = quantity

    def to_dict(self, fields=None):
        dict_repr = super().to_dict(fields=fields)
        dict_repr['meal'] = self.meal.to_dict() if self.meal else {}
        dict_repr['menu'] = self.menu.to_dict() if self.menu else {}
        if dict_repr.get('menu_id'):
            del dict_repr['menu_id']
        if dict_repr.get('meal_id'):
            del dict_repr['meal_id']
        return dict_repr

    @classmethod
    def _apply_db_filters(cls, query, filters):
        if not filters:
            return query

        # search in related
        if 'search' in filters:
            pattern = '%{}%'.format(filters['search'])
            query = query.filter(
                or_(MenuItem.meal.has(Meal.name.ilike(pattern)),
                    MenuItem.menu.has(Menu.name.ilike(pattern))))

        # time specified for orders
        if 'time' in filters:
            time = filters['time']
            # compare as dates
            timestamp = cast(cls.created_at, db.DATE)

            # order history...
            if time == 'history':
                query = query.filter(timestamp < date.today())

            # today's orders...
            elif time == 'today':
                query = query.filter(timestamp == date.today())

            # no filter for all orders...
            elif time == 'all':
                pass

            # orders date specified...
            else:
                from app.utils import str_to_date
                time = str_to_date(time)
                if time:
                    query = query.filter(timestamp == time)

        return query

    @classmethod
    def paginate(cls, filters=None, query=None, name='data'):
        # if user menu items specified by date...
        query = cls.query.order_by(cls.id.desc())
        query = cls._apply_db_filters(query, filters)
        return super().paginate(filters=filters, query=query, name=name)

class Meal(db.Model, BaseModel):
    """Holds a meal in the application"""

    __tablename__ = 'meals'
    _fields = ['name', 'cost', 'img_url']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    cost = db.Column(db.Float(2))
    img_url = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name=None, cost=None, img_url=None):
        """Initialize a meal"""
        self.name = name
        self.cost = cost
        self.img_url = img_url


class OrderStatus:
    """Order Status"""
    PENDING = 1
    ACCEPTED = 2
    REVOKED = 3


class Order(db.Model, BaseModel):
    """Holds an order of the application"""

    __tablename__ = 'orders'
    _fields = ['quantity', 'menu_item_id', 'user_id', 'status']

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.Integer, default=OrderStatus.PENDING)
    menu_item_id = db.Column(
        db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    # relationship with the menu items
    menu_item = db.relationship(
        'MenuItem', backref=db.backref('orders', lazy='dynamic'))

    user = db.relationship(
        'User', backref=db.backref('orders', lazy='dynamic'))

    @classmethod
    def _apply_db_filters(cls, query, filters):
        if not filters:
            return query

        # search in related
        if 'search' in filters:
            pattern = '%{}%'.format(filters['search'])
            query = query.filter(
                or_(Order.user.has(User.username.ilike(pattern)),
                    Order.user.has(User.email.ilike(pattern)),
                    Order.menu_item.has(MenuItem.menu.has(Menu.name.ilike(pattern))),
                    Order.menu_item.has(MenuItem.meal.has(Meal.name.ilike(pattern))))
            )

        # time specified for orders
        if 'time' in filters:
            time = filters['time']
            # compare as dates
            timestamp = cast(cls.created_at, db.DATE)

            # order history...
            if time == 'history':
                query = query.filter(timestamp < date.today())

            # today's orders...
            elif time == 'today':
                query = query.filter(timestamp == date.today())

            # no filter for all orders...
            elif time == 'all':
                pass

            # orders date specified...
            else:
                from app.utils import str_to_date
                time = str_to_date(time)
                if time:
                    query = query.filter(timestamp == time)

        return query

    @classmethod
    def paginate(cls, filters=None, query=None, user_id=None, name='data'):
        # if user orders specified...
        query = cls.query
        if user_id:
            query = query.filter(cls.user_id == user_id)
        query = query.order_by(cls.id.desc())
        query = cls._apply_db_filters(query, filters)
        return super().paginate(filters=filters, query=query, name=name)

    def __init__(self, menu_item_id=None, user_id=None, quantity=None):
        """Initialize the order"""
        self.user_id = user_id
        self.quantity = quantity
        self.menu_item_id = menu_item_id


class Notification(db.Model, BaseModel):
    """Notification model"""

    __tablename__ = 'notifications'
    _fields = ['title', 'message', 'user_id']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    message = db.Column(db.String(2048))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    # relationship with a user
    user = db.relationship(
        'User', backref=db.backref('notifications', lazy='dynamic'))

    @classmethod
    def paginate(cls, filters=None, query=None, user_id=None, name='data'):
        # if user notifications specified...
        query = cls.query
        if user_id:
            query = query.filter(cls.user_id == user_id)
        query = query.order_by(cls.id.desc())
        return super().paginate(filters=filters, query=query, name=name)

    def __init__(self, title=None, message=None, user_id=None):
        """Initialize the notification"""
        self.title = title
        self.message = message
        self.user_id = user_id
