# Datastar Hypermedia Patterns in irgo

Reference guide based on analysis of [github.com/stukennedy/irgo](https://github.com/stukennedy/irgo).

irgo is a cross-platform app framework (iOS, Android, desktop, web) using **Go** for backend logic and **Datastar** for frontend interactivity. It demonstrates a server-centric hypermedia architecture where the server sends HTML fragments over SSE instead of JSON.

---

## Key Concepts

- **No JSON API** — HTML is the wire format
- **No client-side routing** — server controls the page
- **Minimal JavaScript** — Datastar (~11KB) handles reactivity via HTML attributes
- **Server-Sent Events (SSE)** — server streams DOM updates to the browser

---

## Pattern 1: Signals (Client-Side State)

Signals are reactive variables declared in HTML:

```html
<div data-signals="{title: '', count: 0}">
    <input type="text" data-bind:title />
    <span data-text="$count"></span>
</div>
```

| Attribute | Purpose |
|-----------|---------|
| `data-signals="{...}"` | Declare reactive state |
| `data-bind:name` | Two-way bind to signal `name` |
| `data-text="$name"` | Display signal value as text |
| `data-show="$visible"` | Conditionally show/hide element |
| `data-class:active="$isActive"` | Toggle CSS class |

Signals are automatically sent to the server with every Datastar request.

---

## Pattern 2: Event Handlers (Actions)

```html
<!-- Server actions -->
<button data-on:click="@post('/todos')">Add</button>
<button data-on:click="@delete('/todos/42')">Delete</button>
<button data-on:click="@get('/refresh')">Refresh</button>

<!-- With conditions -->
<button data-on:click="$title.trim() && @post('/todos')">Add</button>

<!-- Keyboard events -->
<input data-on:keydown="event.key === 'Enter' && @post('/todos')" />

<!-- Event modifiers -->
<input data-on:input__debounce.300ms="@get('/search')" />
<div data-on:mousemove__throttle.100ms="@get('/api/pulse')">
```

Action shorthand:
- `@get('/path')` — GET request
- `@post('/path')` — POST request (sends signals as JSON body)
- `@put('/path')` — PUT request
- `@patch('/path')` — PATCH request
- `@delete('/path')` — DELETE request

---

## Pattern 3: Initialization

```html
<div data-init="@get('/api/init')">
    <!-- Content populated by server on load -->
</div>
```

`data-init` fires once when the element enters the DOM.

---

## Pattern 4: Two Handler Types (Go Server)

### Fragment Handlers — Full page responses (initial load)

```go
r.GET("/", func(ctx *router.Context) (string, error) {
    todos := store.All()
    return renderer.Render(templates.HomePage(todos))
})
```

Returns `(string, error)` — the full HTML page.

### SSE Handlers — Streaming DOM updates (Datastar interactions)

```go
r.DSPost("/todos", func(ctx *router.Context) error {
    var signals struct {
        Title string `json:"title"`
    }
    ctx.ReadSignals(&signals)

    todo := store.Add(signals.Title)
    sse := ctx.SSE()

    sse.PatchTempl(templates.TodoItem(todo))       // Add item to DOM
    sse.PatchSignals(map[string]any{"title": ""})  // Clear input
    sse.Remove("#empty-state")                     // Remove placeholder

    return nil
})
```

Returns `error` — streams SSE events to the client.

The `DS` prefix (`DSPost`, `DSGet`, `DSDelete`) registers SSE handlers. Detection is via the `Accept: text/event-stream` header that Datastar sends.

---

## Pattern 5: SSE Operations

The SSE writer is the server's "remote control" for the browser:

```go
sse := ctx.SSE()

// DOM Morphing
sse.PatchTempl(component)              // Morph templ component into DOM
sse.PatchHTML("<div id='x'>...</div>") // Morph raw HTML
sse.PatchTemplByID("myid", component)  // Target specific element

// Append / Prepend
sse.AppendTempl(component)
sse.PrependTempl(component)

// Remove
sse.Remove("#selector")
sse.RemoveByID("myid")

// Update client signals
sse.PatchSignals(map[string]any{"count": 5, "title": ""})

// Navigation
sse.Redirect("/new-page")

// Execute JavaScript
sse.ExecuteScript("console.log('hello')")
```

Multiple operations can be sent in a single response — they're independent SSE events.

---

## Pattern 6: ID-Based DOM Targeting

Elements need stable IDs so the server can target them:

```go
templ TodoItem(todo *Todo) {
    <li id={ fmt.Sprintf("todo-%d", todo.ID) }>
        <input type="checkbox"
            checked?={ todo.Completed }
            data-on:click={ fmt.Sprintf("@post('/todos/%d/toggle')", todo.ID) }
        />
        <span class={
            "flex-1",
            templ.KV("line-through text-gray-400", todo.Completed),
        }>
            { todo.Title }
        </span>
        <button data-on:click={ fmt.Sprintf("@delete('/todos/%d')", todo.ID) }>
            Delete
        </button>
    </li>
}
```

When the server sends `sse.PatchTempl(templates.TodoItem(todo))`, Datastar finds `<li id="todo-42">` and morphs just that element.

---

## Pattern 7: Reading Signals on the Server

```go
r.DSPost("/todos", func(ctx *router.Context) error {
    // Define expected signal structure
    var signals struct {
        Title    string `json:"title"`
        Priority int    `json:"priority"`
    }

    // Parse signals from request body
    if err := ctx.ReadSignals(&signals); err != nil {
        return ctx.SSE().PatchTempl(templates.ErrorMessage("Invalid input"))
    }

    // Use signals.Title, signals.Priority...
})
```

Signals sent by Datastar are JSON in the request body. `ReadSignals` deserializes them into a Go struct.

---

## Pattern 8: Templ Templates

irgo uses [templ](https://github.com/a-h/templ) for type-safe HTML:

```go
templ HomePage(todos []*Todo) {
    @Page("Todo App") {
        <div data-signals="{title: ''}" class="mb-6">
            <input type="text" data-bind:title placeholder="What needs to be done?" />
            <button data-on:click="$title.trim() && @post('/todos')">
                Add Todo
            </button>
        </div>
        <ul id="todo-list">
            for _, todo := range todos {
                @TodoItem(todo)
            }
        </ul>
    }
}
```

Templ components are Go functions — compile-time checked, composable, and Datastar attributes work naturally.

---

## The Request/Response Flow

```
1. User clicks: <button data-on:click="@post('/todos')">

2. Datastar:
   - Collects signals from data-signals scope
   - Sends POST /todos
     Accept: text/event-stream
     Content-Type: application/json
     Body: {"title": "Buy milk"}

3. Go handler:
   - ctx.ReadSignals(&signals)  → signals.Title = "Buy milk"
   - store.Add(signals.Title)   → creates todo
   - sse.PatchTempl(...)        → renders HTML fragment

4. SSE Response:
   event: datastar-patch-elements
   data: fragments <li id="todo-3">Buy milk</li>

   event: datastar-patch-signals
   data: signals {"title": ""}

5. Datastar:
   - Morphs <li id="todo-3"> into DOM
   - Updates signal title → "" (clears input)
   - No page reload
```

---

## Cross-Platform Architecture

The same Go handlers work everywhere because the pattern is transport-agnostic:

| Platform | Transport | How it works |
|----------|-----------|-------------|
| Web/Dev | Real HTTP | Standard HTTP server |
| Desktop | Localhost HTTP | Native webview → localhost server |
| Mobile | Virtual HTTP | Go processes requests in-memory via `httptest` |

On mobile, there's no network — Swift/Kotlin calls Go directly, Go uses `httptest.ResponseRecorder` to process the request, and returns HTML/SSE to the native WebView.

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `github.com/a-h/templ` | Type-safe HTML templates |
| `github.com/go-chi/chi/v5` | HTTP router |
| `github.com/starfederation/datastar-go` | Datastar SSE SDK |
| `github.com/webview/webview_go` | Desktop native window |
| `golang.org/x/mobile` | Mobile (gomobile) |

---

## Key Source Files in irgo

| File | What it shows |
|------|--------------|
| `examples/todo/app.go` | Complete handler implementations |
| `examples/todo/templates/todos.templ` | Templates with Datastar attributes |
| `pkg/router/router.go` | Fragment vs SSE handler registration |
| `pkg/router/context.go` | Request context, signal reading, SSE access |
| `pkg/datastar/sse.go` | Full SSE writer API |
| `pkg/router/middleware.go` | Datastar request detection |
| `pkg/adapter/http.go` | Virtual HTTP for mobile |
| `mobile/bridge.go` | Mobile bridge interface |
| `desktop/app.go` | Desktop app with native webview |
