from flask import Flask
from flask_inject import Inject, inject
from functools import wraps
import logging

app = Flask(__name__)
Inject(app)


@app.before_request
@inject("injector")
def before_request(injector):
    version = "v1.0"
    mysql = "mysql connection"
    injector.map(version=version, mysql=mysql)


@app.teardown_request
@inject("mysql")
def teardown_request(exception, mysql):
    logging.info("teardown request")
    logging.info(mysql)


def authentication():
    def decorator(f):
        @inject("injector")
        @wraps(f)
        def decorated_function(injector, *args, **kwargs):
            injector.map(auth=True)
            return injector.apply(["auth"], f, args, kwargs)

        return decorated_function

    return decorator


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
def show_auth(auth):
    if auth:
        return "200"
    return "401"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="localhost", port=8080, use_reloader=True)
