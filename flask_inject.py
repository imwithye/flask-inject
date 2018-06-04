from flask import g
from functools import wraps


class Inject(object):
    class InjectException(Exception):
        def __init__(self, message):
            self.message = message

    class Injector(object):
        def __init__(self, parent=None):
            if parent is not None and not isinstance(parent, Inject.Injector):
                raise Inject.InjectException("Parent injector shall be an instance of Injector but get %s"
                                             % str(type(parent)))
            self.parent = parent
            self._base = dict()

        def map(self, *args, **kwargs):
            for k, v in kwargs.items():
                if not isinstance(k, str):
                    raise Inject.InjectException("Key shall be an instance of str but get %s" % str(type(k)))
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
                if not isinstance(key, str):
                    raise Inject.InjectException("Key shall be an instance of str but get %s" % str(type(key)))
                key_pair = key.split(":")
                if not 1 <= len(key_pair) <= 2:
                    raise Inject.InjectException("Key shall only contain at most one ':'")
                value = self.get(key_pair[0])
                if len(key_pair) == 1:
                    kwargs[key_pair[0]] = value
                else:
                    kwargs[key_pair[1]] = value
            return func(*args, **kwargs)

    def __init__(self, app):
        self._injector = self.Injector()
        self._app = app
        if app is not None:
            self._init_app(app)

    def _init_app(self, app):
        app.before_request(self._before_request)
        app.before_first_request(self._before_request)

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
            if _injector is None or not isinstance(_injector, Inject.Injector):
                raise Inject.InjectException("Injector is not found in flask g variable")
            return _injector.apply(keys, f, args, kwargs)

        return decorated_function

    return decorator
