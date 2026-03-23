# Datastar Interaction Patterns

Reusable patterns for building hypermedia-driven applications with Datastar and Python (Django/Bolt).
Drawn from irgo (Go), htmx examples, and Datastar community resources.

Each pattern shows the **HTML** (frontend) and **Python** (backend) needed.
All backends use `datastar_py.ServerSentEventGenerator as SSE` and Django Bolt's `StreamingResponse`.

---

## Common Backend Boilerplate

Every SSE endpoint follows this shape:

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

---

## Pattern 1: Form Submit with Busy Indicator & Validation

The most common pattern. User fills a form, clicks submit, sees a spinner while
the backend processes, then gets validation feedback or a success update.

### HTML

```html
<form id="contact-form"
      data-signals="{firstName: '', lastName: '', email: '', _saving: false}"
      data-on:submit__prevent="@post('/api/contacts')">

    <!-- Busy overlay — shows while request is in flight -->
    <div data-show="$_saving" class="loading loading-spinner"></div>

    <label>
        First Name
        <input type="text" data-bind:firstName
               class="input input-bordered" />
        <span id="err-firstName" class="text-error text-sm"></span>
    </label>

    <label>
        Last Name
        <input type="text" data-bind:lastName
               class="input input-bordered" />
        <span id="err-lastName" class="text-error text-sm"></span>
    </label>

    <label>
        Email
        <input type="email" data-bind:email
               class="input input-bordered" />
        <span id="err-email" class="text-error text-sm"></span>
    </label>

    <button type="submit"
            data-indicator:_saving
            data-attr:disabled="$_saving"
            class="btn btn-primary">
        <span data-show="!$_saving">Save Contact</span>
        <span data-show="$_saving">Saving…</span>
    </button>
</form>
```

**Key attributes:**
- `data-indicator:_saving` — Datastar automatically sets `_saving=true` while the
  `@post` request is in flight, and `_saving=false` when it completes. The `_` prefix
  means the signal is local-only (never sent to the server).
- `data-attr:disabled="$_saving"` — disables the button while busy.
- `data-show="$_saving"` — toggles spinner/text visibility.
- `data-on:submit__prevent` — prevents default form submission, uses Datastar's `@post`.

### Python Backend

```python
@bolt.post("/api/contacts")
async def create_contact(request):
    async def generate():
        # Read signals sent by Datastar
        import json
        body = await request.body()
        signals = json.loads(body)

        first = signals.get("firstName", "").strip()
        last = signals.get("lastName", "").strip()
        email = signals.get("email", "").strip()

        # --- Validate ---
        errors = {}
        if not first:
            errors["firstName"] = "First name is required"
        if not last:
            errors["lastName"] = "Last name is required"
        if not email or "@" not in email:
            errors["email"] = "Valid email is required"

        if errors:
            # Patch each error span with its message
            for field, msg in errors.items():
                yield SSE.patch_elements(
                    f'<span id="err-{field}" class="text-error text-sm">{msg}</span>'
                )
            return

        # --- Clear errors ---
        for field in ("firstName", "lastName", "email"):
            yield SSE.patch_elements(
                f'<span id="err-{field}" class="text-error text-sm"></span>'
            )

        # --- Save to database ---
        contact = await Contact.objects.acreate(
            first_name=first, last_name=last, email=email
        )

        # --- Send success feedback ---
        yield SSE.patch_elements(
            f'<div id="contact-form" class="alert alert-success">'
            f'  Contact {first} {last} saved!'
            f'</div>'
        )

    return sse_response(generate)
```

### How it flows

```
1. User fills form, clicks "Save Contact"
2. data-on:submit__prevent fires @post('/api/contacts')
3. data-indicator:_saving → _saving = true → spinner shows, button disabled
4. Datastar sends POST with JSON body: {firstName: "Jo", lastName: "", email: "bad"}
5. Backend validates, yields SSE patch_elements for each error span
6. Request completes → _saving = false → spinner hides, button re-enabled
7. User fixes errors, resubmits
8. Backend validates OK, saves, yields success message replacing the form
```

---

## Pattern 2: Click to Edit

Display a record as read-only. Click "Edit" to swap it with a form. Save sends
an update via SSE and morphs back to the display view.

### HTML — Display View

