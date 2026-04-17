## Common Backend Boilerplate

When using django-bolt, every SSE endpoint follows this shape:

clm - is this true, this is just what I tried
```python
from datastar_py import ServerSentEventGenerator as SSE
from django_bolt.responses import StreamingResponse

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Content-Encoding": "identity",
}

def sse_response(generator):
    """Wrap an SSE generator in a StreamingResponse."""
    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
```
