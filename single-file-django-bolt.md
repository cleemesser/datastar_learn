# Single-file Django app with django-bolt
- references: [nanodjango](https://lincolnloop.com/blog/single-file-apps-with-nanodjango), uses django-ninja for api
- django-bolt  - seems early stage but looks promising as being an all-in-one production ready plug and play soln
- litestar - seems more mature than django-bolt maybe
## The problem

`django-bolt` discovers `BoltAPI` instances by scanning for `api.py` or `bolt_api.py` files in installed apps. In a single-file Django app, everything lives in one script (e.g. `podbaydoors_server.py`), so the auto-discovery never finds the `api` variable.

Internally, `runbolt` builds the discovery candidate list like this:

```python
project_name = settings.ROOT_URLCONF.split(".")[0]
# e.g. ROOT_URLCONF = "__main__"  →  tries "__main__.api:api"  (doesn't exist)
```

## The fix

Add `BOLT_API` to `settings.configure()` pointing directly at the module-level `api` variable:

```python
settings.configure(
    ...
    BOLT_API=["__main__:api"],
)
```

`BOLT_API` is a list of `"module:variable"` strings. `runbolt` resolves them via
`importlib.import_module(module_path)`. When the app is run as a script,
`sys.modules["__main__"]` is already populated, so `importlib.import_module("__main__")`
returns the running script and finds `api` there.

## Important: import order

`django_bolt` must be imported **after** `settings.configure()` is called:

```python
settings.configure(
    INSTALLED_APPS=["django_bolt", ...],
    BOLT_API=["__main__:api"],
)

from django_bolt import BoltAPI  # after settings

api = BoltAPI()
```
## if you are doing the typical "flask-style" simple single file app then you probably just want to run the bolt server alone
```
python podbaydoors_server.py runbolt --port 8000 # or whatever port you want
```

## Running the two servers

Django-bolt runs a separate Rust/Actix Web server, not Django's dev server. You could need both if you are using the regular django server

```bash
# Terminal 1 — Django (serves HTML, standard views)
python podbaydoors_server.py runserver 8080

# Terminal 2 — Bolt (serves the BoltAPI routes)
python podbaydoors_server.py runbolt --port 8001
```

## Frontend note

Because Bolt runs on a different port, datastar `@get` calls must include the full origin:

```html
<button data-on:click="@get('http://localhost:8001/open-the-bay-doors')">
```

In production, put a reverse proxy (nginx, Caddy, etc.) in front of both servers to avoid this.

## Minimal working example

```python
# myapp.py — run with: python myapp.py runserver 8080
#             or:      python myapp.py runbolt --port 8001
import sys
from django.conf import settings
from django.urls import path
from django.http import HttpResponse

settings.configure(
    DEBUG=True,
    SECRET_KEY="change-me",
    ROOT_URLCONF=__name__,
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "django_bolt"],
    BOLT_API=["__main__:api"],
)

from django_bolt import BoltAPI

api = BoltAPI()

def home(request):
    return HttpResponse("<h1>Hello</h1>")

urlpatterns = [path("", home)]

@api.get("/hello")
async def hello(request):
    return {"message": "hello"}

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```