```html
<div id="contact-42" class="card bg-base-100 p-4">
    <p><strong>Name:</strong> Jane Doe</p>
    <p><strong>Email:</strong> jane@example.com</p>
    <button data-on:click="@get('/api/contacts/42/edit')"
            class="btn btn-sm">
        Edit
    </button>
</div>
```

### HTML — Edit View (returned by server)

```html
<div id="contact-42"
     data-signals="{firstName: 'Jane', lastName: 'Doe', email: 'jane@example.com'}"
     class="card bg-base-100 p-4">
    <label>First Name
        <input type="text" data-bind:firstName class="input input-bordered" />
    </label>
    <label>Last Name
        <input type="text" data-bind:lastName class="input input-bordered" />
    </label>
    <label>Email
        <input type="email" data-bind:email class="input input-bordered" />
    </label>
    <div class="flex gap-2 mt-2">
        <button data-on:click="@put('/api/contacts/42')"
                data-indicator:_saving
                data-attr:disabled="$_saving"
                class="btn btn-primary">
            Save
        </button>
        <button data-on:click="@get('/api/contacts/42')"
                class="btn btn-ghost">
            Cancel
        </button>
    </div>
</div>
```

### Python Backend

```python
@bolt.get("/api/contacts/{id}")
async def get_contact(request, id: int):
    """Return the display view (also used by Cancel)."""
    contact = await Contact.objects.aget(pk=id)
    async def generate():
        yield SSE.patch_elements(render_contact_display(contact))
    return sse_response(generate)


@bolt.get("/api/contacts/{id}/edit")
async def edit_contact(request, id: int):
    """Return the edit form."""
    contact = await Contact.objects.aget(pk=id)
    async def generate():
        yield SSE.patch_elements(render_contact_edit(contact))
    return sse_response(generate)


@bolt.put("/api/contacts/{id}")
async def update_contact(request, id: int):
    """Validate and save, then return display view."""
    import json
    signals = json.loads(await request.body())

    async def generate():
        # validate...
        contact = await Contact.objects.aget(pk=id)
        contact.first_name = signals["firstName"]
        contact.last_name = signals["lastName"]
        contact.email = signals["email"]
        await contact.asave()

        yield SSE.patch_elements(render_contact_display(contact))

    return sse_response(generate)


def render_contact_display(c):
    return f'''
    <div id="contact-{c.pk}" class="card bg-base-100 p-4">
        <p><strong>Name:</strong> {c.first_name} {c.last_name}</p>
        <p><strong>Email:</strong> {c.email}</p>
        <button data-on:click="@get('/api/contacts/{c.pk}/edit')"
                class="btn btn-sm">Edit</button>
    </div>
    '''

def render_contact_edit(c):
    return f'''
    <div id="contact-{c.pk}"
         data-signals="{{firstName: '{c.first_name}', lastName: '{c.last_name}', email: '{c.email}'}}"
         class="card bg-base-100 p-4">
        <label>First Name
            <input type="text" data-bind:firstName class="input input-bordered" />
        </label>
        <label>Last Name
            <input type="text" data-bind:lastName class="input input-bordered" />
        </label>
        <label>Email
            <input type="email" data-bind:email class="input input-bordered" />
        </label>
        <div class="flex gap-2 mt-2">
            <button data-on:click="@put('/api/contacts/{c.pk}')"
                    data-indicator:_saving
                    data-attr:disabled="$_saving"
                    class="btn btn-primary">Save</button>
            <button data-on:click="@get('/api/contacts/{c.pk}')"
                    class="btn btn-ghost">Cancel</button>
        </div>
    </div>
    '''
```

### The trick

Both views share the **same `id`** (`contact-42`). When the server sends
`SSE.patch_elements(html)`, Datastar morphs the element in place — swapping
display for edit or vice versa. No client-side state machine needed.

---

## Pattern 3: Active Search (Typeahead)

User types in a search box, results update live with debouncing.

### HTML

```html
<div data-signals="{search: ''}">
    <input type="text"
           data-bind:search
           data-on:input__debounce.300ms="@get('/api/search')"
           data-indicator:_searching
           placeholder="Search contacts..."
           class="input input-bordered w-full" />

    <span data-show="$_searching" class="loading loading-dots"></span>

    <div id="search-results" class="mt-2"></div>
</div>
```

