# podbaydoors backend example
# create a single file django app with the api provided via django-bolt, and use datastar-py to send server sent events to the frontend
# all these django imports are here
# run with: python podbaydoors_server.py runbolt --dev
# and this will act like you were doing the usual python manage.py runbolt --dev, but without needing to create a full django project structure
import sys
from django.conf import settings
# from django.urls import path # don't need url_patterns since we're using django-bolt's API routing, but if we were doing normal django views we would need this
# from django.http import HttpResponse # not used

# datastar imports
import asyncio
from datastar_py import ServerSentEventGenerator as SSE

from datastar_py.django import datastar_response


settings.configure(
    DEBUG=True,
    SECRET_KEY="a-bad-secret-key",  # Insecure, use a proper key in production
    ROOT_URLCONF=__name__,
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django_bolt",
    ],
    BOLT_API=["__main__:api"],
)

# django-bolt imports after settings
from django_bolt import BoltAPI
from django_bolt.responses import HTML

api = BoltAPI()


# use bolt server to serve the root static file
@api.get("/")
async def home(request):
    return HTML(
        open("podbaydoors.html").read()
    )  # do it dynamically so I can edit it in while the server is running


@api.get("/open-the-bay-doors")
@datastar_response
async def open_doors(request):
    yield SSE.patch_elements(
        # note this uses a special unicode char for the apostrophes
        """<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>"""
    )
    await asyncio.sleep(1)
    yield SSE.patch_elements("""<div id="hal">Waiting for an order...</div>""")


# Django urlpatterns still needed for runserver, but runbolt handles everything
urlpatterns = []


if __name__ == "__main__":
    from django.core.management import (
        execute_from_command_line,
    )  # needs to be after other things are configured (single-file django app style)

    execute_from_command_line(sys.argv)
