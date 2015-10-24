from flask import g
from functools import wraps


class Inject(object):
    class Injector(object):
        def __init__(self):
            self._base = dict()

        def map(self, *args, **kwargs):
            for k, v in kwargs.iteritems():
                self.map_to(k, v)

        def map_to(self, key, value):
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
        _injector = self.Injector()
        _injector.map(injector=_injector)
        g._injector = _injector


def inject(*keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            _injector = g.get("_injector")
            assert _injector is not None
            for key in keys:
                assert isinstance(key, str)
            return _injector.apply(keys, f, args, kwargs)

        return decorated_function

    return decorator