### Python Backend

```python
@bolt.get("/api/search")
async def search_contacts(request):
    # Datastar sends signals as query params for GET requests
    query = request.GET.get("search", "").strip()

    async def generate():
        if not query:
            yield SSE.patch_elements('<div id="search-results"></div>')
            return

        results = Contact.objects.filter(
            first_name__icontains=query
        ) | Contact.objects.filter(
            email__icontains=query
        )

        rows = ""
        async for c in results[:20]:
            rows += f'<div class="p-2 border-b">{c.first_name} {c.last_name} — {c.email}</div>'

        if not rows:
            rows = '<div class="p-2 text-gray-500">No results found</div>'

        yield SSE.patch_elements(f'<div id="search-results" class="mt-2">{rows}</div>')

    return sse_response(generate)
```

### Key details

- `data-on:input__debounce.300ms` — waits 300ms after the user stops typing
- For GET requests, Datastar sends all signals as query parameters
- `data-indicator:_searching` — automatic busy signal while request in flight

---

## Pattern 4: Delete with Confirmation

### HTML

```html
<tr id="row-42">
    <td>Jane Doe</td>
    <td>jane@example.com</td>
    <td>
        <button data-on:click="confirm('Delete Jane Doe?') && @delete('/api/contacts/42')"
                data-indicator:_deleting
                data-attr:disabled="$_deleting"
                class="btn btn-error btn-sm">
            Delete
        </button>
    </td>
</tr>
```

### Python Backend

```python
@bolt.delete("/api/contacts/{id}")
async def delete_contact(request, id: int):
    await Contact.objects.filter(pk=id).adelete()

    async def generate():
        yield SSE.remove_elements(f"#row-{id}")
    return sse_response(generate)
```

### Notes

- `confirm()` is plain JavaScript — returns `true`/`false`
- `&&` short-circuits: `@delete` only fires if user clicks OK
- `SSE.remove_elements(selector)` tells Datastar to remove the element from the DOM
- For a fancier modal, use a `<dialog>` element with `data-show`

---

## Pattern 5: Inline Validation (Live Field Feedback)

Validate a single field as the user types, without submitting the whole form.

### HTML

```html
<form data-signals="{email: '', _emailError: ''}">
    <label>
        Email
        <input type="email"
               data-bind:email
               data-on:input__debounce.500ms="@post('/api/validate/email')"
               class="input input-bordered" />
        <span data-show="$_emailError"
              data-text="$_emailError"
              class="text-error text-sm"></span>
    </label>
</form>
```

### Python Backend

```python
@bolt.post("/api/validate/email")
async def validate_email(request):
    import json, re
    signals = json.loads(await request.body())
    email = signals.get("email", "").strip()

    async def generate():
        if not email:
            yield SSE.patch_signals({"_emailError": ""})
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            yield SSE.patch_signals({"_emailError": "Invalid email format"})
        elif await Contact.objects.filter(email=email).aexists():
            yield SSE.patch_signals({"_emailError": "Email already taken"})
        else:
            yield SSE.patch_signals({"_emailError": ""})

    return sse_response(generate)
```

### Notes

- Uses `patch_signals` instead of `patch_elements` — updates a client-side signal
  that the `data-show` and `data-text` attributes react to
- `_emailError` uses `_` prefix = local-only, not sent to server on other requests
- Combine with Pattern 1 for full form validation on submit

---

## Pattern 6: Cascading Selects

Second dropdown depends on first dropdown's value.

### HTML

```html
<div data-signals="{make: '', model: ''}">
    <select data-bind:make
            data-on:change="@get('/api/models')"
            class="select select-bordered">
        <option value="">Select Make</option>
        <option value="toyota">Toyota</option>
        <option value="honda">Honda</option>
    </select>

    <select id="model-select" data-bind:model class="select select-bordered">
        <option value="">Select Model</option>
    </select>
</div>
```

### Python Backend

