from functools import wraps


def validate(Request):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            req = Request()
            req.validate()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
