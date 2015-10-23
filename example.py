from flask import Flask
from flask_inject import Inject, inject
from functools import wraps
import logging

app = Flask(__name__)
Inject(app)


@app.before_request
@inject("injector")
def before_request(injector):
    injector.map("version", "v1.0")
    mysql = "mysql connection"
    injector.map("mysql", mysql)


@app.teardown_request
@inject("mysql")
def teardown_request(exception, mysql):
    logging.info("teardown request")
    logging.info(mysql)


def authentication():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_inject import injector
            injector().map("auth", "Auth Passed")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/headers")
@inject("headers")
def show_headers(headers):
    ret = ""
    for key, value in headers.iteritems():
        ret += "%s: %s<br />" % (key, value)
    return ret


@app.route("/version")
@inject("version")
def show_version(version):
    return version


@app.route("/mysql")
@inject("mysql")
def show_mysql(mysql):
    if mysql:
        return "success"
    return "fail"


@app.route("/auth")
@authentication()
@inject("auth")
def show_auth(auth):
    return auth


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="localhost", port=8080, use_reloader=True)