```python
MODELS = {
    "toyota": ["Camry", "Corolla", "RAV4", "Prius"],
    "honda": ["Civic", "Accord", "CR-V", "Fit"],
}

@bolt.get("/api/models")
async def get_models(request):
    make = request.GET.get("make", "")

    async def generate():
        options = '<option value="">Select Model</option>'
        for m in MODELS.get(make, []):
            options += f'<option value="{m.lower()}">{m}</option>'

        yield SSE.patch_elements(
            f'<select id="model-select" data-bind:model class="select select-bordered">{options}</select>'
        )
        # Reset the model signal since the options changed
        yield SSE.patch_signals({"model": ""})

    return sse_response(generate)
```

### Notes

- `data-on:change` fires when selection changes, sends all signals as query params
- Server returns the entire `<select>` element — Datastar morphs it by matching `id`
- `patch_signals({"model": ""})` resets the dependent value

---

## Pattern 7: Infinite Scroll / Lazy Load

Load more items when the user scrolls to the bottom.

### HTML

```html
<div id="feed" class="space-y-4">
    <!-- Initial items rendered by server -->
    <div class="card p-4">Item 1</div>
    <div class="card p-4">Item 2</div>

    <!-- Sentinel — triggers load when scrolled into view -->
    <div id="load-more"
         data-on:intersect="@get('/api/items?page=2')">
        <span class="loading loading-dots"></span> Loading more…
    </div>
</div>
```

### Python Backend

```python
PAGE_SIZE = 20

@bolt.get("/api/items")
async def get_items(request):
    page = int(request.GET.get("page", 1))
    offset = (page - 1) * PAGE_SIZE

    async def generate():
        items = Item.objects.order_by("-created_at")[offset:offset + PAGE_SIZE + 1]
        item_list = [item async for item in items]

        has_more = len(item_list) > PAGE_SIZE
        item_list = item_list[:PAGE_SIZE]

        # Render items and append after the existing ones
        html = ""
        for item in item_list:
            html += f'<div class="card p-4">{item.title}</div>'

        if has_more:
            next_page = page + 1
            html += f'''
            <div id="load-more"
                 data-on:intersect="@get('/api/items?page={next_page}')">
                <span class="loading loading-dots"></span> Loading more…
            </div>
            '''
        else:
            html += '<div id="load-more" class="text-center text-gray-500">No more items</div>'

        # Replace the sentinel with items + new sentinel
        yield SSE.patch_elements(
            f'<div id="load-more">{html}</div>',
        )

    return sse_response(generate)
```

### Notes

- `data-on:intersect` uses IntersectionObserver under the hood
- The sentinel replaces itself with new items + a new sentinel for the next page
- When there are no more items, the sentinel becomes a "No more items" message

---

## Pattern 8: Progress / Long-Running Task

Show a progress bar that updates as the server processes a long task.
This is where Datastar's SSE streaming really shines — the server keeps the
connection open and sends incremental updates.

### HTML

```html
<div data-signals="{_progress: 0, _status: 'idle'}">
    <button data-on:click="@post('/api/process')"
            data-indicator:_processing
            data-attr:disabled="$_processing || $_status === 'running'"
            class="btn btn-primary">
        Start Processing
    </button>

    <div data-show="$_status === 'running' || $_status === 'done'" class="mt-4">
        <progress class="progress progress-primary w-full"
                  data-attr:value="$_progress"
                  max="100"></progress>
        <span data-text="$_progress + '%'" class="text-sm"></span>
    </div>

    <div id="process-result" class="mt-2"></div>
</div>
```

### Python Backend

```python
@bolt.post("/api/process")
async def run_process(request):
    async def generate():
        yield SSE.patch_signals({"_status": "running", "_progress": 0})

        # Simulate a long-running task with progress updates
        for step in range(1, 11):
            await asyncio.sleep(0.5)  # do real work here
            progress = step * 10
            yield SSE.patch_signals({"_progress": progress})

        yield SSE.patch_signals({"_status": "done", "_progress": 100})
        yield SSE.patch_elements(
            '<div id="process-result" class="alert alert-success">Processing complete!</div>'
        )

    return sse_response(generate)
```

### Notes

- The SSE connection stays open while the task runs
- Server yields progress updates as `patch_signals` — the progress bar reacts
- No polling needed — this is a single streaming response
- This is the pattern that **replaces htmx's WebSocket approach** for live updates

---

## Pattern 9: Live Feed (SSE Stream — replaces WebSocket patterns)

Keep a connection open and push updates as they happen. This is the Datastar
equivalent of htmx's WebSocket extension, but simpler — it's just SSE.

