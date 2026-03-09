# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "nanodjango-bolt", "datastar-py"]
# ///
# uv run chat.py should run as well or "pipx run"
import asyncio
from django_bolt.serializers import Serializer
from typing_extensions import Annotated

from django.db import models
from django.http import HttpResponse
from nanodjango import Django
from nanodjango_bolt import BoltAPI
from msgspec import Meta
from django_bolt.serializers import Serializer
from django_bolt.responses import Response, StreamingResponse

from datastar_py import ServerSentEventGenerator as SSE


new_message_event = asyncio.Event()

app = Django(
    # Avoid clashes with other examples
    SQLITE_DATABASE="chat.sqlite3",
    MIGRATIONS_DIR="chat_migrations",
)

bolt = BoltAPI()

# add this to the admin file as well
# @app.admin(list_display=["id","created_at","text_msg"])
class Message(models.Model):
    text_msg = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)


chat_html = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with Friends</title>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@5/themes.css" rel="stylesheet" type="text/css" />
    <link href="https://cdn.jsdelivr.net/npm/daisyui@5/full.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.8/bundles/datastar.js"></script>
</head>

<body data-signals="{text_msg: ''}" data-theme="dim" class="min-h-screen bg-base-200 flex items-center justify-center p-4">
    <div class="card bg-base-100 shadow-xl w-full max-w-lg">
        <div class="card-body">
            <h1 class="card-title text-2xl">Chat with Friends</h1>
            <div id="chat-container" data-init="@get('/api/messages')"
                class="h-80 overflow-y-auto rounded-box bg-base-200 p-4 space-y-2">
                <div id="chat-content"></div>
            </div>
            <div class="flex gap-2 mt-2">
                <textarea id="msg-input" placeholder="Type your message here..."
                    cols="20" rows="4"
                    class="textarea textarea-bordered flex-1"
                    data-bind="text_msg"
                    data-on:keydown="evt.key === 'Enter' && !evt.shiftKey && @post('/api/new_message'); text_msg = ''"></textarea>
                <button id="msg-send-button" class="btn btn-primary"
                    data-on:click="@post('/api/new_message'); text_msg = ''">Send</button>
            </div>
        </div>
    </div>
</body>

</html>
"""

@app.route("/")
def hello_world(request):
    return HttpResponse(chat_html, content_type="text/html")

async def render_messages():
    messages = [msg async for msg in Message.objects.order_by("-created_at")[:5]]
    lines = "".join(
        f'<div class="chat chat-start">'
        f'<div class="chat-header opacity-50 text-xs">{m.created_at:%H:%M}</div>'
        f'<div class="chat-bubble">{m.text_msg}</div>'
        f'</div>'
        for m in reversed(messages)
    )
    print(f"Rendering messages:\n{lines}")
    return (
        f'<div id="chat-content">{lines}</div>'
    )

class MessagePayload(Serializer):
    text_msg: str

@bolt.get("/api/messages")
async def get_messages(request):
    async def generate():
        yield SSE.patch_elements(await render_messages())
        while True:
            new_message_event.clear()
            await new_message_event.wait()
            yield SSE.patch_elements(await render_messages())

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Content-Encoding": "identity",
        },
    )


@bolt.post("/api/new_message")
async def new_message(msg: MessagePayload):
    text_msg = msg.text_msg.strip()
    print(f"Received new message: {text_msg}")
    if text_msg:
        await Message.objects.acreate(text_msg=text_msg)
        new_message_event.set()
    return {"status": "ok"}


bolt.mount_django(r"/")

if __name__ == "__main__":
    import sys
    from django.core.management import (  # noqa: E402 needs to be after other things are configured (single-file django app style)
        execute_from_command_line,
    )

    execute_from_command_line(sys.argv)
