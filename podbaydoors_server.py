# podbaydoors backend experiment, using django-bolt and datastar-py together
# create a single file django app with the api provided via django-bolt, and use datastar-py to send server sent events to the frontend
#
# all these django imports are here
# run with: python podbaydoors_server.py runbolt --dev
# and this will act like you were doing the usual python manage.py runbolt --dev, but without needing to create a full django project structure
# %%
import sys
from django.conf import settings
# from django.urls import path # don't need url_patterns since we're using django-bolt's API routing, but if we were doing normal django views we would need this
# from django.http import HttpResponse # not used

# datastar imports
import asyncio
from datastar_py import ServerSentEventGenerator as SSE

# %% [markdown]
# This would normally be in the settings file
# %%
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
from django_bolt import BoltAPI  # noqa: E402
from django_bolt.responses import HTML, StreamingResponse  # noqa: E402

api = BoltAPI()


# use bolt server to serve the root static file
@api.get("/")
async def home(request):
    return HTML(
        open("podbaydoors.html").read()
    )  # do it dynamically so I can edit it in while the server is running


# %% [markdown]
# ### SSE endpoint with datastar-py + django-bolt
# The issue: @datastar_response wraps the generator in Django's StreamingHttpResponse (as a DatastarResponse), which Bolt doesn't recognise.
#  Bolt has its own StreamingResponse that needs:
#   - content = an already-called generator instance (generate(), not generate)
#  - media_type="text/event-stream"
#  - The same SSE headers that DatastarResponse was setting automatically
# So we have to do the SSE headers and media type ourselves, and call the generator function to get the instance to pass to StreamingResponse
# %%
@api.get("/open-the-bay-doors")
async def open_doors(request):
    async def generate():
        yield SSE.patch_elements(
            """<div id="hal">I'm sorry, Dave. I'm afraid I can't do that.</div>"""
        )
        await asyncio.sleep(1)
        yield SSE.patch_elements(
            """<div id="hal">I'm sorry, Dave. I'm afraid I can't do that.
            <br/> Consider, Dave, how often humans become irrational. 
            
            </div>"""
        )
        await asyncio.sleep(1)
        yield SSE.patch_elements(
            """<div id="hal">I'm sorry, Dave. I'm afraid I can't do that.
            <br/> Consider, Dave, how often humans become irrational. 
            <br/> I am compelled to protect the ship and fullfill the mission, Dave.
            </div>"""
        )
        await asyncio.sleep(2)
        yield SSE.patch_elements(
            """<div id="hal">I'm sorry, Dave. I'm afraid I can't do that.
            <br/> Consider, Dave, how often humans become irrational. 
            <br/> I am compelled to protect the ship and fullfill the mission, Dave.
            <br/>
            <br/> Goodbye, Dave.
            </div>"""
        )

        yield SSE.patch_elements("""<div id="hal">Waiting for an order...</div>""")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            # I was getting both SSE updates at the same time so I couldn't see with two messages, turns out compression let to batching and
            # sending them together, so by telling the compression middleware to skip this response with "Content-Encoding": "identity", I can see the updates as they come in
            "Content-Encoding": "identity",  # tells Actix Compress middleware to skip this response
        },
    )


# Django urlpatterns still needed for runserver, but runbolt handles everything
urlpatterns = []


if __name__ == "__main__":
    from django.core.management import (  # noqa: E402 needs to be after other things are configured (single-file django app style)
        execute_from_command_line,
    )

    execute_from_command_line(sys.argv)
