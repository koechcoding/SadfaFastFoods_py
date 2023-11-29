import re
import json
from datetime import date
from .translator import trans
from app.models import (User, Meal, Menu, MenuItem, Order, Notification,
                        PasswordReset)


class Validator:
    def __init__(self, request={}, rules={}):
        """Initialize rules and models"""
        self._rules = rules
        self._request = request
        self._errors = {}

    def passes(self):
        # for every field and its rules...
        for field, rules in self._rules.items():
            # for each of current field's rule...
            for rule in rules.split('|'):
                # split rule name and its parameters...
                rule_name = rule_params = None
                if ':' in rule:
                    rule_name, rule_params = rule.split(':')
                else:
                    rule_name = rule
                func_name = '_' + rule_name  # rule function name

                # field exists? ...only when not executing required like rule
                if rule_name in ['required', 'required_without'] or \
                        self._request.get(field):

                    # check if we have a function for this rule..
                    if not hasattr(self, func_name):
                        raise Exception('Validator: no rule named ' +
                                        rule_name)

                    # now get that function and call it with the arguments
                    func = getattr(self, func_name)
                    is_valid, message = func(field=field, params=rule_params)

                    # if rule does not pass save the error and bail
                    if not is_valid:
                        if not self._errors.get(field):
                            self._errors[field] = []
                        self._errors[field].append(message)
                        return False
        return True

    def reset(self):
        self._rules = {}
        self._errors = {}
        self._request = {}

    def fails(self):
        return not self.passes()

    def errors(self):
        return self._errors

    def set_rules(self, rules):
        self._rules = rules

    def set_request(self, request):
        self._request = request

    def _accepted(self, field=None, **kwargs):
        valid = [1, '1', True, 'true', 'yes']
        if self._request[field] not in valid:
            return (False, trans('accepted', {':field:': field}))
        return (True, '')

    def _after(self, field=None, params=None, **kwargs):
        field_date = self.__to_date(self._request[field])
        if not field_date:
            return (False, trans('date', {':field:': field}))
        after_date = self.__to_date(params)
        if not after_date:
            raise Exception('Validator: after date must match YYYY-MM-DD')

        if field_date < after_date:
            return (False, trans('after', {
                ':field:': field,
                ':after': params
            }))
        return (True, '')

    def _alpha(self, field=None, **kwargs):
        value = str(self._request[field]).replace(' ', '')
        if not value.isalpha():
            return (False, trans('alpha', {':field:': field}))
        return (True, '')

    def _alpha_dash(self, field=None, **kwargs):
        value = str(self._request[field]).replace('-', '').replace(' ', '')
        if not value.isalnum():
            return (False, trans('alpha_dash', {':field:': field}))
        return (True, '')

    def _alpha_num(self, field=None, **kwargs):
        value = str(self._request[field]).replace(' ', '')
        if not value.isalnum():
            return (False, trans('alpha_num', {':field:': field}))
        return True, ''

    def _before(self, field=None, params=None, **kwargs):
        field_date = self.__to_date(self._request[field])
        if not field_date:
            return (False, trans('date', {':field:': field}))
        before_date = self.__to_date(params)
        if not before_date:
            raise Exception('Validator: before date must match YYYY-MM-DD')

        if field_date > before_date:
            return (False,
                    trans('before', {
                        ':field:': field,
                        ':after:': params
                    }))
        return (True, '')

    def _between_numeric(self, field=None, params=None, **kwargs):
        least, most = [int(x) for x in params.split(',')]
        value = self._request[field]
        if least > value or value > most:
            return (False,
                    trans(
                        'between_numeric', {
                            ':field:': field,
                            ':least:': str(least),
                            ':most:': str(most)
                        }))
        return (True, '')

    def _between_string(self, field=None, params=None, **kwargs):
        least, most = [int(x) for x in params.split(',')]
        value = len(self._request[field])
        if least > value or value > most:
            return (False,
                    trans(
                        'between_string', {
                            ':field:': field,
                            ':least:': str(least),
                            ':most:': str(most)
                        }))
        return (True, '')

    def _boolean(self, field=None, **kwargs):
        valid = [1, '1', True, 'true', 0, '0', False, 'false']
        if self._request[field] not in valid:
            return (False, trans('boolean', {':field:': field}))
        return (True, '')

    def _confirmed(self, field=None, **kwargs):
        confirm_field = field + '_confirmation'
        if self._request.get(confirm_field) is None or  \
                self._request[field] != self._request[confirm_field]:
            return (False, trans('confirmed', {':field:': field}))
        return (True, '')

    def _date(self, field, **kwargs):
        ok = True
        date_lst = self._request[field].split('-')
        ok = len(date_lst) == 3
        if ok:
            try:
                year, month, day = [int(x) for x in date_lst]
                date(year, month, day)
            except (ValueError, TypeError):
                ok = False
        if not ok:
            return (False, trans('date', {':field:': field}))
        return (True, '')

    def _different(self, field=None, params=None, **kwargs):
        if self._request.get(field) == self._request.get(params):
            return (False,
                    trans('different', {
                        ':field:': field,
                        ':other:': params
                    }))
        return (True, '')

    def _digits(self, field=None, params=None, **kwargs):
        length = int(params)
        is_numeric, msg = self._numeric(field=field)
        if not is_numeric:
            return (False, msg)
        str_repr = str(self._request[field])

        if '.' in str_repr: length += 1
        if len(str_repr) != length:
            return (False,
                    trans('digits', {
                        ':field:': field,
                        ':length:': str(length)
                    }))
        return (True, '')

    def _email(self, field=None, **kwargs):
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$",
                        str(self._request[field])):
            return (False, trans('email', {':field:': field}))
        return (True, '')

    def _exists(self, field=None, params=None, **kwargs):
        modelName, column = params.split(',')
        model = eval(modelName)
        if not model.query.filter_by(**{column: self._request[field]}).first():
            return (False, trans('exists', {':field:': field}))
        return (True, '')

    def _found_in(self, field=None, params=None, **kwargs):
        valid = params.split(',')
        if not str(self._request[field]) in valid:
            return (False, trans('found_in', {':field:': field}))
        return (True, '')

    def _integer(self, field=None, **kwargs):
        try:
            int(self._request[field])
        except ValueError:
            return (False, trans('integer', {':field:': field}))
        return (True, '')

    def _json(self, field, **kwargs):
        try:
            json.loads(self._request[field])
        except ValueError:
            return (False, trans('json', {':field:': field}))
        return (True, '')

    def _most_numeric(self, field=None, params=None, **kwargs):
        size = float(params)
        if self._request[field] > size:
            return (False,
                    trans('most_numeric', {
                        ':field:': field,
                        ':most:': str(size)
                    }))
        return (True, '')

    def _most_string(self, field=None, params=None, **kwargs):
        size = int(params)
        if len(self._request[field]) > size:
            return (False,
                    trans('most_string', {
                        ':field:': field,
                        ':most:': str(size)
                    }))
        return (True, '')

    def _least_numeric(self, field=None, params=None, **kwargs):
        size = int(params)
        if self._request[field] < size:
            return (False,
                    trans('least_numeric', {
                        ':field:': field,
                        ':least:': str(size)
                    }))
        return (True, '')

    def _least_string(self, field=None, params=None, **kwargs):
        size = int(params)
        if len(self._request[field]) < size:
            return (False,
                    trans('least_string', {
                        ':field:': field,
                        ':least:': str(size)
                    }))
        return (True, '')

    def _numeric(self, field=None, **kwargs):
        try:
            float(self._request[field])
        except ValueError:
            return (False, trans('numeric', {':field:': field}))
        return (True, '')

    def _not_in(self, field=None, params=None, **kwargs):
        found_in, _ = self._found_in(field, params)
        if found_in:
            return (False,
                    trans('not_in', {
                        ':field:': field,
                        ':not_in:': params
                    }))
        return (True, '')

    def _positive(self, field=None, params=None, **kwargs):
        try:
            val = float(self._request[field])
            if val < 0:
                raise ValueError()
        except ValueError:
            return (False, trans('positive', {':field:': field}))
        return (True, '')

    def _regex(self, field=None, params=None, **kwargs):
        if not re.match(params, str(self._request[field])):
            return (False, trans('regex', {':field:': field}))
        return (True, '')

    def _required(self, field=None, params=None, **kwargs):
        if self._request.get(field) is None:
            return (False, trans('required', {':field:': field}))
        return (True, '')

    def _required_with(self, field=None, params=None, **kwargs):
        if self._request.get(field) and self._request.get(params) is None:
            return (False,
                    trans('required_with', {
                        ':field:': field,
                        ':other:': params
                    }))
        return (True, '')

    def _required_without(self, field=None, params=None, **kwargs):
        if self._request.get(params) is None \
                and self._request.get(field) is None:
            return (False,
                    trans('required_without', {
                        ':field:': field,
                        ':other:': params
                    }))
        return (True, '')

    def _same(self, field=None, params=None, **kwargs):
        if self._request[field] != self._request[params]:
            return (False, trans('same', {
                ':field:': field,
                ':other:': params
            }))
        return (True, '')

    def _size_numeric(self, field=None, params=None, **kwargs):
        size = float(params)
        if abs(self._request[field] - size) > 0.01:
            return (False,
                    trans('size_numeric', {
                        ':field:': field,
                        ':size:': str(size)
                    }))
        return (True, '')

    def _size_string(self, field=None, params=None, **kwargs):
        size = int(params)
        if len(self._request[field]) != size:
            return (False,
                    trans('size_string', {
                        ':field:': field,
                        ':size:': str(size)
                    }))
        return (True, '')

    def _string(self, field=None, params=None, **kwargs):
        if not isinstance(self._request[field], str):
            return (False, trans('string', {':field:': field}))
        return (True, '')

    def _unique(self, field=None, params=None, **kwargs):
        modelName, column = params.split(',')
        model = eval(modelName)
        predicate = getattr(model, column).ilike(self._request[field])
        if model.query.filter(predicate).first():
            return (False, trans('unique', {':field:': field}))
        return (True, '')

    def _url(self, field=None, params=None, **kwargs):
        ptn = '^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        value = self._request[field]
        if not re.match(ptn, value) and value != '#':
            return (False, trans('url', {':field:': field}))
        return (True, '')

    def __to_date(self, date_str):
        date_lst = date_str.split('-')
        if len(date_lst) == 3:
            try:
                year, month, day = [int(x) for x in date_lst]
                return date(year, month, day)
            except ValueError:
                return None
        return None