### HTML

```html
<div data-init="@get('/api/feed')" id="live-feed" class="space-y-2">
    <div id="feed-content"></div>
</div>
```

### Python Backend

```python
# Shared event for notifying new data
feed_event = asyncio.Event()
latest_items = []

@bolt.get("/api/feed")
async def live_feed(request):
    async def generate():
        # Send current state first
        yield SSE.patch_elements(render_feed(latest_items))

        # Then keep connection open and push updates
        while True:
            feed_event.clear()
            await feed_event.wait()
            yield SSE.patch_elements(render_feed(latest_items))

    return sse_response(generate)


def render_feed(items):
    rows = "".join(
        f'<div class="p-2 border-b">{item["text"]} '
        f'<span class="text-xs opacity-50">{item["time"]}</span></div>'
        for item in items[-50:]  # last 50
    )
    return f'<div id="feed-content">{rows}</div>'
```

### When to use this vs. one-shot SSE

| Approach | Use when |
|----------|----------|
| One-shot SSE (`@post`) | User triggers action, server responds with updates, connection closes |
| Streaming SSE (`data-init="@get"`) | Server pushes updates indefinitely (chat, notifications, dashboards) |
| Streaming SSE from action | Long task with progress (Pattern 8) |

### htmx WebSocket patterns → Datastar SSE translation

| htmx WebSocket pattern | Datastar SSE equivalent |
|------------------------|------------------------|
| `hx-ws="connect:/ws/chat"` | `data-init="@get('/api/chat')"` |
| Send message via WS | `@post('/api/chat/send')` (separate endpoint) |
| Server pushes HTML via WS | Server yields `SSE.patch_elements(html)` in the open stream |
| Bi-directional updates | GET stream for receiving + POST for sending (two endpoints) |
| Connection lifecycle | SSE auto-reconnects; `data-init` re-fires on reconnect |

---

## Pattern 10: Editable Table Row

Edit a single row inline in a table. Only one row editable at a time.

### HTML — Display Row

```html
<tr id="row-7">
    <td>Jane Doe</td>
    <td>jane@example.com</td>
    <td>Active</td>
    <td>
        <button data-on:click="@get('/api/contacts/7/edit')"
                class="btn btn-xs">Edit</button>
    </td>
</tr>
```

### HTML — Edit Row (returned by server)

```html
<tr id="row-7" data-signals="{editName: 'Jane Doe', editEmail: 'jane@example.com'}">
    <td><input type="text" data-bind:editName class="input input-xs input-bordered" /></td>
    <td><input type="email" data-bind:editEmail class="input input-xs input-bordered" /></td>
    <td>Active</td>
    <td>
        <button data-on:click="@put('/api/contacts/7')"
                data-indicator:_saving
                data-attr:disabled="$_saving"
                class="btn btn-xs btn-primary">Save</button>
        <button data-on:click="@get('/api/contacts/7')"
                class="btn btn-xs btn-ghost">Cancel</button>
    </td>
</tr>
```

### Python Backend

```python
@bolt.get("/api/contacts/{id}/edit")
async def edit_row(request, id: int):
    contact = await Contact.objects.aget(pk=id)
    async def generate():
        yield SSE.patch_elements(f'''
        <tr id="row-{id}" data-signals="{{editName: '{contact.name}', editEmail: '{contact.email}'}}">
            <td><input type="text" data-bind:editName class="input input-xs input-bordered" /></td>
            <td><input type="email" data-bind:editEmail class="input input-xs input-bordered" /></td>
            <td>{contact.status}</td>
            <td>
                <button data-on:click="@put('/api/contacts/{id}')"
                        data-indicator:_saving data-attr:disabled="$_saving"
                        class="btn btn-xs btn-primary">Save</button>
                <button data-on:click="@get('/api/contacts/{id}')"
                        class="btn btn-xs btn-ghost">Cancel</button>
            </td>
        </tr>
        ''')
    return sse_response(generate)

@bolt.get("/api/contacts/{id}")
async def get_row(request, id: int):
    contact = await Contact.objects.aget(pk=id)
    async def generate():
        yield SSE.patch_elements(f'''
        <tr id="row-{id}">
            <td>{contact.name}</td>
            <td>{contact.email}</td>
            <td>{contact.status}</td>
            <td>
                <button data-on:click="@get('/api/contacts/{id}/edit')"
                        class="btn btn-xs">Edit</button>
            </td>
        </tr>
        ''')
    return sse_response(generate)

@bolt.put("/api/contacts/{id}")
async def save_row(request, id: int):
    import json
    signals = json.loads(await request.body())
    async def generate():
        contact = await Contact.objects.aget(pk=id)
        contact.name = signals["editName"]
        contact.email = signals["editEmail"]
        await contact.asave()

        yield SSE.patch_elements(f'''
        <tr id="row-{id}">
            <td>{contact.name}</td>
            <td>{contact.email}</td>
            <td>{contact.status}</td>
            <td>
                <button data-on:click="@get('/api/contacts/{id}/edit')"
                        class="btn btn-xs">Edit</button>
            </td>
        </tr>
        ''')
    return sse_response(generate)
```

