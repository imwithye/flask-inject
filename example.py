from flask import Flask, request
from flask_inject import Inject, inject
from functools import wraps
import logging

app = Flask(__name__)

# Add Inject framework to the Flask App.
# It will setup the all necessary handlers.
# The method will also return a global injector which you can call map, get and apply on it.
inj = Inject(app)

# When you call map on this global injector, it will attach the value to the corresponding key.
# Note that this is a global or shared injector, so the variables are shared cross all handlers.
# If you want have a injector for each different request, setup injector in before_request handler.
inj.map(version="v1.0")

# get method will return the value of a key. This is a reclusive lookup strategy. That means if the key
# presents in the injector, it will simply return the value. But if the key does not present, it will
# lookup this key in its parent injector.

# This global injector has no parent. If "version" is not a valid key, it simply returns None. But global
# injector is the parent injector of per request injector, so the value inside global injector is available
# to each per request injector.
# Again, the value in global injector is shared cross all handlers.
v = inj.get("version")


# Set up per request injector.
# Here we try to open a mysql connection for each request and in tear down method, we will close this connection.
# Using @inject decorator to inject the dependencies to the handler.
@app.before_request
@inject("injector")
def before_request(injector):
    # Open mysql connection here
    mysql = "open mysql here"
    # Add mysql to the injector so that it will be available for handlers after before request
    injector.map(mysql=mysql)


# Now we want to close the mysql connection.
# Using @inject decorator to inject the mysql dependency to the handler.
@app.teardown_request
@inject("mysql")
def teardown_request(exception, mysql):
    # close mysql here
    mysql = "close mysql here"


# Suppose we need show the app version in this handler. We add the version to the global injector and as we
# mentioned before, the global injector is the parent injector of each per request injector. So here the version
# is also available.
# Using @inject decorator to inject the dependencies to the handler.
@app.route("/version")
@inject("version")
def show_version(version):
    return version


# Suppose we need access mysql database here.
# Since we add mysql to the injector before request.
# So just use @inject decorator to inject the dependencies to the handler.
@app.route("/mysql")
@inject("mysql")
def show_mysql(mysql):
    # do something with mysql
    mysql = "exec a query"
    return "success"


# Injector is also available in the function decorator.
# Suppose we have an authentication decorator which checks the auth_token parameter in the url parameters.
def authentication(f):
    @inject("injector")
    @wraps(f)
    def decorated_function(injector, *args, **kwargs):
        # Check the aut_token here
        auth_token = request.args.get("auth_token")
        authorized = False
        if auth_token is not None and len(auth_token) > 0:
            authorized = True
        # Now we can map the result to the injector
        injector.map(authorized=authorized)
        return f(*args, **kwargs)

    return decorated_function


# Then authorized is available for injecting to the handler.
# Using @inject decorator to inject the dependencies to the handler.
@app.route("/auth")
@authentication
@inject("authorized")
def show_auth(authorized):
    if authorized:
        return "200"
    return "401"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="localhost", port=8080, use_reloader=True)
