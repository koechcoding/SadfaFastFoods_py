"""Translates validation error messages for the response"""


messages = {
    'accepted': 'The :field: must be accepted.',
    'after': 'The :field: must be a date after :other:.',
    'alpha': 'The :field: may contain only letters.',
    'alpha_dash': 'The :field: may only contain letters, numbers, and dashes.',
    'alpha_num': 'The :field: may contain only letters and numbers.',
    'array': 'The :field: must be an array.',
    'before': 'The :field: must be a date before :other:.',
    'between': 'The :field: must be between :least: and :most:.',
    'between_string': 'The :field: must be between :least: and :most: characters.',
    'between_numeric': 'The :field: must be between :least: and :most:.',
    'boolean': 'The :field: must be either true or false.',
    'confirmed': 'The :field: confirmation does not match.',
    'date': 'The :field: is not a valid date.',
    'different': 'The :field: and :other: must be different.',
    'digits': 'The :field: must be :length: digits.',
    'email': 'The :field: must be a valid email address.',
    'exists': 'The selected :field: is invalid.',
    'found_in': 'The selected :field: is invalid.',
    'integer': 'The :field: must be an integer.',
    'json': 'The :field: must be valid json format.',
    'most_string': 'The :field: must not be greater than :most: characters.',
    'most_numeric': 'The :field: must not be greater than :most:.',
    'least_string': 'The :field: must be at least :least: characters.',
    'least_numeric': 'The :field: must be at least :least:.',
    'not_in': 'The selected :field: is invalid.',
    'numeric': 'The :field: must be a number.',
    'positive': 'The :field: must be a positive number.',
    'regex': 'The :field: format is invalid.',
    'required': 'The :field: field is required.',
    'required_with': 'The :field: field is required when :other: is present.',
    'required_without': 'The :field: field is required when :other: si not present.',
    'same': 'The :field: and :other: must match.',
    'size_string': 'The :field: must be :size: characters.',
    'size_numeric': 'The :field: must be :size:.',
    'string': 'The :field: must be a string.',
    'unique': 'The :field: is already taken.',
    'url': 'The :field: format is invalid.',
}


def trans(rule, fields):
    message = messages[rule] 
    for k, v in fields.items():
        message = message.replace(k, v).replace('_', ' ')
    return message

