import json
import unittest
from app.validation.validator import Validator

class TestValidator(unittest.TestCase):

    def setUp(self):
        self.V = Validator()

    def test_accepted(self):
        V = self.V
        V.set_rules({'field': 'accepted'})

        V.set_request({'field': '0'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('accepted', err_str)

        for val in [1, '1', True, 'true', 'yes']:
            V.set_request({'field': val})
            self.assertTrue(V.passes())

    def test_after(self):
        V = self.V
        V.set_rules({'field': 'after:2008-01-10'})

        V.set_request({'field': '2002-02-10'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('after', err_str)

        V.set_request({'field': '2009-01-10'})
        self.assertTrue(V.passes())

    def test_alpha(self):
        V = self.V
        V.set_rules({'field': 'alpha'})

        V.set_request({'field': '123 abc'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('letters', err_str)

        V.set_request({'field': 'abc def'})
        self.assertTrue(V.passes())

    def test_alpha_dash(self):
        V = self.V
        V.set_rules({'field': 'alpha_dash'})

        V.set_request({'field': '123 abc --- ###'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('dashes', err_str)
        self.assertIn('letters', err_str)

        V.set_request({'field': '123 abc ---'})
        self.assertTrue(V.passes())

    def test_alpha_num(self):
        V = self.V
        V.set_rules({'field': 'alpha_num'})

        V.set_request({'field': '1234 abc --'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('numbers', err_str)
        self.assertIn('letters', err_str)

        V.set_request({'field': '1234 hi there'})
        self.assertTrue(V.passes())

    def test_before(self):
        V = self.V
        V.set_rules({'field': 'before:2008-01-10'})

        V.set_request({'field': '2012-02-10'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('before', err_str)

        V.set_request({'field': '2007-01-10'})
        self.assertTrue(V.passes())

    def test_between_numeric(self):
        V = self.V
        V.set_rules({'field': 'between_numeric:0,100'})

        V.set_request({'field': 123})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('between', err_str)

        V.set_request({'field': 50})
        self.assertTrue(V.passes())

    def test_between_string(self):
        V = self.V
        V.set_rules({'field': 'between_string:0,10'})

        V.set_request({'field': 'xxxxxxxxxxxxx'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('between', err_str)
        self.assertIn('characters', err_str)

        V.set_request({'field': 'xxxx'})
        self.assertTrue(V.passes())

    def test_boolean(self):
        V = self.V
        V.set_rules({'field': 'boolean'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('true or false', err_str)

        for val in [1, '1', True, 'true', 0, '0', False, 'false' ]:
            V.set_request({'field': val})
            self.assertTrue(V.passes())

    def test_confirmed(self):
        V = self.V
        V.set_rules({'field': 'confirmed'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('confirmation', err_str)

        V.set_request({'field': 'hi', 'field_confirmation': 'hi there'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('confirmation', err_str)

        V.set_request({'field': 'hi', 'field_confirmation': 'hi'})
        self.assertTrue(V.passes())

    def test_date(self):
        V = self.V
        V.set_rules({'field': 'date'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('date', err_str)

        V.set_request({'field': '2018-02-12'})
        self.assertTrue(V.passes())

    def test_different(self):
        V = self.V
        V.set_rules({'field': 'different:field2'})

        V.set_request({'field': 'hi', 'field2': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('different', err_str)

        V.set_request({'field': 'hi', 'field2': 'there'})
        self.assertTrue(V.passes())

    def test_digits(self):
        V = self.V
        V.set_rules({'field': 'digits:5'})

        V.set_request({'field': 1.032})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('digits', err_str)

        V.set_request({'field': 1.0245})
        self.assertTrue(V.passes())

    def test_email(self):
        V = self.V
        V.set_rules({'field': 'email'})

        V.set_request({'field': 'user@mail'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('email', err_str)

        V.set_request({'field': 'user@mail.com'})
        self.assertTrue(V.passes())

    def test_found_in(self):
        V = self.V
        V.set_rules({'field': 'found_in:male,female'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('invalid', err_str)

        V.set_request({'field': 'male'})
        self.assertTrue(V.passes())

    def test_integer(self):
        V = self.V
        V.set_rules({'field': 'integer'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('integer', err_str)

        V.set_request({'field': 10})
        self.assertTrue(V.passes())

    def test_json(self):
        V = self.V
        V.set_rules({'field': 'json'})

        V.set_request({'field': '{hi man}'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('json', err_str)

        V.set_request({'field': json.dumps({'hi': 'there'})})
        self.assertTrue(V.passes())

    def test_most_numeric(self):
        V = self.V
        V.set_rules({'field': 'most_numeric:30'})

        V.set_request({'field': 309})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('not be greater than', err_str)

        V.set_request({'field': 20})
        self.assertTrue(V.passes())


    def test_most_string(self):
        V = self.V
        V.set_rules({'field': 'most_string:10'})

        V.set_request({'field': 'xxxxxxxxxxxxx'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('not be greater than', err_str)

        V.set_request({'field': 'xxxx'})
        self.assertTrue(V.passes())


    def test_least_numeric(self):
        V = self.V
        V.set_rules({'field': 'least_numeric:30'})

        V.set_request({'field': 20})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('least', err_str)

        V.set_request({'field': 200})
        self.assertTrue(V.passes())

    def test_least_string(self):
        V = self.V
        V.set_rules({'field': 'least_string:10'})

        V.set_request({'field': 'xxx'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('least', err_str)

        V.set_request({'field': 'xxxxxxxxxxxx'})
        self.assertTrue(V.passes())

    def test_numeric(self):
        V = self.V
        V.set_rules({'field': 'numeric'})

        V.set_request({'field': 'hi'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('number', err_str)

        V.set_request({'field': 10.0})
        self.assertTrue(V.passes())

        V.set_request({'field': -10})
        self.assertTrue(V.passes())

    def test_not_in(self):
        V = self.V
        V.set_rules({'field': 'not_in:xyz,abc'})

        V.set_request({'field': 'abc'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('invalid', err_str)

        V.set_request({'field': 'def'})
        self.assertTrue(V.passes())

    def test_regex(self):
        V = self.V
        V.set_rules({'field': 'regex:^\d+'})

        V.set_request({'field': 'test'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('format', err_str)

        V.set_request({'field': '123'})
        self.assertTrue(V.passes())

    def test_required(self):
        V = self.V
        V.set_rules({'field2': 'required'})

        V.set_request({'field': 'test'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('required', err_str)

        V.set_request({'field2': '123'})
        self.assertTrue(V.passes())

    def test_required_with(self):
        V = self.V
        V.set_rules({'field2': 'required_with:field1'})

        V.set_request({'field2': 'test'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('required when', err_str)

        V.set_request({'field2': '123', 'field1': 'hi'})
        self.assertTrue(V.passes())

    def test_required_without(self):
        V = self.V
        V.set_rules({'field2': 'required_without:field1'})

        V.set_request({'field3': 'test'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('required when', err_str)

        V.set_request({'field1': '123'})
        self.assertTrue(V.passes())

        V.set_request({'field2': '123'})
        self.assertTrue(V.passes())

    def test_same(self):
        V = self.V
        V.set_rules({'field2': 'same:field1'})

        V.set_request({'field1': 'test', 'field2': 'different'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('match', err_str)

        V.set_request({'field1': '123', 'field2': '123'})
        self.assertTrue(V.passes())

    def test_size_numeric(self):
        V = self.V
        V.set_rules({'field': 'size_numeric:30'})

        V.set_request({'field': 309})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('must be', err_str)

        V.set_request({'field': 30})
        self.assertTrue(V.passes())


    def test_size_string(self):
        V = self.V
        V.set_rules({'field': 'size_string:5'})

        V.set_request({'field': 'xxx'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('must be', err_str)

        V.set_request({'field': 'xxxxx'})
        self.assertTrue(V.passes())

    def test_string(self):
        V = self.V
        V.set_rules({'field': 'string'})

        V.set_request({'field': 10})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('string', err_str)

        V.set_request({'field': 'xxxxx'})
        self.assertTrue(V.passes())

    def test_url(self):
        V = self.V
        V.set_rules({'field': 'url'})

        V.set_request({'field': 'hi there'})
        self.assertTrue(V.fails())
        err_str = str(V.errors())
        self.assertIn('format is invalid', err_str)

        V.set_request({'field': 'http://www.google.com'})
        self.assertTrue(V.passes())

