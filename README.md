Flask-Inject
===

```python
pip install flask-inject
```

A micro dependency injection framework for Flask micro web framework :)

## Usage

Add Inject framework to the Flask App. It will setup the all necessary handlers. The method will also return a global injector which you can call map, get and apply on it.

```python
app = Flask(__name__)
inj = Inject(app)
```

Now you can attach some value to the global injector. When you call map on this global injector, it will attach the value to the corresponding key. Note that this is a global or shared injector, so the variables are shared cross all handlers. If you want have a injector for each different request, setup injector in before_request handler.

```python
inj.map(version="v1.0")
```

You can also add dependency to the per request injector so that the dependency will not be shared across the different requests. Here we try to open a mysql connection for each request and in tear down method, we will close this connection. We will use `@inject` decorator to inject the dependencies to the handler.

The injector itself can be injeteced to the target function. So we just inject the injector itself to the function so that we can add new dependency to it. Note that the injector object here is a per request injector and its parent is the global injector `inj` we declared before.

```python
@app.before_request
@inject("injector")
def before_request(injector):
    # Open mysql connection here
    mysql = "open mysql here"
    # Add mysql to the injector so that it will be available for handlers after before request
    injector.map(mysql=mysql)
```

Now we want to close the mysql connection in the teardown_request.

```python
@app.teardown_request
@inject("mysql")
def teardown_request(exception, mysql):
    # close mysql here
    mysql = "close mysql here"
```

Suppose we need show the app version in this handler. We add the version to the global injector and as we mentioned before, the global injector is the parent injector of each per request injector. So here the version is also available.

Using @inject decorator to inject the dependencies to the handler.

```python
@app.route("/version")
@inject("version")
def show_version(version):
    return version
```

Suppose we need access mysql database here. Since we add mysql to the injector before request. So just use @inject decorator to inject the dependencies to the handler.

```python
@app.route("/mysql")
@inject("mysql")
def show_mysql(mysql):
    # do something with mysql
    mysql = "exec a query"
    return "success"
```

Injector is also available in the function decorator. Suppose we have an authentication decorator which checks the auth_token parameter in the url parameters.

```python
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
```

Then authorized is available for injecting to the handler.

Using @inject decorator to inject the dependencies to the handler.

You can use the : operator to rename the injected dependency.

```python
@app.route("/auth")
@authentication
@inject("authorized:auth")
def show_auth(auth):
    if auth:
        return "200"
    return "401"
```
