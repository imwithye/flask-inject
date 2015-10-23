from flask import g, request
from functools import wraps


class Inject(object):
    class Injector(object):
        def __init__(self):
            self._base = dict()

        def map(self, key, value):
            assert isinstance(key, str)
            self._base[key] = value

        def lookup(self, key):
            return self._base.get(key)

        def apply(self, keys, func, args, kwargs):
            for key in keys:
                kwargs[key] = self.lookup(key)
            return func(*args, **kwargs)

    def __init__(self, app):
        self.app = app
        if app is not None:
            self._init_app(app)

    def _init_app(self, app):
        app.before_request(self.before_request)

    def before_request(self):
        injector = self.Injector()
        injector.map("injector", injector)
        injector.map("app", self.app)
        injector.map("request", request)
        injector.map("headers", request.headers)
        injector.map("cookies", request.cookies)
        g._injector = injector


def inject(*keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            injector = g.get("_injector")
            assert injector is not None
            for key in keys:
                assert isinstance(key, str)
            return injector.apply(keys, f, args, kwargs)

        return decorated_function

    return decorator