---

## Pattern 11: Bulk Actions (Select All / Act on Selection)

### HTML

```html
<div data-signals="{_selectedIds: [], _selectAll: false}">

    <!-- Select-all checkbox -->
    <input type="checkbox"
           data-bind:_selectAll
           data-on:change="@get('/api/contacts/toggle-all')"
           class="checkbox" />

    <!-- Action buttons -->
    <button data-on:click="@post('/api/contacts/bulk-delete')"
            data-show="$_selectedIds.length > 0"
            class="btn btn-error btn-sm">
        Delete Selected
    </button>

    <table>
        <tbody id="contact-rows">
            <tr id="row-1">
                <td><input type="checkbox" value="1"
                           data-on:change="..." /></td>
                <td>Jane Doe</td>
            </tr>
            <!-- ... more rows ... -->
        </tbody>
    </table>
</div>
```

### Notes

- `_selectedIds` is local-only (prefixed with `_`) — tracks which rows are checked
- Bulk operations send the selected IDs to the server
- Server responds with `SSE.remove_elements` for each deleted row, or
  `SSE.patch_elements` for each updated row

---

## Quick Reference: Datastar Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-signals="{...}"` | Initialize reactive state | `data-signals="{name: '', count: 0}"` |
| `data-bind:name` | Two-way binding | `<input data-bind:email />` |
| `data-on:event` | Event handler | `data-on:click="@post('/api')"` |
| `data-on:event__modifier` | With modifier | `data-on:input__debounce.300ms` |
| `data-indicator:signal` | Auto busy signal | `data-indicator:_loading` |
| `data-show="expr"` | Conditional visibility | `data-show="$_loading"` |
| `data-text="expr"` | Dynamic text | `data-text="$count + ' items'"` |
| `data-attr:name="expr"` | Dynamic attribute | `data-attr:disabled="$_busy"` |
| `data-class:name="expr"` | Dynamic CSS class | `data-class:active="$isActive"` |
| `data-init="action"` | Run on mount | `data-init="@get('/api/init')"` |
| `data-on:intersect` | Intersection observer | `data-on:intersect="@get('/api/more')"` |

## Quick Reference: SSE Methods (datastar-py)

| Method | Purpose |
|--------|---------|
| `SSE.patch_elements(html)` | Morph HTML into DOM (match by id) |
| `SSE.remove_elements(selector)` | Remove element from DOM |
| `SSE.patch_signals(dict)` | Update client-side signals |
| `SSE.execute_script(js)` | Run JavaScript on client |
| `SSE.redirect(url)` | Navigate browser |

## Quick Reference: Event Modifiers

| Modifier | Purpose | Example |
|----------|---------|---------|
| `__debounce.Nms` | Wait N ms after last event | `data-on:input__debounce.300ms` |
| `__throttle.Nms` | At most once per N ms | `data-on:mousemove__throttle.100ms` |
| `__prevent` | preventDefault() | `data-on:submit__prevent` |
| `__stop` | stopPropagation() | `data-on:click__stop` |
| `__window` | Listen on window | `data-on:resize__window` |

## Quick Reference: Local vs Shared Signals

| Signal | Behavior |
|--------|----------|
| `name` | Sent to server with every request |
| `_name` | Local-only — never sent to server |

Use `_` prefix for UI-only state: `_loading`, `_editing`, `_expanded`, `_errors`, etc.
