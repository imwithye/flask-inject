from flask import g
from functools import wraps


class Inject(object):
    class Injector(object):
        def __init__(self, parent=None):
            if parent is not None:
                assert isinstance(parent, Inject.Injector)
            self.parent = parent
            self._base = dict()

        def map(self, *args, **kwargs):
            for k, v in kwargs.iteritems():
                assert isinstance(k, str)
                self._base[k] = v
            return self

        def get(self, key):
            value = self._base.get(key)
            if value is None:
                if self.parent is not None:
                    return self.parent.get(key)
                return None
            return value

        def apply(self, keys, func, args, kwargs):
            for key in keys:
                kwargs[key] = self.get(key)
            return func(*args, **kwargs)

    def __init__(self, app):
        self._injector = self.Injector()
        self._app = app
        if app is not None:
            self._init_app(app)

    def _init_app(self, app):
        app.before_request(self._before_request)

    def _before_request(self):
        _injector = self.Injector(self._injector)
        _injector.map(injector=_injector)
        g._injector = _injector

    def map(self, *args, **kwargs):
        self._injector.map(*args, **kwargs)
        return self

    def get(self, key):
        return self._injector.get(key)

    def apply(self, keys, func, args, kwargs):
        return self._injector.apply(keys, func, args, kwargs)


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
