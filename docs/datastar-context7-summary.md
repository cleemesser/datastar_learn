### Setup Context Helpers Overview

Source: https://data-star.dev/reference/rocket

A detailed explanation of each helper function available within the Datastar setup context.

```APIDOC
## Datastar Setup Context Helpers

### Description
The setup context provides a collection of helper functions and properties that allow components to manage their internal state, react to changes, interact with global state, and control their lifecycle.

### Method
N/A (These are context properties available within the `setup` function)

### Endpoint
N/A

### Parameters
#### Setup Context Helpers
- **`props`** (object) - The normalized prop values for the current instance. Keeps setup code on the same decoded inputs that render uses, without a second function argument.
- **`$$`** (object) - Creates mutable instance-local state and exposes it on `$$.name`. Gives each component instance its own Datastar-backed state bucket with a property-style API that mirrors template `$$name` access.
- **`effect(fn)`** (function) - Runs a reactive side effect and tracks cleanup. Ideal for timers, subscriptions, and imperative DOM/library sync.
- **`apply(root, merge?)`** (function) - Runs Datastar apply on a root. Useful when third-party code injects DOM that needs Datastar activation.
- **`cleanup(fn)`** (function) - Registers disconnect cleanup. Prevents leaked timers, observers, and library instances.
- **`$`** (object) - Reads and writes the global Datastar signal store. Useful when setup needs shared app state instead of component-local Rocket state.
- **`actions`** (object) - Calls Datastar global actions from setup code. Useful when component setup needs the same global helpers available to `@action(...)` expressions.
- **`action(name, fn)`** (function) - Registers a local action callable from rendered markup. Lets event handlers target the current component instance instead of global actions.
- **`observeProps(fn, ...propNames)`** (function) - Responds to prop changes after decoding. Separates prop-driven imperative work from full rerenders.
- **`overrideProp(name, getter?, setter?)`** (function) - Wraps a declared prop’s default host accessor for this instance. Useful when a public prop must read from or write through a live inner control.
- **`defineHostProp(name, descriptor)`** (function) - Defines a host-only property or method on this instance. Useful for native-like host APIs that are not Rocket props, such as `files` or imperative methods.
- **`render(overrides, ...args)`** (function) - Reruns the component render function from setup code. Lets async or imperative work trigger a render with explicit trailing args.
- **`host`** (object) - The current custom element instance. Gives access to attributes, classes, observers, focus, and shadow APIs.

### Request Example
```javascript
setup({
  props, // Access component props
  $$,     // Access and modify local state
  $,      // Access global state
  action, // Define local actions
  actions, // Call global actions
  cleanup, // Register cleanup functions
  effect,  // Run side effects
  apply,   // Apply Datastar to DOM roots
  host,    // Access the host element
  // ... other helpers
}) {
  // ... setup logic using these helpers
}
```

### Response
N/A

#### Success Response (200)
N/A

#### Response Example
N/A
```

--------------------------------

### Demo Copy Button Component Example

Source: https://data-star.dev/reference/rocket

An example of a 'demo-copy-button' component using the Datastar setup context to manage state, actions, and rendering.

```APIDOC
## `demo-copy-button` Component Example

### Description
This example demonstrates the usage of the Datastar setup context within a custom web component, `demo-copy-button`. It showcases how to define props, manage local state with `$$`, define actions, and render the component's UI.

### Method
`rocket('component-name', { ...options })`

### Endpoint
N/A (Component definition)

### Parameters
#### Props
- **text** (string) - Optional - The text to be copied. Defaults to 'Copy me'.
- **resetMs** (number) - Optional - The duration in milliseconds before the label resets. Defaults to 1200ms, minimum 100ms.

#### Setup Context Helpers
- **`$$`**: Creates mutable instance-local state. Used here for `copied` and `label`.
- **`$`**: Accesses the global Datastar signal store. Used here to check `analyticsEnabled` and set `lastCopiedText`.
- **`action`**: Defines a local action callable from markup. Used here for the 'copy' action.
- **`actions`**: Accesses global Datastar actions. Used here for `actions.intl`.
- **`cleanup`**: Registers a function to run when the component is disconnected. Used here to clear the `setTimeout` timer.
- **`props`**: Provides access to the component's normalized props.

### Request Example
```javascript
1rocket('demo-copy-button', {
  props: ({ string, number }) => ({
    text: string.default('Copy me'),
    resetMs: number.min(100).default(1200),
  }),
  setup({ $$, $, action, actions, cleanup, props }) {
    $$.copied = false
    $$.label = () => ($$.copied ? 'Copied' : 'Copy')
    $$.resetMsLabel = actions.intl(
      'number',
      props.resetMs,
      { maximumFractionDigits: 0 },
      'en-US',
    )
    let timerId = 0

    action('copy', async () => {
      await navigator.clipboard.writeText(props.text)
      $$.copied = true
      if ($.analyticsEnabled !== false) {
        $.lastCopiedText = props.text
      }
      clearTimeout(timerId)
      timerId = window.setTimeout(() => {
        $$.copied = false
      }, props.resetMs)
    })

    cleanup(() => clearTimeout(timerId))
  },
  render({ html, props: { text } }) {
    return html`
      <button data-on:click="@copy()">
        <span data-text="$$label"></span>
        <small>${text} ($$resetMsLabel ms)</small>
      </button>
    `
  },
})
```

### Response
N/A (Component renders HTML)

#### Success Response (200)
N/A

#### Response Example
N/A
```

--------------------------------

### Setup Hook and Context Rendering

Source: https://data-star.dev/docs.md

The `setup` hook is used for asynchronous operations, initial data fetching, and managing component lifecycle. It provides access to `cleanup` and `render` for imperative updates.

```APIDOC
## `setup` Hook and Imperative Rendering

### Description
The `setup` hook is the place for initializing asynchronous operations, setting up event listeners, and managing component state that requires cleanup. It also provides a `render` function for imperative UI updates.

### Usage
Use `setup` for tasks like fetching data, subscribing to external events, or any logic that needs to be cleaned up when the component disconnects. The `render` function within the `setup` context can be used to force a re-render of the component, typically with new props or data, especially after asynchronous operations complete.

### Example
```javascript
rocket('demo-user-card', {
  props: ({ number, string }) => ({
    userId: number.min(1),
    fallbackName: string.default('Unknown user'),
  }),
  setup({ cleanup, render, props }) {
    let cancelled = false

    ;(async () => {
      try {
        const response = await fetch('/users/' + props.userId + '.json')
        const user = await response.json()
        if (!cancelled) {
          render({}, user, null) // Rerender with fetched user data
        }
      } catch (error) {
        if (!cancelled) {
          render({}, null, error) // Rerender with error information
        }
      }
    })()

    cleanup(() => {
      cancelled = true // Ensure async operations are cancelled on cleanup
    })
  },
  render({ html, props: { fallbackName } }, user = null, error = null) {
    if (error) {
      return html`<p>Failed to load user.</p>`
    }
    if (!user) {
      return html`<p>Loading user...</p>`
    }
    return html`
      <article>
        <h3>${user.name ?? fallbackName}</h3>
        <p>${user.email ?? 'No email provided'}</p>
      </article>
    `
  },
})
```

### Imperative Rendering with `ctx.render`
If setup code needs to force a render later, call `ctx.render` with an empty overrides object and any trailing args. This reruns the component render function with the current host, props, and template helpers, plus any extra arguments passed. This is not a replacement for local signals; use `ctx.render` for coarse structural patches after async or imperative work, not for high-frequency state updates.
```

--------------------------------

### Setup and Actions

Source: https://data-star.dev/reference/rocket

The `setup` function is used for initializing state in Rocket components when that state is not dependent on rendered refs. It provides access to context hooks for creating local Datastar-backed state and integrating browser behaviors.

```APIDOC
## Setup and Actions

### Description
`setup` is where Rocket components become stateful when that state does not depend on rendered refs. The context object gives you a focused set of hooks to create local Datastar-backed state and wire browser behavior.
```

--------------------------------

### Implement Component Logic in Setup

Source: https://data-star.dev/reference/rocket

Implement component logic within the `setup` function, including initializing state, setting up timers, and observing prop changes. Use `cleanup` to clear intervals when the component disconnects.

```javascript
rocket('demo-timer', {
  props: ({ number, bool }) => ({
    intervalMs: number.min(50).default(1000),
    autoplay: bool,
  }),
  setup({ $$, cleanup, props, observeProps }) {
    $$.seconds = 0
    let timerId = 0

    let syncTimer = () => {
      clearInterval(timerId)
      if (!props.autoplay) {
        return
      }
      timerId = window.setInterval(() => {
        $$.seconds += 1
      }, props.intervalMs)
    }

    syncTimer()
    observeProps(syncTimer)

    cleanup(() => clearInterval(timerId))
  },
  render({ html }) {
    return html`<p data-text="$$seconds"></p>`
  },
})
```

--------------------------------

### Start a Streaming Response with Rust

Source: https://data-star.dev/docs.md

Starts an SSE stream using Rust and the async_stream crate. This example demonstrates sending signals with a delay. Ensure datastar and async_stream are included in your dependencies.

```rust
use async_stream::stream;
use datastar::prelude::*;
use std::thread;
use std::time::Duration;

Sse(stream! {
    // Patches signals.
    yield PatchSignals::new("{hal: 'Affirmative, Dave. I read you.'}").into();

    thread::sleep(Duration::from_secs(1));

    yield PatchSignals::new("{hal: '...'}").into();
})
```

--------------------------------

### Setup API

Source: https://data-star.dev/reference/rocket

The `setup` function runs once per connected element instance after Rocket creates the component scope and before the initial Datastar apply pass. It's the default place for local signals, computed state, prop observers, timers, and cleanup handlers.

```APIDOC
## Setup API

### Description
Runs once per connected element instance to set up component logic, including signals, state, prop observers, timers, and cleanup handlers. It should not be used for DOM manipulation that requires rendered refs.

### Method
Not applicable (Configuration object property)

### Endpoint
Not applicable

### Parameters
#### Request Body
- **setup** (function) - Optional - A function that receives a `SetupContext` object.
  - **context** (`SetupContext`) - An object containing:
    - **$$** (object) - Access to component state and signals.
    - **cleanup** (function) - Function to register cleanup handlers.
    - **props** (object) - Normalized component props.
    - **observeProps** (function) - Function to observe prop changes.

### Request Example
```javascript
rocket('demo-timer', {
  props: ({ number }) => ({
    intervalMs: number.min(50).default(1000),
  }),
  setup({ $$, cleanup, props, observeProps }) {
    $$.seconds = 0;
    let timerId = 0;

    let syncTimer = () => {
      clearInterval(timerId);
      if (!props.autoplay) {
        return;
      }
      timerId = window.setInterval(() => {
        $$.seconds += 1;
      }, props.intervalMs);
    };

    syncTimer();
    observeProps(syncTimer);

    cleanup(() => clearInterval(timerId));
  },
  render({ html }) {
    return html`<p data-text="$$seconds"></p>`;
  },
});
```

### Response
#### Success Response (200)
Not applicable (This is a configuration object, not an API endpoint response)

#### Response Example
Not applicable
```

--------------------------------

### Setup Input Bridge with onFirstRender

Source: https://data-star.dev/reference/rocket

This example demonstrates setting up an input bridge using `onFirstRender` to synchronize an input element's value with component props. It uses `overrideProp` to manage bidirectional value flow and `refs` to access the DOM element.

```typescript
1rocket('demo-input-bridge', {
 2  props: ({ string }) => ({
 3    value: string.default(''),
 4  }),
 5  render: ({ html, props: { value } }) => html`
 6    <input data-ref:input value="${value}">
 7  `,
 8  onFirstRender({ overrideProp, refs }) {
 9    overrideProp(
10      'value',
11      (getDefault) => refs.input?.value ?? getDefault(),
12      (value, setDefault) => {
13        const next = String(value ?? '')
14        if (refs.input && refs.input.value !== next) refs.input.value = next
15        setDefault(next)
16      },
17    )
18  },
19})
```

--------------------------------

### Define Component Setup Context

Source: https://data-star.dev/reference/rocket

The `setup` function runs once per connected element instance. It's the default place for local signals, computed state, prop observers, timers, and cleanup handlers that do not depend on rendered refs.

```typescript
setup?: (context: SetupContext<InferProps<Defs>>) => void
```

--------------------------------

### Asynchronous Data Fetching and Rendering in setup

Source: https://data-star.dev/docs.md

This `setup` function fetches user data asynchronously. It uses `render` to update the component's view with fetched data or an error message, and `cleanup` to prevent state updates after unmounting.

```typescript
rocket('demo-user-card', {
  props: ({ string, number }) => ({
    userId: number.min(1),
    fallbackName: string.default('Unknown user'),
  }),
  setup({ cleanup, render, props }) {
    let cancelled = false

    ;(async () => {
      try {
        const response = await fetch('/users/' + props.userId + '.json')
        const user = await response.json()
        if (!cancelled) {
          render({}, user, null)
        }
      } catch (error) {
        if (!cancelled) {
          render({}, null, error)
        }
      }
    })()

    cleanup(() => {
      cancelled = true
    })
  },
  render({ html, props: { fallbackName } }, user = null, error = null) {
    if (error) {
      return html`<p>Failed to load user.</p>`
    }
    if (!user) {
      return html`<p>Loading user...</p>`
    }
    return html`
      <article>
        <h3>${user.name ?? fallbackName}</h3>
        <p>${user.email ?? 'No email provided'}</p>
      </article>
    `
  },
})
```

--------------------------------

### Create Custom Codecs

Source: https://data-star.dev/docs.md

Examples of creating custom codecs using the createCodec utility.

```javascript
import { createCodec } from '/bundles/datastar-pro.js'

let myCodec = createCodec({
  decode(value) {
    // normalize input
  },
  encode(value) {
    // reflect back to attribute text
  },
})
```

```javascript
import { createCodec, rocket } from '/bundles/datastar-pro.js'

let percent = createCodec({
    decode(value) {
      let text = String(value ?? '').trim().replace(/%$/, '')
      let number = Number.parseFloat(text)
      return Number.isFinite(number)
        ? Math.max(0, Math.min(100, number))
        : 0
    },
    encode(value) {
      return String(Math.max(0, Math.min(100, value)))
    },
})

rocket('demo-meter', {
  props: ({ string }) => ({
    value: percent.default(50),
    label: string.trim.default('Progress'),
  }),
})
```

--------------------------------

### Setup and Ref-backed Host Accessors with onFirstRender

Source: https://data-star.dev/docs.md

Use `onFirstRender` for logic that requires rendered DOM or `data-ref:*` refs. It provides access to the setup context and refs for DOM manipulation and prop overrides.

```typescript
onFirstRender?: (context: SetupContext<InferProps<Defs>> & { refs: Record<string, any> }) => void
```

--------------------------------

### Rocket Globe Pro Usage Example

Source: https://data-star.dev/examples/rocket_globe

This example shows how to use the globe-view component with data attributes for places and arcs.

```html
1<globe-view
2    data-attr:places='[
3        ["New York", [40.7128, -74.0060]],
4        ["London", [51.5074, -0.1278]]
5    ]'
6    data-attr:arcs='[
7        [[40.7128, -74.0060], [51.5074, -0.1278]]
8    ]'
9></globe-view>
```

--------------------------------

### System Dark Mode Match Example

Source: https://data-star.dev/examples/match_media

This example demonstrates how to use data-match-media to track the 'prefers-color-scheme: dark' media query. The $isDark signal is bound to the match state, and a 'dark' class is conditionally applied to the element. The current match state is displayed using a data-text binding.

```html
<div
    data-match-media:is-dark="prefers-color-scheme: dark"
    class="match-media-card"
    data-class:dark="$isDark"
>
    <p>System dark-mode match: <code data-text="$isDark"></code></p>
</div>
```

--------------------------------

### Usage Example for Starfield Component

Source: https://data-star.dev/examples/rocket_starfield

Demonstrates how to initialize the star-field component with reactive data attributes for configuration.

```html
1<div data-signals='{"centerX":50,"centerY":50,"speed":50,"starCount":500}'>
2    <star-field
3        data-attr:center-x="$centerX"
4        data-attr:center-y="$centerY"
5        data-attr:speed="$speed"
6        data-attr:star-count="$starCount"
7    ></star-field>
8</div>
```

--------------------------------

### Datastar Computed Property and Conditional Rendering

Source: https://data-star.dev/guide/reactive_signals

This example shows how to initialize multiple signals, define a computed signal using `data-computed`, and conditionally render content based on signal values using `data-show`. It also includes an example of updating a signal with user input.

```html
<div
    data-signals="{response: '', answer: 'bread'}"
    data-computed:correct="$response.toLowerCase() == $answer"
>
    <div id="question">What do you put in a toaster?</div>
    <button data-on:click="$response = prompt('Answer:') ?? ''">BUZZ</button>
    <div data-show="$response != ''">
        You answered “<span data-text="$response"></span>”.
        <span data-show="$correct">That is correct ✅</span>
        <span data-show="!$correct">
        The correct answer is “
        <span data-text="$answer"></span>
        ” 🤷
        </span>
    </div>
</div>
```

--------------------------------

### Implement component props and render

Source: https://data-star.dev/reference/rocket

Example showing how to define props with codecs and access them within the render function.

```javascript
rocket('demo-progress', {
  props: ({ number, bool, string }) => ({
    value: number.clamp(0, 100),
    striped: bool,
    label: string.trim.default('Progress'),
  }),
  render({ html, props: { value, striped, label } }) {
    return html`
      <div>
        <strong>${label}</strong>
        <div class="bar" data-style="{ width: ${value} + '%' }"></div>
        <span data-show="${striped}">Striped</span>
      </div>
    `
  },
})
```

--------------------------------

### Go: Create SSE Generator and Patch Content

Source: https://data-star.dev/docs.md

This Go example demonstrates creating a ServerSentEventGenerator and using it to patch elements and signals.

```go
import ("github.com/starfederation/datastar-go/datastar")

// Creates a new `ServerSentEventGenerator` instance.
sse := datastar.NewSSE(w,r)

// Patches elements into the DOM.
sse.PatchElements(
    `<div id="question">What do you put in a toaster?</div>`
)

// Patches signals.
sse.PatchSignals([]byte(`{response: '', answer: 'bread'}`))
```

--------------------------------

### Implement Signal Patching

Source: https://data-star.dev/examples/on_signal_patch

Example demonstrating signal patching with filtering to track specific signal updates.

```html
 1<div data-signals="{counter: 0, message: 'Hello World', allChanges: [], counterChanges: []}">
 2    <div class="actions">
 3        <button data-on:click="$message = `Updated: ${performance.now().toFixed(2)}`">
 4            Update Message
 5        </button>
 6        <button data-on:click="$counter++">
 7            Increment Counter
 8        </button>
 9        <button
10            class="error"
11            data-on:click="$allChanges.length = 0; $counterChanges.length = 0"
12        >
13            Clear All Changes
14        </button>
15    </div>
16    <div>
17        <h3>Current Values</h3>
18        <p>Counter: <span data-text="$counter"></span></p>
19        <p>Message: <span data-text="$message"></span></p>
20    </div>
21    <div
22        data-on-signal-patch="$counterChanges.push(patch)"
23        data-on-signal-patch-filter="{include: /^counter$/}"
24    >
25        <h3>Counter Changes Only</h3>
26        <pre data-json-signals__terse="{include: /^counterChanges/}"></pre>
27    </div>
28    <div
29        data-on-signal-patch="$allChanges.push(patch)"
30        data-on-signal-patch-filter="{exclude: /allChanges|counterChanges/}"
31    >
32        <h3>All Signal Changes</h3>
33        <pre data-json-signals__terse="{include: /^allChanges/}"></pre>
34    </div>
35</div>
```

--------------------------------

### Start a Streaming Response (JavaScript)

Source: https://data-star.dev/docs.md

Initiates a Server-Sent Events stream in JavaScript. Use this to send real-time updates to the client. Requires a server-side setup to handle the request and response objects.

```javascript
// Creates a new `ServerSentEventGenerator` instance (this also sends required headers)
ServerSentEventGenerator.stream(req, res, (stream) => {
      // Patches elements into the DOM.
     stream.patchElements(`<div id="question">What do you put in a toaster?</div>`);

     // Patches signals.
     stream.patchSignals({'response':  '', 'answer': 'bread'});
});
```

--------------------------------

### Define a Demo Counter Rocket Component

Source: https://data-star.dev/reference/rocket

This example demonstrates how to define a custom web component using Rocket. It includes props for 'count' and 'label', and a setup function to manage the count state. The render function returns HTML for a counter with a reset button.

```javascript
1rocket('demo-counter', {
  mode: 'light',
  props: ({ number, string }) => ({
    count: number.step(1).min(0),
    label: string.trim.default('Counter'),
  }),
  setup({ $$, observeProps, props }) {
    $$.count = props.count
    observeProps(() => {
      $$.count = props.count
    }, 'count')
  },
  render({ html, props: { count, label } }) {
    return html`
      <div class="stack gap-2">
        <button
          type="button"
          data-on:click="$$count += 1"
          data-text="${label} + ': ' + $$count"
        ></button>
        <template data-if="$$count !== ${count}">
          <button type="button" data-on:click="$$count = ${count}">Reset</button>
        </template>
      </div>
    `
  },
})

```

--------------------------------

### Python: SSE with Litestar and DatastarResponse

Source: https://data-star.dev/docs.md

An asynchronous Python example using Litestar and DatastarResponse to stream SSE, patching elements and signals.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.litestar import DatastarResponse

async def endpoint():
    return DatastarResponse([
        SSE.patch_elements('<div id="question">What do you put in a toaster?</div>'),
        SSE.patch_signals({"response": "", "answer": "bread"})
    ])
```

--------------------------------

### Install Datastar via CDN

Source: https://data-star.dev/guide

Include the Datastar library in your project using a script tag from a CDN.

```html
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0/bundles/datastar.js"></script>
```

```html
<script type="module" src="/path/to/datastar.js"></script>
```

--------------------------------

### Define a Rocket component with setup logic

Source: https://data-star.dev/docs.md

Demonstrates the use of props, local state ($$), global signals ($), actions, and cleanup within a Rocket component definition.

```javascript
rocket('demo-copy-button', {
  props: ({ string, number }) => ({
    text: string.default('Copy me'),
    resetMs: number.min(100).default(1200),
  }),
  setup({ $$, $, action, actions, cleanup, props }) {
    $$.copied = false
    $$.label = () => ($$.copied ? 'Copied' : 'Copy')
    $$.resetMsLabel = actions.intl(
      'number',
      props.resetMs,
      { maximumFractionDigits: 0 },
      'en-US',
    )
    let timerId = 0

    action('copy', async () => {
      await navigator.clipboard.writeText(props.text)
      $$.copied = true
      if ($.analyticsEnabled !== false) {
        $.lastCopiedText = props.text
      }
      clearTimeout(timerId)
      timerId = window.setTimeout(() => {
        $$.copied = false
      }, props.resetMs)
    })

    cleanup(() => clearTimeout(timerId))
  },
  render({ html, props: { text } }) {
    return html`
      <button data-on:click="@copy()">
        <span data-text="$$label"></span>
        <small>${text} ($$resetMsLabel ms)</small>
      </button>
    `
  },
})
```

--------------------------------

### Copy Button Usage Example

Source: https://data-star.dev/examples/rocket_copy_button

Demonstrates how to bind a text input to a copy-button component using Datastar signals.

```html
1<div data-signals='{"myCode":"To infinity and beyond"}'>
2    <input data-bind:my-code type="text" />
3    <copy-button data-attr:code="$myCode"></copy-button>
4</div>
```

--------------------------------

### Usage Example of echarts-view

Source: https://data-star.dev/examples/rocket_echarts

Demonstrates how to implement the echarts-view component with a configuration object passed via the option attribute.

```html
 1<echarts-view data-attr:option="{
 2    title: { text: 'Sales Data' },
 3    tooltip: { trigger: 'axis' },
 4    legend: {
 5        formatter: function (name) {
 6            return 'Series: ' + name
 7        }
 8    },
 9    xAxis: {
10        type: 'category',
11        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
12    },
13    yAxis: { type: 'value' },
14    series: [{
15        name: 'Sales',
16        data: [120, 200, 150, 80, 70, 110, 130],
17        type: 'bar'
18    }]
19}"></echarts-view>
```

--------------------------------

### Kotlin: Patch Elements and Signals via SSE

Source: https://data-star.dev/docs.md

A Kotlin example demonstrating the use of ServerSentEventGenerator to patch elements and signals for SSE communication.

```kotlin
val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements = """<div id="question">What do you put in a toaster?</div>""",
)

generator.patchSignals(
    signals = """{"response": "", "answer": "bread"}""",
)
```

--------------------------------

### Redirect with Delay using SSE in Go

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This Go example shows how to send HTML to update the UI, pause execution, and then run a JavaScript snippet to redirect the user. It uses the datastar-go library.

```go
import (
    "time"
    "github.com/starfederation/datastar-go/datastar"
)

sse := datastar.NewSSE(w, r)
sse.PatchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`)
time.Sleep(3 * time.Second)
sse.ExecuteScript(`
    setTimeout(() => window.location = "/guide")
`)

```

--------------------------------

### GET /endpoint

Source: https://data-star.dev/reference/actions

Sends a GET request to the specified URI. Signals are sent as query parameters by default.

```APIDOC
## GET /endpoint

### Description
Sends a GET request to the backend using the Fetch API. The response must contain zero or more Datastar SSE events.

### Method
GET

### Endpoint
/endpoint

### Parameters
#### Query Parameters
- **datastar** (object) - Optional - Contains existing signals, excluding those starting with an underscore.

### Request Example
<button data-on:click="@get('/endpoint')"></button>
```

--------------------------------

### Kotlin Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Kotlin example demonstrating SSE patch elements with DataStar. It formats the current time and updates the `#time` div.

```kotlin
val now: LocalDateTime = currentTime()

val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements =
        """
        <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
            $now
        </div>
        ".trimIndent()
)

```

--------------------------------

### Rocket Open Shadow DOM Component Example

Source: https://data-star.dev/docs.md

An example of a Rocket component using 'open' shadow DOM mode. It includes encapsulated styles and renders a div with a title prop. The shadowRoot is accessible for debugging.

```javascript
rocket('demo-modal-frame', {
  mode: 'open',
  props: ({ string }) => ({
    title: string.default('Dialog'),
  }),
  render({ html, props: { title } }) {
    return html`
      <style>
        :host { display: block; }
        .frame { border: 1px solid #d4d4d8; padding: 1rem; }
      </style>
      <div class="frame">${title}</div>
    `
  },
})
```

--------------------------------

### Trigger GET Request with @get() Action

Source: https://data-star.dev/docs.md

Use the `@get()` action on an element to send a GET request to the specified URL when an event occurs (e.g., click). The response will be used to patch the DOM.

```html
<button data-on:click="@get('/endpoint')">
    Open the pod bay doors, HAL.
</button>
<div id="hal"></div>
```

--------------------------------

### Component Event Registration and Lifecycle

Source: https://data-star.dev/examples/rocket_flow

Setup of event listeners for flow nodes and edges, along with property observers and cleanup logic.

```javascript
    host.addEventListener('flow-node-register', onNodeRegister)
    host.addEventListener('flow-node-update', onNodeUpdate)
    host.addEventListener('flow-node-remove', onNodeRemove)
    host.addEventListener('flow-edge-register', onEdgeRegister)
    host.addEventListener('flow-edge-update', onEdgeUpdate)
    host.addEventListener('flow-edge-remove', onEdgeRemove)
    host.addEventListener('flow-node-drag-start', (evt) => {
      const detail = /** @type {CustomEvent<{ node?: { id?: string } }>} */ (
        evt
      ).detail
      setPendingState(detail?.node?.id ?? '')
    })
    host.addEventListener('flow-node-drag-end', (evt) => {
      const detail = /** @type {CustomEvent<{ node?: { id?: string } }>} */ (
        evt
      ).detail
      setPendingState(detail?.node?.id ?? '')
    })
    host.addEventListener('flow-node-drag-cancel', clearPendingState)
    host.addEventListener('keydown', handleKeydown)
    childObserver.observe(host, { childList: true })
    queueMicrotask(() => {
      Array.from(host.children).forEach(hideFlowChild)
    })
    init()

    observeProps(() => {
      viewport = normalizeViewport(props.viewport)
      schedule()
    }, 'viewport')
    observeProps(() => {
      grid = props.grid
      schedule()
    }, 'grid')
    observeProps(() => {
      const next = props.serverUpdateTime.getTime()
      if (next === lastServerUpdateTime) return
      lastServerUpdateTime = next
      clearPendingState()
      clearSelectedEdge()
    }, 'serverUpdateTime')

    cleanup(() => {
      childObserver.disconnect()
      host.removeEventListener('flow-node-register', onNodeRegister)
      host.removeEventListener('flow-node-update', onNodeUpdate)
      host.removeEventListener('flow-node-remove', onNodeRemove)
      host.removeEventListener('flow-edge-register', onEdgeRegister)
      host.removeEventListener('flow-edge-update', onEdgeUpdate)
      host.removeEventListener('flow-edge-remove', onEdgeRemove)
      host.removeEventListener('keydown', handleKeydown)
      if (svg) {
        svg.removeEventListener('pointerdown', pointerDown)
        svg.removeEventListener('wheel', handleWheel)
      }
      if (frame) cancelAnimationFrame(frame)
      if (graphFrame) cancelAnimationFrame(graphFrame)
      if (edgeFrameId) cancelAnimationFrame(edgeFrameId)
    })
```

--------------------------------

### Complex reactivity with signals, computed, and conditional display

Source: https://data-star.dev/docs.md

This example demonstrates creating multiple signals, a computed signal, and conditionally displaying content based on signal values and computed results.

```html
<div
    data-signals="{response: '', answer: 'bread'}"
    data-computed:correct="$response.toLowerCase() == $answer"
>
    <div id="question">What do you put in a toaster?</div>
    <button data-on:click="$response = prompt('Answer:') ?? ''">BUZZ</button>
    <div data-show="$response != ''">
        You answered “<span data-text="$response"></span>”.
        <span data-show="$correct">That is correct ✅</span>
        <span data-show="!$correct">
        The correct answer is “
        <span data-text="$answer"></span>
        ”
        </span>
    </div>
</div>
```

--------------------------------

### Triggering a Patch via GET Request

Source: https://data-star.dev/guide/getting_started

Use the @get() action to send a request to the backend, which returns HTML to be morphed into the DOM.

```html
1<button data-on:click="@get('/endpoint')">
2    Open the pod bay doors, HAL.
3</button>
4<div id="hal"></div>
```

--------------------------------

### Set Interval for Backend Request

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Use the `data-on-interval__duration` attribute to specify an interval for making a GET request to the backend. The interval is set to 5 seconds in this example.

```html
<div id="time"
     data-on-interval__duration.5s="@get('/endpoint')"
></div>
```

--------------------------------

### Rust Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Rust example using DataStar to send SSE patch elements. It formats the current time and patches the `#time` div.

```rust
use datastar::prelude::*;
use chrono::Local;
use async_stream::stream;

let current_time = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();

Sse(stream! {
    yield PatchElements::new(
        format!(
            "<div id='time' data-on-interval__duration.5s='@get(\"/endpoint\")'>{}</div>",
            current_time
        )
    ).into();
})

```

--------------------------------

### Redirect with Delay using SSE in Go (Redirect Method)

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This Go example demonstrates using the SSE.Redirect method for client-side redirection after a delay and UI update. It's an alternative to ExecuteScript for redirects.

```go
import (
    "time"
    "github.com/starfederation/datastar-go/datastar"
)

sse := datastar.NewSSE(w, r)
sse.PatchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`)
time.Sleep(3 * time.Second)
sse.Redirect("/guide")

```

--------------------------------

### Rocket Scope Rewriting Example

Source: https://data-star.dev/reference/rocket

Demonstrates how Rocket automatically transforms local component state references into instance-specific paths.

```javascript
1// You write this in render():
2html`
3  <button data-on:click="$$count += 1"></button>
4  <span data-text="$$count"></span>
5`
6
7// For <demo-counter id="inventory-panel">, Rocket rewrites it as:
8<button data-on:click="_rocket.demo_counter.inventory_panel.count += 1"></button>
9<span data-text="_rocket.demo_counter.inventory_panel.count"></span>
```

--------------------------------

### GET Request

Source: https://data-star.dev/docs.md

Sends a GET request to the backend. Signals are sent as query parameters by default. Supports options like `openWhenHidden` and `contentType`.

```APIDOC
## GET /endpoint

### Description
Sends a `GET` request to the backend using the Fetch API. The URI can be any valid endpoint and the response must contain zero or more Datastar SSE events.

### Method
GET

### Endpoint
`/endpoint`

### Parameters
#### Query Parameters
- **openWhenHidden** (boolean) - Optional - If true, the SSE connection remains open when the page is hidden.
- **contentType** (string) - Optional - Sets the `Content-Type` header. Can be 'form' for `application/x-www-form-urlencoded`.

### Request Example
```html
<button data-on:click="@get('/endpoint')"></button>
<button data-on:click="@get('/endpoint', {openWhenHidden: true})"></button>
<button data-on:click="@get('/endpoint', {contentType: 'form'})></button>
```

### Response
#### Success Response (200)
- **Datastar SSE events** (array) - Zero or more SSE events from the backend.
```

--------------------------------

### Start a Streaming Response with Ruby

Source: https://data-star.dev/docs.md

Initiates a Server-Sent Events (SSE) stream using Ruby. Use this to send real-time updates to the client. Requires the datastar gem.

```ruby
datastar.stream do |sse|
  # Patches signals
  sse.patch_signals(hal: 'Affirmative, Dave. I read you.')

  sleep 1

  sse.patch_signals(hal: '...')
end
```

--------------------------------

### Perform GET request with Datastar

Source: https://data-star.dev/reference/actions

Sends a GET request to the specified endpoint. Signals are sent as query parameters by default.

```html
<button data-on:click="@get('/endpoint')"></button>
```

--------------------------------

### Redirect with Delay using SSE in Kotlin

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

A Kotlin example demonstrating how to send HTML for UI updates, pause for a duration, and then execute a JavaScript redirect. Uses ServerSentEventGenerator.

```kotlin
val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements = """
        <div id="indicator">Redirecting in 3 seconds...</div>
        """.trimIndent(),
)

Thread.sleep(3 * ONE_SECOND)

generator.executeScript(
    script = "setTimeout(() => window.location = '/guide')",
)

```

--------------------------------

### Ruby Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Ruby example using DataStar to send SSE patch elements. It formats the current time and patches the `#time` div.

```ruby
datastar = Datastar.new(request:, response:)

current_time = Time.now.strftime('%Y-%m-%d %H:%M:%S')

datastar.patch_elements <<~FRAGMENT
    <div id="time"
         data-on-interval__duration.5s="@get('/endpoint')"
    >
        #{current_time}
    </div>
FRAGMENT

```

--------------------------------

### Node.js Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Node.js example using DataStar to send SSE patch elements. It formats the current time and patches the `#time` div.

```javascript
import { createServer } from "node:http";
import { ServerSentEventGenerator } from "../npm/esm/node/serverSentEventGenerator.js";

const server = createServer(async (req, res) => {
  const currentTime = new Date().toISOString();

  ServerSentEventGenerator.stream(req, res, (sse) => {
    sse.patchElements(`
       <div id="time"
          data-on-interval__duration.5s="@get('/endpoint')"
       >
         ${currentTime}
       </div>
    `);
  });
});

```

--------------------------------

### Send Form Encoded GET Request with @get()

Source: https://data-star.dev/docs.md

Use `contentType: 'form'` to send GET requests with `application/x-www-form-urlencoded` encoding.

```html
<button data-on:click="@get('/endpoint', {contentType: 'form'})></button>
```

--------------------------------

### C# Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

C# example using DataStar's `IDatastarService` to patch elements. It formats the current time and sends an updated `#time` div via SSE.

```csharp
using StarFederation.Datastar.DependencyInjection;

app.MapGet("/endpoint", async (IDatastarService datastarService) =>
{
    var currentTime = DateTime.Now.ToString("yyyy-MM-dd hh:mm:ss");
    await datastarService.PatchElementsAsync($"""
        <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
            {currentTime}
        </div>
    """);
});

```

--------------------------------

### Fetch User Data and Render with Context

Source: https://data-star.dev/reference/rocket

This component fetches user data asynchronously. It uses `setup` for the fetch operation and `render` to display the user information, loading state, or an error message. `ctx.render` is called to update the component after data is available or an error occurs.

```typescript
1rocket('demo-user-card', {
 2  props: ({ string, number }) => ({
 3    userId: number.min(1),
 4    fallbackName: string.default('Unknown user'),
 5  }),
 6  setup({ cleanup, render, props }) {
 7    let cancelled = false
 8
 9    ;(async () => {
10      try {
11        const response = await fetch('/users/' + props.userId + '.json')
12        const user = await response.json()
13        if (!cancelled) {
14          render({}, user, null)
15        }
16      } catch (error) {
17        if (!cancelled) {
18          render({}, null, error)
19        }
20      }
21    })()
22
23    cleanup(() => {
24      cancelled = true
25    })
26  },
27  render({ html, props: { fallbackName } }, user = null, error = null) {
28    if (error) {
29      return html`<p>Failed to load user.</p>`
30    }
31    if (!user) {
32      return html`<p>Loading user...</p>`
33    }
34    return html`
35      <article>
36        <h3>${user.name ?? fallbackName}</h3>
37        <p>${user.email ?? 'No email provided'}</p>
38      </article>
39    `
40  },
41})
```

--------------------------------

### Start a Streaming Response (Rust)

Source: https://data-star.dev/docs.md

Initiates a Server-Sent Events stream in Rust using `async-stream`. Use this to send real-time updates to the client. Requires `datastar` and `async-stream` crates.

```rust
use datastar::prelude::*;
use async_stream::stream;

Sse(stream! {
    // Patches elements into the DOM.
    yield PatchElements::new("<div id='question'>What do you put in a toaster?</div>").into();

    // Patches signals.
    yield PatchSignals::new("{response: '', answer: 'bread'}").into();
})
```

--------------------------------

### Python (FastAPI/Sanic) SSE Patch Signals

Source: https://data-star.dev/docs.md

An asynchronous example in Python using ServerSentEventGenerator to patch signals, with asyncio.sleep for delays.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

@app.get('/do-you-read-me')
@datastar_response
async def open_doors(request):
    yield SSE.patch_signals({"hal": "Affirmative, Dave. I read you."})
    await asyncio.sleep(1)
    yield SSE.patch_signals({"hal": "..."})
```

--------------------------------

### Light DOM Component Example

Source: https://data-star.dev/reference/rocket

A simple 'demo-chip' component using light DOM mode. It displays a label within a span, inheriting styles from the parent document.

```javascript
1rocket('demo-chip', {
2  mode: 'light',
3  props: ({ string }) => ({
4    label: string.default('Chip'),
5  }),
6  render({ html, props: { label } }) {
7    return html`<span class="chip">${label}</span>`
8  },
9})
```

--------------------------------

### Use a Rocket Component in HTML

Source: https://data-star.dev/reference/rocket

This example shows how to import and use a custom Rocket component ('demo-counter') within an HTML file. It assumes the 'rocket' function is imported from the Datastar Pro bundle.

```html
<script type="module">
  import { rocket } from '/bundles/datastar-pro.js'
  // define demo-counter here
</script>

<demo-counter count="5" label="Inventory"></demo-counter>

```

--------------------------------

### Datastar Runtime Error Example

Source: https://data-star.dev/docs.md

This is an example of a Datastar runtime error message logged to the browser console when a data attribute is used incorrectly. The 'More info' link provides context-specific error details.

```javascript
Uncaught datastar runtime error: textKeyNotAllowed
More info: https://data-star.dev/errors/key_not_allowed?metadata=%7B%22plugin%22%3A%7B%22name%22%3A%22text%22%2C%22type%22%3A%22attribute%22%7D%2C%22element%22%3A%7B%22id%22%3A%22%22%2C%22tag%22%3A%22DIV%22%7D%2C%22expression%22%3A%7B%22rawKey%22%3A%22textFoo%22%2C%22key%22%3A%22foo%22%2C%22value%22%3A%22%22%2C%22fnContent%22%3A%22%22%7D%7D
Context: {
    "plugin": {
        "name": "text",
        "type": "attribute"
    },
    "element": {
        "id": "",
        "tag": "DIV"
    },
    "expression": {
        "rawKey": "textFoo",
        "key": "foo",
        "value": "",
        "fnContent": ""
    }
}
```

--------------------------------

### Redirect with Delay using SSE in Ruby

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This Ruby example uses Datastar to stream SSE events. It patches elements, pauses, and then executes a JavaScript snippet to redirect the user. Uses a heredoc for the script.

```ruby
datastar = Datastar.new(request:, response:)

datastar.stream do |sse|
  sse.patch_elements '<div id="indicator">Redirecting in 3 seconds...</div>'

  sleep 3

  sse.execute_script <<~JS
    setTimeout(() => {
      window.location = '/guide'
    })
  JS
end

```

--------------------------------

### Configure GET request options

Source: https://data-star.dev/reference/actions

Adjusts request behavior such as keeping the connection open when the page is hidden or changing the content type.

```html
<button data-on:click="@get('/endpoint', {openWhenHidden: true})"></button>
```

```html
<button data-on:click="@get('/endpoint', {contentType: 'form'})"></button>
```

--------------------------------

### Python (Sanic) Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Python example using DataStar with the Sanic framework to send SSE patch elements. It formats the current time and updates the `#time` div.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import DatastarResponse

@app.get("/endpoint")
async def endpoint():
    current_time = datetime.now()

    return DatastarResponse(SSE.patch_elements(f"""
        <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
            {current_time:%Y-%m-%d %H:%M:%S}
        </div>
    """,))

```

--------------------------------

### Implement Password Strength Component Usage

Source: https://data-star.dev/examples/rocket_password_strength

Use the custom element tag to initialize the component with an optional starting password value.

```html
1<password-strength password="Str0ng!Pass"></password-strength>
```

--------------------------------

### Alphabet Stream Component Usage

Source: https://data-star.dev/examples/rocket_letter_stream

This is an example of how to use the alphabet-stream component with a specified seed string.

```html
1<alphabet-stream seed="ABCDEF"></alphabet-stream>
```

--------------------------------

### Custom Request Cancellation Strategies

Source: https://data-star.dev/docs.md

Examples of disabling automatic cancellation and using an AbortController for manual request control.

```html
<!-- Allow concurrent requests (no automatic cancellation) -->
<button data-on:click="@get('/endpoint', {requestCancellation: 'disabled'})">Allow Multiple</button>

<!-- Custom abort controller for fine-grained control -->
<div data-signals:controller="new AbortController()">
    <button data-on:click="@get('/endpoint', {requestCancellation: $controller})">Start Request</button>
    <button data-on:click="$controller.abort()">Cancel Request</button>
</div>
```

--------------------------------

### HTML for Load More Button

Source: https://data-star.dev/how_tos/load_more_list_items

Sets up an HTML button with unique IDs and data attributes to trigger a GET request and manage the offset for loading more data.

```html
1<div id="list">
2<div>Item 1</div>
3</div>
4<button id="load-more"
5        data-signals:offset="1"
6        data-on:click="@get('/how_tos/load_more/data')">
7Click to load another item
8</button>
```

--------------------------------

### Creating a Percentage Codec

Source: https://data-star.dev/reference/rocket

An example of a custom percentage codec that normalizes string inputs (e.g., '50%') to a number between 0 and 100, and encodes numbers back into strings with a '%' sign. It also demonstrates registering this codec with a custom element.

```javascript
import { createCodec, rocket } from '/bundles/datastar-pro.js'

let percent = createCodec({
    decode(value) {
      let text = String(value ?? '').trim().replace(/%$/, '')
      let number = Number.parseFloat(text)
      return Number.isFinite(number)
        ? Math.max(0, Math.min(100, number))
        : 0
    },
    encode(value) {
      return String(Math.max(0, Math.min(100, value)))
    },
})

rocket('demo-meter', {
  props: ({ string }) => ({
    value: percent.default(50),
    label: string.trim.default('Progress'),
  }),
})
```

--------------------------------

### Java SDK for SSE Patching

Source: https://data-star.dev/docs.md

This Java example demonstrates using the Datastar SDK to send SSE events for DOM patching. It includes sending an initial HTML element, pausing, and then sending a subsequent update.

```java
import starfederation.datastar.utils.ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);

// Patches elements into the DOM.
generator.send(PatchElements.builder()
    .data("<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
    .build()
);

Thread.sleep(1000);

generator.send(PatchElements.builder()
```

--------------------------------

### HTML Button for Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Use the `data-on:click` attribute to trigger a GET request to a backend endpoint that initiates the redirect.

```html
<button data-on:click="@get('/endpoint')">
    Click to be redirected from the backend
</button>
<div id="indicator"></div>
```

--------------------------------

### Redirect with Delay using SSE in Kotlin (Redirect Method)

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

A Kotlin example using ServerSentEventGenerator's redirect method to navigate the client to a new URL after a specified delay and UI update.

```kotlin
val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements = """
        <div id="indicator">Redirecting in 3 seconds...</div>
        """.trimIndent(),
)

Thread.sleep(3 * ONE_SECOND)

generator.redirect("/guide")

```

--------------------------------

### Button with Automatic Loading Indicator

Source: https://data-star.dev/guide/the_tao_of_datastar

This example shows how to automatically display a loading indicator on a button while a backend request is in progress. The `data-indicator` attribute manages the visibility of the loading message.

```html
<div>
    <button data-indicator:_loading
            data-on:click="@post('/do_something')"
    >
        Do something
        <span data-show="$_loading">Loading...</span>
    </button>
</div>
```

--------------------------------

### Clojure Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Example of a Clojure backend using DataStar to send SSE patch elements. It formats the current time and patches the `#time` div at a 5-second interval.

```clojure
(require
  '[starfederation.datastar.clojure.api :as d*]
  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
  '[some.hiccup.library :refer [html]])

(import
  'java.time.format.DateTimeFormatter
  'java.time.LocalDateTime)

(def formatter (DateTimeFormatter/ofPattern "YYYY-MM-DD HH:mm:ss"))

(defn handle [ring-request]
   (->sse-response ring-request
     {on-open
      (fn [sse]
        (d*/patch-elements! sse
          (html [:div#time {:data-on-interval__duration.5s (d*/sse-get "/endpoint")}
                  (LocalDateTime/.format (LocalDateTime/now) formatter)])))}))

        (d*/close-sse! sse)))

```

--------------------------------

### Redirect with Delay using SSE in Python (Sanic)

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

An asynchronous Python example using Sanic to handle redirects. It yields SSE events for UI updates, waits, and then executes a script for redirection. Requires datastar_py.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

@app.get("/redirect")
@datastar_response
async def redirect_from_backend():
    yield SSE.patch_elements('<div id="indicator">Redirecting in 3 seconds...</div>')
    await asyncio.sleep(3)
    yield SSE.execute_script('setTimeout(() => window.location = "/guide")')

```

--------------------------------

### Redirect with Delay using SSE in Clojure

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

A Clojure example using datastar-clojure to handle SSE. It defines a handler that patches elements, sleeps, and then redirects the user using d*/redirect!.

```clojure
(require
  '[starfederation.datastar.clojure.api :as d*]
  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]
  '[some.hiccup.library :refer [html]])


(defn handler [ring-request]
  (->sse-response ring-request
    {on-open
      (fn [sse]
        (d*/patch-elements! sse
          (html [:div#indicator "Redirecting in 3 seconds..."]))
        (Thread/sleep 3000)
        (d*/redirect! sse "/guide")
        (d*/close-sse! sse))}))

```

--------------------------------

### Custom Request Cancellation

Source: https://data-star.dev/reference/actions

Examples of disabling automatic cancellation or using an AbortController for manual request management.

```html
1<!-- Allow concurrent requests (no automatic cancellation) -->
2<button data-on:click="@get('/endpoint', {requestCancellation: 'disabled'})">Allow Multiple</button>
3
4<!-- Custom abort controller for fine-grained control -->
5<div data-signals:controller="new AbortController()">
6    <button data-on:click="@get('/endpoint', {requestCancellation: $controller})">Start Request</button>
7    <button data-on:click="$controller.abort()">Cancel Request</button>
8</div>
```

--------------------------------

### Ruby Rack Handler for Data-Star

Source: https://data-star.dev/docs.md

Initializes a Data-Star dispatcher within a Rack handler context. This snippet shows the setup for using Data-Star in a Ruby Rack application.

```ruby
require 'datastar'

# Create a Datastar::Dispatcher instance

datastar = Datastar.new(request:, response:)

# In a Rack handler, you can instantiate from the Rack env
# datastar = Datastar.from_rack_env(env)

```

--------------------------------

### Initial Signal Value from Element

Source: https://data-star.dev/reference

The initial value of a signal bound with `data-bind` is set to the element's value, unless the signal is already defined. This example sets `$fooBar` to `baz`.

```html
<input data-bind:foo-bar value="baz" />
```

--------------------------------

### Rocket Light DOM Component Example

Source: https://data-star.dev/docs.md

A simple Rocket component using 'light' DOM mode, rendering a span with a label prop. This component will inherit styles from the parent page.

```javascript
rocket('demo-chip', {
  mode: 'light',
  props: ({ string }) => ({
    label: string.default('Chip'),
  }),
  render({ html, props: { label } }) {
    return html`<span class="chip">${label}</span>`
  },
})
```

--------------------------------

### Redirect with Delay using SSE in Rust

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

A Rust example using the datastar crate to send SSE events. It yields events to patch elements, waits, and then yields an event to execute a script for redirection. Uses async_stream.

```rust
use datastar::prelude::*;
use async_stream::stream;
use core::time::Duration;

Sse(stream! {
    yield PatchElements::new("<div id='indicator'>Redirecting in 3 seconds...</div>").into();
    tokio::time::sleep(core::time::Duration::from_secs(3)).await;
    yield ExecuteScript::new("setTimeout(() => window.location = '/guide')").into();
});

```

--------------------------------

### Override Property Setter

Source: https://data-star.dev/reference/rocket

Customizes the setter for a component property during setup.

```javascript
1rocket('demo-prop-normalize', {
  props: ({ string }) => ({
    value: string.default(''),
  }),
  setup({ overrideProp }) {
    overrideProp('value', undefined, (value, setDefault) => {
      setDefault(String(value ?? '').trim())
    })
  },
})
```

--------------------------------

### Redirect with Delay using SSE in Node.js

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This Node.js example uses the http module and ServerSentEventGenerator to stream SSE. It patches elements, sets a timeout to execute a script for redirection.

```javascript
import { createServer } from "node:http";
import { ServerSentEventGenerator } from "../npm/esm/node/serverSentEventGenerator.js";

const server = createServer(async (req, res) => {

  ServerSentEventGenerator.stream(req, res, async (sse) => {
    sse.patchElements(`
      <div id="indicator">Redirecting in 3 seconds...</div>
    `);

    setTimeout(() => {
      sse.executeScript(`setTimeout(() => window.location = "/guide")`);
    }, 3000);
  });
});

```

--------------------------------

### JavaScript SSE Stream with Patch Signals

Source: https://data-star.dev/guide/reactive_signals

Create a Server-Sent Events stream in JavaScript using Datastar's SDK. This example demonstrates sending patch signals with a delay using `setTimeout`.

```javascript
// Creates a new `ServerSentEventGenerator` instance (this also sends required headers)
ServerSentEventGenerator.stream(req, res, (stream) => {
    // Patches signals.
    stream.patchSignals({'hal': 'Affirmative, Dave. I read you.'});

    setTimeout(() => {
        stream.patchSignals({'hal': '...'});
    }, 1000);
});
```

--------------------------------

### Redirect with Delay using DatastarService in C#

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This C# example uses IDatastarService to perform a redirect after patching elements and a delay. It's a more direct approach to redirection compared to executing a script.

```csharp
using StarFederation.Datastar.DependencyInjection;
using StarFederation.Datastar.Scripts;

app.MapGet("/redirect", async (IDatastarService datastarService) =>
{
    await datastarService.PatchElementsAsync("<div id=\"indicator\">Redirecting in 3 seconds...</div>");
    await Task.Delay(TimeSpan.FromSeconds(3));
    await datastarService.Redirect("/guide");
});

```

--------------------------------

### Creating a Basic Custom Codec

Source: https://data-star.dev/reference/rocket

Demonstrates how to use `createCodec` to wrap custom decode and encode functions into a Rocket prop codec. This is useful for integrating custom data normalization logic.

```javascript
import { createCodec } from '/bundles/datastar-pro.js'

let myCodec = createCodec({
  decode(value) {
    // normalize input
  },
  encode(value) {
    // reflect back to attribute text
  },
})
```

--------------------------------

### HTML Usage Example for Light and Shadow DOM Counters

Source: https://data-star.dev/examples/rocket_projection

This HTML structure defines two custom elements, 'light-counter' and 'slot-counter', demonstrating how to embed interactive buttons that update local state using Rocket's `$$` syntax for click events and text display.

```html
 1<light-counter>
 2    <div class="callout success">
 3        <button
 4            data-on:click="$$clicks++"
 5            data-text="'Light clicks: ' + $$clicks"
 6        ></button>
 7    </div>
 8</light-counter>
 9
10<slot-counter>
11    <button
12        data-on:click="$$clicks++"
13        data-text="'Shadow clicks: ' + $$clicks"
14    ></button>
15</slot-counter>
```

--------------------------------

### Ruby: Initialize Datastar for SSE

Source: https://data-star.dev/docs.md

This Ruby snippet shows how to initialize a Datastar::Dispatcher instance for handling Server-Sent Events.

```ruby
require 'datastar'

# Create a Datastar::Dispatcher instance

datastar = Datastar.new(request:, response:)

# In a Rack handler, you can instantiate from the Rack env
# datastar = Datastar.from_rack_env(env)
```

--------------------------------

### Reference Element Using Signal

Source: https://data-star.dev/reference/attributes

The signal created by `data-ref` can be used to reference the element. This example shows how to access the element's tag name.

```html
$foo is a reference to a <span data-text="$foo.tagName"></span> element
```

--------------------------------

### Submit Form via Submit Listener

Source: https://data-star.dev/examples/form_data

Triggers a GET request upon form submission using the data-on:submit attribute.

```html
<form data-on:submit="@get('/endpoint', {contentType: 'form'})">
    foo: <input type="text" name="foo" required />
    <button>
        Submit form
    </button>
</form>
```

--------------------------------

### Datastar Starfield Attributes

Source: https://data-star.dev/

Example of using Datastar's data-attr:* attribute to bind reactive signals to web component attributes.

```html
<star-field
    data-attr:center-x="$x"
    data-attr:center-y="$y"
    data-attr:speed="$speed"
></star-field>
```

--------------------------------

### Shadow DOM Component Example

Source: https://data-star.dev/reference/rocket

A 'demo-modal-frame' component using open shadow DOM mode. It includes encapsulated styles and renders a title within a styled div.

```javascript
1rocket('demo-modal-frame', {
2  mode: 'open',
3  props: ({ string }) => ({
4    title: string.default('Dialog'),
5  }),
6  render({ html, props: { title } }) {
7    return html`
8      <style>
9        :host { display: block; }
10        .frame { border: 1px solid #d4d4d8; padding: 1rem; }
11      </style>
12      <div class="frame">${title}</div>
13    `
14  },
15})
```

--------------------------------

### Implementing onFirstRender for Input Value Synchronization

Source: https://data-star.dev/docs.md

This example demonstrates using `onFirstRender` to synchronize an input element's value with a component prop. It utilizes `overrideProp` to manage bidirectional data flow and `refs` to access the DOM element.

```typescript
rocket('demo-input-bridge', {
  props: ({ string }) => ({
    value: string.default(''),
  }),
  render: ({ html, props: { value } }) => html`
    <input data-ref:input value="${value}">
  `,
  onFirstRender({ overrideProp, refs }) {
    overrideProp(
      'value',
      (getDefault) => refs.input?.value ?? getDefault(),
      (value, setDefault) => {
        const next = String(value ?? '')
        if (refs.input && refs.input.value !== next) refs.input.value = next
        setDefault(next)
      },
    )
  },
})
```

--------------------------------

### Active Search Input Field

Source: https://data-star.dev/examples/active_search

An input field configured to trigger a debounced GET request upon user input.

```html
<input
    type="text"
    placeholder="Search..."
    data-bind:search
    data-on:input__debounce.200ms="@get('/examples/active_search/search')"
/>
```

--------------------------------

### onFirstRender Hook

Source: https://data-star.dev/docs.md

The `onFirstRender` hook runs once after the initial render and ref population. It's ideal for DOM interactions, ref-based accessors, and third-party widget setup.

```APIDOC
## `onFirstRender` Hook

### Description
Runs once per connected instance after Rocket has finished the initial `render()`, Datastar `apply(...)`, and ref population pass. Use it for work that depends on rendered DOM or `data-ref:*` refs.

### Signature
```typescript
onFirstRender?: (context: SetupContext<InferProps<Defs>> & { refs: Record<string, any> }) => void
```

### Usage
This hook is suitable for ref-backed host accessors, DOM measurements, focus management, or third-party widget setup that requires actual rendered nodes. If logic doesn't rely on refs, it should be kept in `setup`.

### Example
```javascript
rocket('demo-input-bridge', {
  props: ({ string }) => ({
    value: string.default(''),
  }),
  render: ({ html, props: { value } }) => html`
    <input data-ref:input value="${value}">
  `,
  onFirstRender({ overrideProp, refs }) {
    overrideProp(
      'value',
      (getDefault) => refs.input?.value ?? getDefault(),
      (value, setDefault) => {
        const next = String(value ?? '')
        if (refs.input && refs.input.value !== next) refs.input.value = next
        setDefault(next)
      },
    )
  },
})
```
```

--------------------------------

### Initialize OpenFreeMap Component

Source: https://data-star.dev/examples/rocket_openfreemap

Configures the map component using data-signals to manage style and viewport state.

```html
 1<div data-signals='{"style":"liberty","styleUrl":"https://tiles.openfreemap.org/styles/liberty","view":{"center":[-115.172816,36.114647],"zoom":13.8,"bearing":0,"pitch":0}}'>
 2    <openfreemap-map
 3        data-attr:style-url="$styleUrl"
 4        data-attr:center="$view.center"
 5        data-attr:zoom="$view.zoom"
 6        data-attr:bearing="$view.bearing"
 7        data-attr:pitch="$view.pitch"
 8        data-attr:drag-rotate="$style == 'liberty-3d' || $style == 'dark-3d'"
 9        data-attr:cluster="true"
10        data-attr:cluster-max-zoom="14"
11    ></openfreemap-map>
12</div>
```

--------------------------------

### Set HTML Attribute with Expression

Source: https://data-star.dev/reference

Use `data-attr` to set any HTML attribute to an expression and keep it in sync. This example sets the `aria-label` attribute.

```html
<div data-attr:aria-label="$foo"></div>
```

--------------------------------

### Go SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Uses `datastar-go` to create an SSE connection, patch elements, and execute a JavaScript redirect.

```go
import (
    "time"
    "github.com/starfederation/datastar-go/datastar"
)

sse := datastar.NewSSE(w, r)
sse.PatchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`)
time.Sleep(3 * time.Second)
sse.ExecuteScript(`
    window.location = "/guide"
`)
```

--------------------------------

### Use Alert Action in HTML

Source: https://data-star.dev/examples/custom_plugin

Example of using the custom 'alert' action within an HTML button's click event. The action is invoked with a string argument.

```html
1<button data-on:click="@alert('Hello from an action')">
2    Alert using an action
</button>
```

--------------------------------

### Rocket Biome Configuration Override

Source: https://data-star.dev/docs.md

This Biome configuration override is used in Rocket example sources to prevent `lint/suspicious/noTemplateCurlyInString` warnings for intentional template literals.

```json
{
  "overrides": [
    {
      "includes": ["site/shared/static/rocket/**/*.js"],
      "linter": {
        "rules": {
          "suspicious": {
            "noTemplateCurlyInString": "off"
          }
        }
      }
    }
  ]
}
```

--------------------------------

### Use Alert Attribute in HTML

Source: https://data-star.dev/examples/custom_plugin

Example of using the custom 'alert' attribute on an HTML button. The attribute expects a string value, which is then displayed in the alert.

```html
1<button data-alert="'Hello from an attribute'">
2    Alert using an attribute
</button>
```

--------------------------------

### Display All Signal Changes

Source: https://data-star.dev/examples/on_signal_patch

Initial state for tracking all signal changes.

```json
{"allChanges":[]}
```

--------------------------------

### Preserving Signal Type During Binding

Source: https://data-star.dev/reference

When a signal is predefined, its type is preserved during binding. This example sets `$fooBar` to the number `10` when the option is selected.

```html
<div data-signals:foo-bar="0">
    <select data-bind:foo-bar>
        <option value="10">10</option>
    </select>
</div>
```

--------------------------------

### Format date and time in a specific locale

Source: https://data-star.dev/docs.md

Use the @intl() function to format a date and time in a specified locale ('de-AT' in this example). Provide the 'datetime' type and detailed formatting options.

```html
<div data-text="@intl('datetime', new Date(), {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'}, 'de-AT')"></div>
```

--------------------------------

### Define a Simple User Card Rocket Component

Source: https://data-star.dev/reference/rocket

A basic example of a Rocket component that displays a user's name. It defines a 'name' prop with a default value and renders a paragraph element with the name.

```javascript
rocket('demo-user-card', {
  props: ({ string }) => ({
    name: string.default('Anonymous'),
  }),
  render({ html, props: { name } }) {
    return html`<p>${name}</p>`
  },
})

```

--------------------------------

### Debounce Signal Patch Listener

Source: https://data-star.dev/reference/attributes

Apply modifiers like `__debounce` to control the timing of `data-on-signal-patch` event listeners. This example debounces the listener for 500ms.

```html
<div data-on-signal-patch__debounce.500ms="doSomething()"></div>
```

--------------------------------

### Rocket Scope Rewriting Example

Source: https://data-star.dev/docs.md

Rocket rewrites `$$name` to `_rocket.<component_id>.<instance_id>.name` for isolated local state. Always write `$$name` in your component code.

```javascript
// You write this in render():
html`
  <button data-on:click="$$count += 1"></button>
  <span data-text="$$count"></span>
`

// For <demo-counter id="inventory-panel">, Rocket rewrites it as:
<button data-on:click="_rocket.demo_counter.inventory_panel.count += 1"></button>
<span data-text="_rocket.demo_counter.inventory_panel.count"></span>
```

--------------------------------

### Include Datastar from Local Path

Source: https://data-star.dev/guide/getting_started

If you host the Datastar file yourself, include it using this script tag pointing to its local path.

```html
<script type="module" src="/path/to/datastar.js"></script>
```

--------------------------------

### Set Multiple HTML Attributes

Source: https://data-star.dev/reference

Use `data-attr` with a key-value object to set multiple HTML attributes simultaneously. This example sets `aria-label` and `disabled` attributes.

```html
<div data-attr="{'aria-label': $foo, disabled: $bar}"></div>
```

--------------------------------

### Python: Async Redirect with Server-Sent Events

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Utilize datastar_response and SSE to patch elements and perform an asynchronous redirect.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

@app.get("/redirect")
@datastar_response
async def redirect_from_backend():
    yield SSE.patch_elements('<div id="indicator">Redirecting in 3 seconds...</div>')
    await asyncio.sleep(3)
    yield SSE.redirect("/guide")
```

--------------------------------

### DRY Button Clicks with Templating Variable

Source: https://data-star.dev/how_tos/keep_datastar_code_dry

Solves code repetition by defining the backend action in a templating variable and reusing it. This requires setup within your templating language.

```html
{% set action = "@get('/endpoint')" %}
<button data-on:click="{{ action }}">Click me</button>
<button data-on:click="{{ action }}">No, click me!</button>
<button data-on:click="{{ action }}">Click us all!</button>
```

--------------------------------

### Preserve Multiple Attributes on DOM Morph

Source: https://data-star.dev/reference/attributes

Multiple attributes can be preserved by separating them with a space in the `data-preserve-attr` value. This example preserves `open` and `class` attributes.

```html
<details open class="foo" data-preserve-attr="open class">
    <summary>Title</summary>
    Content
</details>
```

--------------------------------

### Submit Form Data via GET and POST

Source: https://data-star.dev/examples/form_data

Uses the contentType: 'form' option to send form data. The selector option allows targeting a form from outside its scope.

```html
<form id="myform">
    foo:<input type="checkbox" name="checkboxes" value="foo" />
    bar:<input type="checkbox" name="checkboxes" value="bar" />
    baz:<input type="checkbox" name="checkboxes" value="baz" />
    <button data-on:click="@get('/endpoint', {contentType: 'form'})">
        Submit GET request
    </button>
    <button data-on:click="@post('/endpoint', {contentType: 'form'})">
        Submit POST request
    </button>
</form>

<button data-on:click="@get('/endpoint', {contentType: 'form', selector: '#myform'})">
    Submit GET request from outside the form
</button>
```

--------------------------------

### Preserve Single Attribute on DOM Morph

Source: https://data-star.dev/reference/attributes

The `data-preserve-attr` attribute prevents specified attributes from being morphed during DOM updates. This example preserves the `open` attribute.

```html
<details open data-preserve-attr="open">
    <summary>Title</summary>
    Content
</details>
```

--------------------------------

### Two-Way Data Binding to Signal

Source: https://data-star.dev/reference

Use `data-bind` to create a two-way data binding between an element's state and a signal. This example binds the input's value to the `foo` signal.

```html
<input data-bind:foo />
```

--------------------------------

### Datastar Server-Sent Events (SSE) Patch

Source: https://data-star.dev/

Example of using Datastar's sse.PatchElements function to update DOM elements via server-sent events. Includes a delay to demonstrate state changes.

```go
sse.PatchElements("\n    <div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>\n")
time.Sleep(1 * time.Second)
sse.PatchElements("<div id=\"hal\">Waiting for an order...</div>")
```

--------------------------------

### CQRS Endpoint Initialization and Click Handler

Source: https://data-star.dev/guide/the_tao_of_datastar

This snippet demonstrates how to initialize a Datastar component with a backend endpoint and attach a click handler that triggers a POST request. Use this for basic CQRS patterns where a button initiates a write operation.

```html
<div id="main" data-init="@get('/cqrs_endpoint')">
    <button data-on:click="@post('/do_something')">
        Do something
    </button>
</div>
```

--------------------------------

### Define Custom Element with Datastar

Source: https://data-star.dev/reference/rocket

Defines a custom element 'demo-copy-button' using Datastar, configuring props, setup logic, and render function. Use this to create reusable components with reactive state and declarative rendering.

```javascript
1rocket('demo-copy-button', {
  props: ({ string, number }) => ({
    text: string.default('Copy me'),
    resetMs: number.min(100).default(1200),
  }),
  setup({ $$, $, action, actions, cleanup, props }) {
    $$.copied = false
    $$.label = () => ($$.copied ? 'Copied' : 'Copy')
    $$.resetMsLabel = actions.intl(
      'number',
      props.resetMs,
      { maximumFractionDigits: 0 },
      'en-US',
    )
    let timerId = 0

    action('copy', async () => {
      await navigator.clipboard.writeText(props.text)
      $$.copied = true
      if ($.analyticsEnabled !== false) {
        $.lastCopiedText = props.text
      }
      clearTimeout(timerId)
      timerId = window.setTimeout(() => {
        $$.copied = false
      }, props.resetMs)
    })

    cleanup(() => clearTimeout(timerId))
  },
  render({ html, props: { text } }) {
    return html`
      <button data-on:click="@copy()">
        <span data-text="$$label"></span>
        <small>${text} ($$resetMsLabel ms)</small>
      </button>
    `
  },
})
```

--------------------------------

### Trim and Normalize Prop Value

Source: https://data-star.dev/docs.md

This example demonstrates overriding the 'value' prop to trim whitespace before setting the default value. It's useful for input fields where leading/trailing spaces should be ignored.

```typescript
rocket('demo-prop-normalize', {
  props: ({ string }) => ({
    value: string.default(''),
  }),
  setup({ overrideProp }) {
    overrideProp('value', undefined, (value, setDefault) => {
      setDefault(String(value ?? '').trim())
    })
  },
})
```

--------------------------------

### Conditional Re-render with renderOnPropChange

Source: https://data-star.dev/reference/rocket

Example of using `renderOnPropChange` to conditionally trigger a re-render only when the 'theme' prop changes. This optimizes performance by skipping DOM updates when unrelated props change.

```javascript
1rocket('demo-chart', {
2  props: ({ json, string }) => ({
3    series: json.default(() => []),
4    theme: string.default('light'),
5  }),
6  mode: 'light',
7  renderOnPropChange({ changes }) {
8    return 'theme' in changes
9  },
10  setup({ host, observeProps, props }) {
11    observeProps(() => {
12      drawChart(host, props.series, props.theme)
13    }, 'series', 'theme')
14  },
15  render({ html }) {
16    return html`<canvas width="640" height="320"></canvas>`
17  },
18})
```

--------------------------------

### Append Item and Update Signals with DataStar (Python)

Source: https://data-star.dev/how_tos/load_more_list_items

Appends a new item to a list and updates the offset signal if the maximum number of items has not been reached. Otherwise, it removes the load more button. This example uses FastAPI.

```Python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import datastar_response, ReadSignals

MAX_ITEMS = 5

@app.get("/how_tos/load_more/data")
@datastar_response
async def load_data(signals: ReadSignals):
    if signals["offset"] < MAX_ITEMS:
        new_offset = signals["offset"] + 1
        yield SSE.patch_elements(
            f"<div>Item {new_offset}</div>",
            mode=ElementPatchMode.APPEND,
            selector="#list"
        )
        if new_offset < MAX_ITEMS:
            yield SSE.patch_signals({"offset": new_offset})
        else:
            yield SSE.remove_elements("#load-more")
```

--------------------------------

### Initialize Flow Component

Source: https://data-star.dev/examples/rocket_flow

Sets up the SVG grid, layers, and event listeners for pointer and wheel interactions.

```javascript
const init = () => {
      if (!ensureRefs()) return
      const patternId = `flow-grid-${/** @type {HTMLElement & { rocketInstanceId?: string }} */ (host).rocketInstanceId ?? ''}`
      gridPattern.id = patternId
      background.setAttribute('fill', `url(#${patternId})`)
      edgesLayer = ensureLayer('edges')
      nodesLayer = ensureLayer('nodes')
      schedule()
      svg.addEventListener('pointerdown', pointerDown)
      svg.addEventListener('wheel', handleWheel, { passive: false })
      const resize = new ResizeObserver(schedule)
      resize.observe(svg)
      cleanup(() => resize.disconnect())
    }
```

--------------------------------

### Calculate Bezier Curve Control Points

Source: https://data-star.dev/examples/rocket_flow

Determines control points for a cubic bezier curve based on start and end points, optimizing for horizontal or vertical alignment.

```javascript
const bezierPathPoints = (sx, sy, tx, ty) => {
  const dx = tx - sx
  const dy = ty - sy
  if (Math.abs(dx) >= Math.abs(dy)) {
    const midX = sx + dx * 0.5
    return { c1x: midX, c1y: sy, c2x: midX, c2y: ty }
  }
  const midY = sy + dy * 0.5
  return { c1x: sx, c1y: midY, c2x: tx, c2y: midY }
}
```

--------------------------------

### Using Computed Signals in Expressions

Source: https://data-star.dev/reference/attributes

Demonstrates creating a computed signal `foo` and then using its value in another binding (`data-text`).

```html
1<div data-computed:foo="$bar + $baz"></div>
2<div data-text="$foo"></div>
```

--------------------------------

### Binding Multiple Checkbox Values to an Array Signal

Source: https://data-star.dev/reference

Predefine a signal as an array to bind multiple checkbox values to it. This example sets `$fooBar` to `["fizz", "baz"]` when both checkboxes are checked.

```html
<div data-signals:foo-bar="[]">
    <input data-bind:foo-bar type="checkbox" value="fizz" />
    <input data-bind:foo-bar type="checkbox" value="baz" />
</div>
```

--------------------------------

### Implement Server-Driven Quiz UI

Source: https://data-star.dev/guide/backend_requests

Uses data-signals and data-on:click to fetch data from the server and update the UI based on signal state.

```html
<div
    data-signals="{response: '', answer: ''}"
    data-computed:correct="$response.toLowerCase() == $answer"
>
    <div id="question"></div>
    <button data-on:click="@get('/actions/quiz')">Fetch a question</button>
    <button
        data-show="$answer != ''"
        data-on:click="$response = prompt('Answer:') ?? ''"
    >
        BUZZ
    </button>
    <div data-show="$response != ''">
        You answered “<span data-text="$response"></span>”.
        <span data-show="$correct">That is correct ✅</span>
        <span data-show="!$correct">
        The correct answer is “<span data-text="$answer"></span>” 🤷
        </span>
    </div>
</div>
```

--------------------------------

### Execute Script with Go SDK

Source: https://data-star.dev/guide/datastar_expressions

Uses the Go SDK helper function to trigger script execution via SSE.

```go
sse := datastar.NewSSE(writer, request)
sse.ExecuteScript(`alert('This mission is too important for me to allow you to jeopardize it.')`)
```

--------------------------------

### Create a file upload interface

Source: https://data-star.dev/examples/file_upload

Uses data-bind to capture files and data-on to trigger a POST request. The input must be bound to a signal to enable automatic base64 encoding.

```html
 1<label>
 2    <p>Pick anything less than 1MB</p>
 3    <input type="file" data-bind:files multiple/>
 4</label>
 5<button
 6    class="warning"
 7    data-on:click="$files.length && @post('/examples/file_upload')"
 8    data-attr:disabled="!$files.length"
 9>
10    Submit
11</button>
```

--------------------------------

### Rocket Component with Conditional RenderOnPropChange

Source: https://data-star.dev/docs.md

Example of a Rocket component where `renderOnPropChange` is a function, allowing re-renders only when the 'theme' prop changes. Other prop changes like 'series' update state but skip DOM rerendering.

```javascript
rocket('demo-chart', {
  props: ({ json, string }) => ({
    series: json.default(() => []),
    theme: string.default('light'),
  }),
  mode: 'light',
  renderOnPropChange({ changes }) {
    return 'theme' in changes
  },
  setup({ host, observeProps, props }) {
    observeProps(() => {
      drawChart(host, props.series, props.theme)
    }, 'series', 'theme')
  },
  render({ html }) {
    return html`<canvas width="640" height="320"></canvas>`
  },
})
```

--------------------------------

### Define Component Props and Render

Source: https://data-star.dev/docs.md

Demonstrates defining component props with built-in codecs and using them within a render function.

```javascript
rocket('demo-badge', {
  props: ({ string, bool, number }) => ({
    label: string.trim.default('New'),
    tone: string.lower.default('neutral'),
    visible: bool.default(true),
    priority: number.clamp(0, 5),
  }),
  render({ html, props: { label, tone, visible, priority } }) {
    return html`
      <span
        data-show="${visible}"
        data-attr:data-tone="${tone}"
        data-text="${label + ' #' + priority}">
      </span>
    `
  },
})

const badge = document.querySelector('demo-badge')

// Property write:
badge.priority = 7

// Reflected attribute after encoding:
// <demo-badge priority="5"></demo-badge>

// Attribute write:
badge.setAttribute('label', '  shipped  ')

// Decoded prop value in setup/render:
// props.label === 'shipped'
```

--------------------------------

### Two-Way Data Binding with Signal in Value

Source: https://data-star.dev/reference

Use `data-bind` to bind an element's state to a signal, specifying the signal name in the attribute's value. This example binds the input's value to the `foo` signal.

```html
<input data-bind="foo" />
```

--------------------------------

### Go Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Go implementation for sending SSE patch elements using DataStar. It formats the current time and patches the `#time` div.

```go
import (
    "time"
    "github.com/starfederation/datastar-go/datastar"
)

currentTime := time.Now().Format("2006-01-02 15:04:05")

sse := datastar.NewSSE(w, r)
sse.PatchElements(fmt.Sprintf(`
    <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
        %s
    </div>
`, currentTime))

```

--------------------------------

### Implement Templ Counter HTML

Source: https://data-star.dev/examples/templ_counter

Uses data-init and data-on attributes to handle server-side state updates via patch requests.

```html
 1<div data-init="@get('/examples/templ_counter/updates')">
 2    <!-- Global Counter -->
 3    <button
 4        id="global"
 5        class="info"
 6        data-on:click="@patch('/examples/templ_counter/global')"
 7    >
 8        Global Clicks: 0
 9    </button>
10
11    <!-- User Counter -->
12    <button
13        id="user"
14        class="success"
15        data-on:click="@patch('/examples/templ_counter/user')"
16    >
17        User Clicks: 0
18    </button>
19</div>
```

--------------------------------

### Bind HTML attribute to expression with data-attr

Source: https://data-star.dev/docs.md

Use data-attr to bind any HTML attribute to an expression. The attribute name is converted to kebab case. For example, data-attr:aria-hidden sets the aria-hidden attribute.

```html
<input data-bind:foo />
<button data-attr:disabled="$foo == ''">
    Save
</button>
```

```html
<button data-attr:aria-hidden="$foo">Save</button>
```

```html
<button data-attr="{disabled: $foo == '', 'aria-hidden': $foo}">Save</button>
```

--------------------------------

### C#: Add DataStar Service and Handle SSE

Source: https://data-star.dev/docs.md

This C# code snippet shows how to add DataStar as a service and handle SSE requests by patching elements and signals into the DOM.

```csharp
using StarFederation.Datastar.DependencyInjection;

// Adds Datastar as a service
builder.Services.AddDatastar();

app.MapGet("/", async (IDatastarService datastarService) =>
{
    // Patches elements into the DOM.
    await datastarService.PatchElementsAsync(@"<div id=\"question\">What do you put in a toaster?</div>");

    // Patches signals.
    await datastarService.PatchSignalsAsync(new { response = "", answer = "bread" });
});
```

--------------------------------

### Define DataStar Flow Edge Component

Source: https://data-star.dev/examples/rocket_flow

Defines the 'flow-edge' component using the rocket function. It specifies component props and the setup logic for managing edge behavior, including event emission and attribute observation.

```javascript
1106rocket('flow-edge', {
  props: ({ string, bool }) => ({
    source: string,
    target: string,
    label: string,
    animated: bool,
  }),
  setup({ cleanup, effect, host, props }) {
    host.style.display = 'none'

    const snapshot = () => ({
      id: host.getAttribute('id') ?? '',
      source: host.getAttribute('source') ?? props.source,
      target: host.getAttribute('target') ?? props.target,
      label: host.getAttribute('label') ?? props.label,
      animated: props.animated || host.hasAttribute('animated'),
    })

    const emit = (name) => {
      host.dispatchEvent(
        new CustomEvent(name, {
          detail: snapshot(),
          bubbles: true,
          composed: true,
        }),
      )
    }

    const observer = new MutationObserver(() =>
      queueMicrotask(() => emit('flow-edge-update')),
    )
    observer.observe(host, { attributes: true })

    queueMicrotask(() => emit('flow-edge-register'))
    cleanup(() => {
      observer.disconnect()
      emit('flow-edge-remove')
    })
    effect(() => {
      props.source
      props.target
      props.label
      props.animated
      emit('flow-edge-update')
    })
  },
})

```

--------------------------------

### Initialize MapLibre GL Map and Event Listeners

Source: https://data-star.dev/examples/rocket_openfreemap

Configures map controls, handles missing style images, and attaches event listeners for map lifecycle and user interactions.

```javascript
map.addControl(
        new maplibregl.NavigationControl({ showCompass: false }),
        'top-right',
      )
      map.on('styleimagemissing', (evt) => {
        if (!evt?.id || map.hasImage(evt.id)) return
        try {
          map.addImage(evt.id, {
            width: 1,
            height: 1,
            data: new Uint8Array([0, 0, 0, 0]),
          })
        } catch {}
      })
      map.on('load', ensure3DBuildings)
      map.on('style.load', ensure3DBuildings)
      map.on('styledata', ensure3DBuildings)
      map.on('zoomend', syncMarkers)
      map.on('moveend', syncMarkers)
      map.on('idle', syncMarkers)
      map.on('style.load', syncMarkers)
      map.on('click', clusterLayerID, async (evt) => {
        const feature = map.queryRenderedFeatures(evt.point, {
          layers: [clusterLayerID],
        })[0]
        const clusterID = Number(feature?.properties?.cluster_id)
        if (!feature || !Number.isFinite(clusterID)) return
        const source = map.getSource(clusterSourceID)
        if (!source || typeof source.getClusterExpansionZoom !== 'function')
          return
        try {
          const zoom = await source.getClusterExpansionZoom(clusterID)
          const [lng, lat] = feature.geometry?.coordinates ?? []
          if (!Number.isFinite(lng) || !Number.isFinite(lat)) return
          map.easeTo({ center: [lng, lat], zoom })
        } catch {}
      })
      map.on('mouseenter', clusterLayerID, () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', clusterLayerID, () => {
        map.getCanvas().style.cursor = ''
      })

      new ResizeObserver(() => map.resize()).observe(host)
      syncMarkers()
```

--------------------------------

### Basic Signal and Text Binding in Datastar

Source: https://data-star.dev/guide/reactive_signals

This snippet demonstrates how to declare a signal using `data-signals` and bind it to an element's text content using `data-text`. It also shows how to update a signal with an event handler using `data-on:click`.

```html
<div data-signals:hal="'...'" >
    <button data-on:click="$hal = 'Affirmative, Dave. I read you.'">
        HAL, do you read me?
    </button>
    <div data-text="$hal"></div>
</div>
```

--------------------------------

### Ruby SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Uses `Datastar.new` to create an SSE stream, patching elements and executing a script for redirection.

```ruby
datastar = Datastar.new(request:, response:)

datastar.stream do |sse|
  sse.patch_elements '<div id="indicator">Redirecting in 3 seconds...</div>'
  sleep 3
  sse.execute_script 'window.location = "/guide"'
end
```

--------------------------------

### Configure Datastar Request Options

Source: https://data-star.dev/reference/actions

Demonstrates applying custom options like signal filtering, headers, and cancellation policies to a button click event.

```html
1<button data-on:click="@get('/endpoint', {
2    filterSignals: {include: /^foo\./},
3    headers: {
4        'X-Csrf-Token': 'JImikTbsoCYQ9oGOcvugov0Awc5LbqFsZW6ObRCxuq',
5    },
6    openWhenHidden: true,
7    requestCancellation: 'disabled',
8})"></button>
```

--------------------------------

### Define Frontend Signals

Source: https://data-star.dev/guide/reactive_signals

HTML structure for initializing signals and triggering backend actions.

```html
1<div data-signals:hal="'...'">
2    <button data-on:click="@get('/endpoint')">
3        HAL, do you read me?
4    </button>
5    <div data-text="$hal"></div>
6</div>
```

--------------------------------

### Rocket Component Definition

Source: https://data-star.dev/examples/rocket_letter_stream

Defines the 'alphabet-stream' component using the datastar rocket function. It manages an animated letter stream, deriving blocks and rows from a seed string and appending letters until 'Z'. The setup function initializes the letters, defines a computed property for blocks, and schedules the next letter stream animation.

```javascript
1import { rocket } from 'datastar'
  2
  3rocket('alphabet-stream', {
  4  props({ string }) {
  5    return { seed: string.default('ABCDEF') }
  6  },
  7  setup({ props, $$ }) {
  8    $$.letters = props.seed.split('')
  9    $$.blocks = () => {
 10      const letters = [...$$.letters]
 11      const blocks = []
 12      for (let offset = 0; offset < letters.length; offset += 9) {
 13        const rows = []
 14        for (let rowOffset = offset; rowOffset < offset + 9; rowOffset += 3) {
 15          const cells = letters.slice(rowOffset, rowOffset + 3)
 16          if (!cells.length) continue
 17          rows.push({
 18            name: `Row ${rows.length + 1}`,
 19            cells,
 20          })
 21        }
 22        if (!rows.length) continue
 23        blocks.push({
 24          name: `Block ${blocks.length + 1}`,
 25          rows,
 26        })
 27      }
 28      return blocks
 29    }
 30    let nextCode = 65 + $$.letters.length
 31    const streamNextLetter = () => {
 32      $$.letters.push(String.fromCharCode(nextCode++))
 33      if (nextCode <= 90) requestAnimationFrame(streamNextLetter)
 34    }
 35    requestAnimationFrame(streamNextLetter)
 36  },
 37  render: ({ html }) => html`
 38    <section>
 39      <style>
 40        :host {
 41          display: block;
 42        }
 43
 44        section {
 45          display: grid;
 46          gap: 0.75rem;
 47        }
 48
 49        ul,
 50        ol {
 51          display: flex;
 52          flex-wrap: wrap;
 53          gap: 0.5rem;
 54          list-style: none;
 55          padding: 0;
 56          margin: 0;
 57        }
 58
 59        .block-list {
 60          display: grid;
 61          gap: 1rem;
 62        }
 63
 64        .block-card {
 65          display: grid;
 66          gap: 0.75rem;
 67          padding: 1rem;
 68          border: 1px solid var(--gray-5);
 69          border-radius: 1rem;
 70          background: linear-gradient(180deg, var(--gray-1), var(--gray-2));
 71        }
 72
 73        .block-card h4,
 74        .block-card h5 {
 75          margin: 0;
 76        }
 77
 78        .row-list {
 79          display: grid;
 80          gap: 0.75rem;
 81        }
 82
 83        .cell-list li {
 84          padding: 0.35rem 0.6rem;
 85          border-radius: 999px;
 86          background: var(--blue-2);
 87          color: var(--blue-12);
 88          border: 1px solid var(--blue-6);
 89        }
 90
 91        li strong {
 92          font-variant-numeric: tabular-nums;
 93          margin-right: 0.25rem;
 94        }
 95
 96        p {
 97          margin: 0;
 98          color: var(--gray-11);
 99        }
100
101        code {
102          color: var(--gray-12);
103        }
104      </style>
105
106      <h3>Letter Stream</h3>
107      <p>
108        This example nests three Rocket loops to exercise default and named aliases:
109        outer <code>i</code>, middle <code>j</code>, inner <code>k</code>.
110      </p>
111      <div class="block-list">
112        <template data-for="block in $$blocks">
113          <section class="block-card">
114            <h4 data-text="block.name"></h4>
115            <div class="row-list">
116              <template data-for="row, j in block.rows">
117                <article>
118                  <h5 data-text="row.name"></h5>
119                  <ol class="cell-list">
120                    <template data-for="letter, k in row.cells">
121                      <li>
122                        <strong data-text="letter"></strong>
123                        <span data-text="i + ':' + j + ':' + k"></span>
124                      </li>
125                    </template>
126                  </ol>
127                </article>
128              </template>
129            </div>
130          </section>
131        </template>
132      </div>
133      <div data-text="$$letters.join(' ')"></div>
134    </section>
135  `,
136})
```

--------------------------------

### Render Lists with Rocket

Source: https://data-star.dev/reference/rocket

Demonstrates declarative list rendering using the html helper to map over arrays.

```javascript
 1rocket('demo-nav-list', {
 2  props: ({ array, object, string }) => ({
 3    items: array(object({
 4      href: string.trim.default('#'),
 5      label: string.trim.default('Untitled'),
 6    })),
 7    title: string.trim.default('Navigation'),
 8  }),
 9  render({ html, props: { items, title } }) {
10    return html`
11      <nav aria-label="${title}">
12        <h3>${title}</h3>
13        <ul>
14          ${items.map((item) => html`
15            <li>
16              <a href="${item.href}">${item.label}</a>
17            </li>
18          `)}
19        </ul>
20      </nav>
21    `
22  },
23})
```

--------------------------------

### Initialize Globe Component with Rocket

Source: https://data-star.dev/examples/rocket_globe

This snippet demonstrates how to initialize the Rocket component, which in turn initializes a globe.gl instance. It sets up the globe with image URLs for the base map and topology, and configures initial view and data synchronization.

```javascript
import { rocket } from 'datastar'

const { default: Globe } = await import(
  'https://cdn.jsdelivr.net/npm/globe.gl@2.43.0/+esm'
)
ocket('globe-view', {
  props: ({ json }) => ({
    paths: json.default([]),
    target: json.default([36, -115]),
    places: json.default([]),
    arcs: json.default([]),
  }),
  onFirstRender({ refs, cleanup, host, observeProps, props }) {
    let globe

    const target = () => ({
      lat: props.target?.[0] ?? 36,
      lng: props.target?.[1] ?? -115,
      altitude:
        (refs.container?.offsetWidth ?? 1) /
          (refs.container?.offsetHeight ?? 1) >
        1.5
          ? 0.8
          : (refs.container?.offsetWidth ?? 1) /
                (refs.container?.offsetHeight ?? 1) >
              1
          ? 1.2
          : 1.5,
    })
    const syncTarget = () => {
      if (!globe) return
      globe.pointOfView(target(), 2000)
    }
    const syncPaths = () => {
      if (!globe) return
      if (props.paths?.length) {
        globe
          .pathsData(props.paths)
          .pathPointLat((point) => point[0])
          .pathPointLng((point) => point[1])
          .pathColor(() => '#ff0000')
          .pathStroke(0.5)
        return
      }
      globe.pathsData([])
    }
    const syncArcs = () => {
      if (!globe) return
      if (props.arcs?.length) {
        globe
          .arcsData(props.arcs)
          .arcStartLat((arc) => arc[0][0])
          .arcStartLng((arc) => arc[0][1])
          .arcEndLat((arc) => arc[1][0])
          .arcEndLng((arc) => arc[1][1])
          .arcDashLength(0.5)
          .arcDashGap(0.5)
          .arcDashAnimateTime(1000)
        return
      }
      globe.arcsData([])
    }
    const syncPlaces = () => {
      if (!globe) return
      if (!props.places?.length) {
        globe.htmlElementsData([])
        return
      }
      globe
        .htmlElementsData(
          props.places.map(([name, [lat, lng]]) => ({ name, lat, lng })),
        )
        .htmlLat((entry) => entry.lat)
        .htmlLng((entry) => entry.lng)
        .htmlElement((entry) => {
          const wrapper = document.createElement('div')
          wrapper.className = 'marker-wrapper'
          wrapper.style.cursor = 'pointer'
          wrapper.style.pointerEvents = 'auto'

          const icon = document.createElement('div')
          icon.className = 'marker-icon'
          icon.style.width = '32px'
          icon.style.height = '32px'
          icon.innerHTML = `<svg viewBox="-4 0 36 36" width="32" height="32"><path fill="currentColor" d="M14,0 C21.732,0 28,5.641 28,12.6 C28,23.963 14,36 14,36 C14,36 0,24.064 0,12.6 C0,5.641 6.268,0 14,0 Z"/><circle fill="black" cx="14" cy="14" r="7"/></svg>`

          const label = document.createElement('div')
          label.className = 'marker-label'
          label.textContent = entry.name

          wrapper.append(icon, label)
          wrapper.addEventListener('click', (evt) => {
            evt.preventDefault()
            evt.stopPropagation()
            host.dispatchEvent(
              new CustomEvent('marker-click', {
                detail: { name: entry.name, lat: entry.lat, lng: entry.lng },
                bubbles: true,
                composed: true,
              }),
            )
          })
          return wrapper
        })
    }

    if (refs.container instanceof HTMLElement) {
      globe = Globe()(refs.container)
        .width(refs.container.offsetWidth)
        .height(refs.container.offsetHeight)
        .globeImageUrl(
          'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg',
        )
        .bumpImageUrl(
          'https://unpkg.com/three-globe/example/img/earth-topology.png',
        )
        .pointOfView(target(), 0)
      syncPaths()
      syncTarget()
      syncArcs()
      syncPlaces()
    }

    observeProps(syncPaths, 'paths')
    observeProps(syncTarget, 'target')
    observeProps(syncArcs, 'arcs')
    observeProps(syncPlaces, 'places')

    cleanup(() => globe?._destructor?.())
  },
  render: ({ html }) => html`
    <style>
      :host {
        display: block;
        width: 100%;
        height: 100%;
        position: relative;
        overflow: hidden;
      }

      .globe-container {
        position: absolute;
        inset: 0;
        overflow: hidden;
      }

      .marker-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        transform: translate(-50%, -100%);
        position: relative;
        z-index: 1;

```

--------------------------------

### Patching Elements with Go SDK

Source: https://data-star.dev/guide/getting_started

Initialize a ServerSentEventGenerator and call PatchElements to stream DOM updates.

```go
 1import (
 2    "github.com/starfederation/datastar-go/datastar"
 3    time
 4)
 5
 6// Creates a new `ServerSentEventGenerator` instance.
 7sse := datastar.NewSSE(w,r)
 8
 9// Patches elements into the DOM.
10sse.PatchElements(
11    `<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>`
12)
13
14time.Sleep(1 * time.Second)
15
16sse.PatchElements(
17    `<div id="hal">Waiting for an order...</div>`
18)
```

--------------------------------

### Initialize State with data-init

Source: https://data-star.dev/reference

Executes expressions upon element initialization. Supports modifiers for delays and view transitions.

```html
<div data-init="$count = 1"></div>
```

```html
<div data-init__delay.500ms="$count = 1"></div>
```

--------------------------------

### Define Web Component Integration

Source: https://data-star.dev/guide/datastar_expressions

Demonstrates using a custom element with data-binding and event listeners.

```html
<div data-signals:result="''">
    <input data-bind:foo />
    <my-component
        data-attr:src="$foo"
        data-on:mycustomevent="$result = evt.detail.value"
    ></my-component>
    <span data-text="$result"></span>
</div>
```

--------------------------------

### Implement two-way data binding

Source: https://data-star.dev/guide/reactive_signals

Sets up two-way binding between an input element and a signal. The signal is automatically created if it does not exist.

```html
<input data-bind:foo />
```

```html
<input data-bind="foo" />
```

--------------------------------

### Reading Signals in Ruby

Source: https://data-star.dev/guide/backend_requests

Instantiate the `Datastar` client with the request and response objects, then access signals using bracket notation for direct retrieval.

```ruby
1# Setup with request
2datastar = Datastar.new(request:, response:)
3
4# Read signals
5some_signal = datastar.signals[:some_signal]
```

--------------------------------

### Patch elements and signals via SSE

Source: https://data-star.dev/docs.md

Demonstrates how to send multiple patch events in a single SSE response across various backend languages.

```clojure
(d*/patch-elements! sse "<div id=\"question\">...</div>")
(d*/patch-elements! sse "<div id=\"instructions\">...</div>")
(d*/patch-signals! sse "{answer: '...', prize: '...'}")
```

```csharp
datastarService.PatchElementsAsync(@"<div id=""question"">...</div>");
datastarService.PatchElementsAsync(@"<div id=""instructions"">...</div>");
datastarService.PatchSignalsAsync(new { answer = "...", prize = "..." } );
```

```go
sse.PatchElements(`<div id="question">...</div>`)
sse.PatchElements(`<div id="instructions">...</div>`)
sse.PatchSignals([]byte(`{answer: '...', prize: '...'}`))
```

```java
generator.send(PatchElements.builder()
    .data("<div id=\"question\">...</div>")
    .build()
);
generator.send(PatchElements.builder()
    .data("<div id=\"instructions\">...</div>")
    .build()
);
generator.send(PatchSignals.builder()
    .data("{\"answer\": \"...\", \"prize\": \"...\"}")
    .build()
);
```

```kotlin
generator.patchElements(
    elements = """<div id="question">...</div>""",
)
generator.patchElements(
    elements = """<div id="instructions">...</div>""",
)
generator.patchSignals(
    signals = """{"answer": "...", "prize": "..."}""",
)
```

```php
$sse->patchElements('<div id="question">...</div>');
$sse->patchElements('<div id="instructions">...</div>');
$sse->patchSignals(['answer' => '...', 'prize' => '...']);
```

```python
return DatastarResponse([
    SSE.patch_elements('<div id="question">...</div>'),
    SSE.patch_elements('<div id="instructions">...</div>'),
    SSE.patch_signals({"answer": "...", "prize": "..."})
])
```

```ruby
datastar.stream do |sse|
  sse.patch_elements('<div id="question">...</div>')
  sse.patch_elements('<div id="instructions">...</div>')
  sse.patch_signals(answer: '...', prize: '...')
end
```

```rust
yield PatchElements::new("<div id='question'>...</div>").into()
yield PatchElements::new("<div id='instructions'>...</div>").into()
yield PatchSignals::new("{answer: '...', prize: '...'}").into()
```

```javascript
stream.patchElements('<div id="question">...</div>');
stream.patchElements('<div id="instructions">...</div>');
stream.patchSignals({'answer': '...', 'prize': '...'});
```

--------------------------------

### Import and use a custom web component

Source: https://data-star.dev/docs.md

Import the 'rocket' function from the Data-star Pro bundle and define a custom element. Then, use the defined custom element in your HTML.

```javascript
import { rocket } from '/bundles/datastar-pro.js'
// define demo-counter here
```

```html
<demo-counter count="5" label="Inventory"></demo-counter>
```

--------------------------------

### Import Datastar with Package Manager

Source: https://data-star.dev/guide/getting_started

Import Datastar directly in your project using a package manager like npm, Deno, or Bun. TypeScript users may need to add a comment to ignore type errors.

```javascript
// @ts-expect-error (only required for TypeScript projects)
import 'https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0/bundles/datastar.js'
```

--------------------------------

### Sequential DOM Patching with SSE

Source: https://data-star.dev/docs.md

Demonstrates sending multiple `datastar-patch-elements` SSE events in a stream to update the DOM sequentially. This allows for dynamic content changes over time.

```text
event: datastar-patch-elements
data: elements <div id="hal">
data: elements     I’m sorry, Dave. I’m afraid I can’t do that.
data: elements </div>

event: datastar-patch-elements
data: elements <div id="hal">
data: elements     Waiting for an order...
data: elements </div>


```

--------------------------------

### Implement Click-to-Load Button

Source: https://data-star.dev/examples/click_to_load

Use this HTML button to trigger the loading of the next page of data. It includes attributes for managing loading states and handling click events.

```html
<button
    class="info wide"
    data-indicator:_fetching
    data-attr:aria-disabled="`${$_fetching}`"
    data-on:click="!$_fetching && @get('/examples/click_to_load/more')"
>
    Load More
</button>
```

--------------------------------

### Configure SSE connection persistence

Source: https://data-star.dev/how_tos/prevent_sse_connections_closing

Set the openWhenHidden option to true to prevent the SSE connection from closing when the page is hidden.

```html
<button data-on:click="@get('/endpoint', {openWhenHidden: true})"></button>
```

--------------------------------

### Initial Lazy Load State

Source: https://data-star.dev/examples/lazy_load

Define the initial container with a data-init attribute to specify the source for the lazy-loaded content.

```html
<div id="graph" data-init="@get('/examples/lazy_load/graph')">
    Loading...
</div>
```

--------------------------------

### C# SDK for SSE Patching

Source: https://data-star.dev/docs.md

This C# code snippet shows how to use the Datastar SDK to patch elements into the DOM asynchronously. It sends an initial response, waits, and then sends an updated response.

```csharp
using StarFederation.Datastar.DependencyInjection;

// Adds Datastar as a service
builder.Services.AddDatastar();

app.MapGet("/", async (IDatastarService datastarService) =>
{
    // Patches elements into the DOM.
    await datastarService.PatchElementsAsync(@"<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>");

    await Task.Delay(TimeSpan.FromSeconds(1));

    await datastarService.PatchElementsAsync(@"<div id=\"hal\">Waiting for an order...</div>");
});
```

--------------------------------

### Listen for Any Keydown Event Globally

Source: https://data-star.dev/how_tos/bind_keydown_events_to_specific_keys

Use `data-on:keydown__window` to capture any keydown event on the window. This will trigger an alert for every key press.

```html
<div data-on:keydown__window="alert('Key pressed')"></div>
```

--------------------------------

### Basic Repeated Button Click Action

Source: https://data-star.dev/how_tos/keep_datastar_code_dry

Demonstrates a common scenario where the same backend action is repeated for multiple buttons. This approach leads to code duplication.

```html
<button data-on:click="@get('/endpoint')">Click me</button>
<button data-on:click="@get('/endpoint')">No, click me!</button>
<button data-on:click="@get('/endpoint')">Click us all!</button>
```

--------------------------------

### Initialize Graph State and Refs

Source: https://data-star.dev/examples/rocket_flow

Defines the core state variables and a helper to validate SVG element references.

```javascript
let gridPath
let graph
let frame = 0
let graphFrame = 0
let edgeFrameId = 0
let edgeFramePending = false
let lastSignature = ''
let selectedEdgeKey = null
let lastServerUpdateTime = Number.NaN
let viewport = normalizeViewport(props.viewport)
let grid = props.grid

const metrics = {
  screenWidth: 1,
  screenHeight: 1,
  worldWidth: 1,
  worldHeight: 1,
  zoom: 1,
  minX: 0,
  minY: 0,
}
const nodes = new Map()
const nodesById = new Map()
const edges = new Map()
const edgesByKey = new Map()
const activeNodeDrags = new Map()
const edgeSelectionBoundGroups = new WeakSet()
const dragEnabledGroups = new WeakSet()

const ensureRefs = () => {
  svg = refs.svg ?? null
  background = refs.background ?? null
  gridPattern = refs.gridPattern ?? null
  gridPath = refs.gridPath ?? null
  graph = refs.graph ?? null
  return (
    svg instanceof SVGSVGElement &&
    background instanceof SVGRectElement &&
    gridPattern instanceof SVGPatternElement &&
    gridPath instanceof SVGPathElement &&
    graph instanceof SVGGElement
  )
}
```

--------------------------------

### POST /api/rocket/manifests

Source: https://data-star.dev/docs.md

Publishes the full component manifest document as JSON to a registry service or documentation build system.

```APIDOC
## POST /api/rocket/manifests

### Description
Publishes the full manifest document containing component metadata, including inferred props, slots, and events.

### Method
POST

### Endpoint
/api/rocket/manifests

### Request Body
- **version** (string) - The version of the manifest document.
- **generatedAt** (string) - Timestamp of when the manifest was generated.
- **components** (array) - List of component entries containing tag name, props, slots, and events.

### Request Example
{
  "version": "1.0.0",
  "generatedAt": "2023-10-27T10:00:00Z",
  "components": [
    {
      "tag": "demo-dialog",
      "props": { ... },
      "slots": [{ "name": "default", "description": "Dialog body content." }],
      "events": [{ "name": "close", "kind": "custom-event" }]
    }
  ]
}
```

--------------------------------

### Define Host Properties and Methods

Source: https://data-star.dev/docs.md

Use `defineHostProp` to expose read-only properties like 'version' or imperative methods like 'reset' on the host element. This is for members that are not standard Rocket props.

```typescript
rocket('demo-host-methods', {
  setup({ defineHostProp }) {
    defineHostProp('version', {
      get() {
        return '1'
      },
    })
    defineHostProp('reset', {
      value() {
        console.log('reset')
      },
    })
  },
})
```

--------------------------------

### Codec Tables Overview

Source: https://data-star.dev/docs.md

Overview of the codec types provided in the 'props' registry.

```APIDOC
## Codec Tables

Rocket ships these codecs in the `props` registry.

| Codec | Decoded type | Typical input | Typical uses |
|---|---|---|---|
| `string` | `string` | `" hello "` | Text props, labels, ids, classes, case-normalized names. |
| `number` | `number` | `"42"` | Ranges, dimensions, timing, scores, percentages. |
| `bool` | `boolean` | `""`, `"true"`, `"1"` | Feature flags and toggles. |
| `date` | `Date` | `"2026-03-18T12:00:00.000Z"` | Timestamps and schedule props. |
| `json` | `any` | `'{"items":[1,2,3]}'` | Structured JSON payloads. |
| `js` | `any` | `"{ foo: 1, bar: [2, 3] }"` | JS-like object literals when strict JSON is inconvenient. |
| `bin` | `Uint8Array` | text-like binary payload | Binary or byte-oriented props. |
| `array(codec)` | `T[]` | `'["a","b"]'` | Lists of values with per-item normalization. |
| `array(codecA, codecB, ...)` | Tuple | `'["en",10,true]'` | Fixed-length ordered values. |
| `object(shape)` | Typed object | `'{"x":10,"y":20}'` | Named structured props. |
| `oneOf(...)` | Union | `"primary"` | Enums and constrained variants. |
```

--------------------------------

### Ruby: Stream Redirect with Server-Sent Events

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Implement a server-sent event stream to patch elements and redirect using the Datastar SDK.

```ruby
datastar = Datastar.new(request:, response:)

datastar.stream do |sse|
  sse.patch_elements '<div id="indicator">Redirecting in 3 seconds...</div>'

  sleep 3

  sse.redirect '/guide'
end
```

--------------------------------

### Practical Use Case: Nested Menu State Management

Source: https://data-star.dev/guide/backend_requests

Manage the open/closed state of multiple menus and implement a 'toggle all' functionality using nested signals and an action.

```html
1<div data-signals="{menu: {isOpen: {desktop: false, mobile: false}}}">
2    <button data-on:click="@toggleAll({include: /^menu\.isOpen\./})">
3        Open/close menu
4    </button>
5</div>
```

--------------------------------

### Rocket Component Implementation

Source: https://data-star.dev/examples/rocket_openfreemap

Initializes a MapLibre GL map instance with support for markers, clustering, and custom styling.

```javascript
  1import { rocket } from 'datastar'
  2
  3const { default: maplibregl } = await import(
  4  'https://cdn.jsdelivr.net/npm/maplibre-gl@5.18.0/+esm'
  5)
  6
  7const markerEntriesToGeoJSON = (entries) => ({
  8  type: 'FeatureCollection',
  9  features: entries.map((entry, id) => ({
 10    type: 'Feature',
 11    properties: { id, label: entry.label, icon: entry.icon },
 12    geometry: { type: 'Point', coordinates: entry.coords },
 13  })),
 14})
 15
 16rocket('openfreemap-map', {
 17  props: ({ string, json, number, bool }) => ({
 18    styleUrl: string.default('https://tiles.openfreemap.org/styles/liberty'),
 19    center: json.default([-115.172816, 36.114647]),
 20    zoom: number.clamp(0, 22).default(9.5),
 21    bearing: number,
 22    pitch: number.clamp(0, 85),
 23    dragRotate: bool,
 24    cluster: bool,
 25    clusterMaxZoom: number.clamp(0, 22).default(12),
 26    clusterRadius: number.clamp(10, 100).default(50),
 27    markers: json.default([]),
 28  }),
 29  onFirstRender({ refs, cleanup, host, observeProps, props }) {
 30    let map
 31    let markers = []
 32    let markerEntries = []
 33    let prevMarkers = ''
 34    let prevStyleURL = props.styleUrl
 35    let prevView = JSON.stringify({
 36      center: props.center,
 37      zoom: props.zoom,
 38      bearing: props.bearing,
 39      pitch: props.pitch,
 40    })
 41    let prevDragRotate = props.dragRotate
 42    let prevClusterSignal = JSON.stringify([
 43      props.cluster,
 44      Math.round(props.clusterMaxZoom),
 45      Math.round(props.clusterRadius),
 46    ])
 47    let prevAppliedClusterConfig = ''
 48
 49    const clusterSourceID = 'rocket-openfreemap-markers-cluster'
 50    const clusterLayerID = 'rocket-openfreemap-markers-clusters'
 51    const clusterCountLayerID = 'rocket-openfreemap-markers-cluster-count'
 52    const unclusteredLayerID = 'rocket-openfreemap-markers-unclustered'
 53
 54    const readMarkerEntries = () =>
 55      Array.isArray(props.markers)
 56        ? props.markers
 57            .map((m) => {
 58              const hasNestedCoords = Array.isArray(m?.[0])
 59              const coords = hasNestedCoords ? m[0] : [m?.[0], m?.[1]]
 60              const label = hasNestedCoords ? m?.[1] : m?.[2]
 61              const icon = hasNestedCoords ? m?.[2] : m?.[3]
 62              const [lng, lat] = coords.map(Number)
 63              if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null
 64              return {
 65                coords: [lng, lat],
 66                label: typeof label === 'string' ? label : '',
 67                icon: (typeof icon === 'string' && icon) || 'mdi:map-marker',
 68              }
 69            })
 70            .filter((m) => m != null)
 71        : []
 72
 73    const removeClusterLayersAndSource = () => {
 74      if (!map) return
 75      if (map.getLayer(clusterCountLayerID))
 76        map.removeLayer(clusterCountLayerID)
 77      if (map.getLayer(clusterLayerID)) map.removeLayer(clusterLayerID)
 78      if (map.getLayer(unclusteredLayerID)) map.removeLayer(unclusteredLayerID)
 79      if (map.getSource(clusterSourceID)) map.removeSource(clusterSourceID)
 80    }
 81
 82    const removeDomMarkers = () => {
 83      for (const marker of markers) marker.remove()
 84      markers = []
 85    }
 86
 87    const renderDomMarkers = () => {
 88      if (!map) return
 89      removeDomMarkers()
 90      markers = markerEntries.map((entry) => {
 91        const markerEl = document.createElement('div')
 92        markerEl.className = 'rocket-openfreemap-marker'
 93
 94        const iconEl = document.createElement('span')
 95        iconEl.className = 'rocket-openfreemap-marker-icon'
 96        if (entry.icon.includes(':')) {
 97          const iconifyEl = document.createElement('iconify-icon')
 98          iconifyEl.setAttribute('icon', entry.icon)
 99          iconifyEl.setAttribute('noobserver', '')
100          iconifyEl.setAttribute('aria-hidden', 'true')
101          iconEl.append(iconifyEl)
102        } else {
103          iconEl.textContent = entry.icon
104        }
105
106        markerEl.append(iconEl)
107        if (entry.label) {
108          const labelEl = document.createElement('span')
109          labelEl.className = 'rocket-openfreemap-marker-label'
110          labelEl.textContent = entry.label
111          markerEl.append(labelEl)
112        }
113
114        return new maplibregl.Marker({ element: markerEl, anchor: 'bottom' })
115          .setLngLat(entry.coords)
116          .addTo(map)
117      })
118    }
119
120    const ensure3DBuildings = () => {
121      if (!map || !props.dragRotate) return
122      const layers = map.getStyle()?.layers ?? []
123      if (layers.some((layer) => layer.type === 'fill-extrusion')) return
124      const buildingLayer = layers.find(
125        (layer) =>
126          layer.type === 'fill' &&
127          layer.source &&
128          layer['source-layer'] === 'building',
```

--------------------------------

### Redirect with Delay using SSE in PHP

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

This PHP snippet shows how to send HTML to the client, pause for 3 seconds, and then execute a JavaScript redirect. It utilizes the ServerSentEventGenerator class.

```php
use starfederation\datastar\ServerSentEventGenerator;

$sse = new ServerSentEventGenerator();
$sse->patchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`);
sleep(3);
$sse->executeScript(`
    setTimeout(() => window.location = "/guide")
`);

```

--------------------------------

### Correct usage of Datastar action with URL

Source: https://data-star.dev/errors/fetch_no_url_provided

Provide a valid URL as the first argument to the action to resolve the FetchNoUrlProvided error.

```html
<button data-on:click="@post('/endpoint')"></button>
```

--------------------------------

### PHP Backend for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

PHP implementation for sending SSE patch elements using DataStar. It formats the current time and patches the `#time` div.

```php
use starfederation\datastar\ServerSentEventGenerator;

$currentTime = date('Y-m-d H:i:s');

$sse = new ServerSentEventGenerator();
$sse->patchElements(`
    <div id="time"
         data-on-interval__duration.5s="@get('/endpoint')"
    >
        $currentTime
    </div>
`);

```

--------------------------------

### Initialize Rocket Virtual Scroll Component

Source: https://data-star.dev/examples/rocket_virtual_scroll

Configures the virtual scroll component with properties for data fetching and rendering. Requires 'datastar' import and a component ID. Ensure 'url' prop is provided for data loading.

```javascript
import { rocket } from 'datastar'

rocket('virtual-scroll', {
  mode: 'light',
  props: ({ string, number }) => ({
    url: string,
    initialIndex: number.min(0).default(20),
    bufferSize: number.min(1).default(50),
    totalItems: number.min(1).default(100000),
  }),
  onFirstRender({ cleanup, host, observeProps, props, refs }) {
    /** @type {HTMLElement | null} */
    let viewport
    /** @type {HTMLElement | null} */
    let spacer
    /** @type {{ A: HTMLElement | null, B: HTMLElement | null, C: HTMLElement | null }} */
    let blocks = { A: null, B: null, C: null }
    let blockAStartIndex = 0
    let blockBStartIndex = 0
    let blockCStartIndex = 0
    let blockAY = 0
    let blockBY = 0
    let blockCY = 0
    let avgItemHeight = 50
    let scrollHeight = 0
    let isLoading = false
    let blockPositions = ['A', 'B', 'C']
    let measuredItems = 0
    let totalMeasuredHeight = 0
    let jumpTimeout = 0
    let hasInitializedScroll = false
    let lastProcessedScroll = 0
    let scrollTimeout = 0
    let observer
    const lastBlockContent = { A: '', B: '', C: '' }
    const setHeights = () => {
      scrollHeight = props.totalItems * avgItemHeight
      if (spacer) spacer.style.height = `${scrollHeight}px`
    }

    const startIndexOf = (name) =>
      name === 'A'
        ? blockAStartIndex
        : name === 'B'
          ? blockBStartIndex
          : blockCStartIndex

    const setStartIndex = (name, value) => {
      if (name === 'A') blockAStartIndex = value
      else if (name === 'B') blockBStartIndex = value
      else blockCStartIndex = value
    }

    const setY = (name, value) => {
      if (name === 'A') blockAY = value
      else if (name === 'B') blockBY = value
      else blockCY = value
      blocks[name]?.style.setProperty('transform', `translateY(${value}px)`)
    }

    const clearJumpTimeout = () => {
      if (!jumpTimeout) return
      clearTimeout(jumpTimeout)
      jumpTimeout = 0
    }

    const loadBlock = async (startIndex, blockId) => {
      if (!host.id) {
        throw new Error(
          '[IonVirtualScroll] Component element must have an id attribute',
        )
      }
      if (!props.url) {
        throw new Error('[IonVirtualScroll] url prop is required')
      }
      const response = await fetch(props.url, {
        method: 'POST',
        headers: {
          Accept: 'text/event-stream, text/html, application/json',
          'Content-Type': 'application/json',
          'Datastar-Request': 'true',
        },
        body: JSON.stringify({
          startIndex,
          count: props.bufferSize,
          blockId: blockId === 'all' ? host.id : `${host.id}-${blockId}`,
          componentId: host.id,
          instanceNum:
            host.getAttribute('rocket-instance-id') ??
            /** @type {HTMLElement & { rocketInstanceId?: string }} */ (host)
              .rocketInstanceId ??
            '',
        }),
      })
      if (!response.body) return
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      const flush = (chunk) => {
        let event = 'message'
        const data = []
        for (const line of chunk.split('\n')) {
          if (line.startsWith('event:')) event = line.slice(6).trim()
          else if (line.startsWith('data:'))
            data.push(line.slice(5).trimStart())
        }
        if (!event.startsWith('datastar')) return
        const argsRawLines = {}
        for (const line of data.join('\n').split('\n')) {
          const i = line.indexOf(' ')
          if (i < 0) continue
          const key = line.slice(0, i)
          const value = line.slice(i + 1)
          ;(argsRawLines[key] ??= []).push(value)
        }
        document.dispatchEvent(
          new CustomEvent('datastar-fetch', {
            detail: {
              type: event,
              el: host,
              argsRaw: Object.fromEntries(
                Object.entries(argsRawLines).map(([key, values]) => [
                  key,
                  values.join('\n'),
                ]),
              ),
            },
          }),
        )
      }

      while (true) {
        const { done, value } = await reader.read()
        buffer += decoder.decode(value ?? new Uint8Array(), {
          stream: !done,
        })
        let boundary = buffer.indexOf('\n\n')
        while (boundary >= 0) {
          flush(buffer.slice(0, boundary))
          buffer = buffer.slice(boundary + 2)
          boundary = buffer.indexOf('\n\n')
        }
      }
    }
  }
})
```

--------------------------------

### Dynamic Polling Frequency in Go

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses the Datastar Go library to calculate duration and patch elements via SSE.

```go
 1import (
 2    "time"
 3    "github.com/starfederation/datastar-go/datastar"
 4)
 5
 6currentTime := time.Now().Format("2006-01-02 15:04:05")
 7currentSeconds := time.Now().Format("05")
 8duration := 1
 9if currentSeconds < "50" {
10    duration = 5
11}
12
13sse := datastar.NewSSE(w, r)
14sse.PatchElements(fmt.Sprintf(`
15    <div id="time" data-on-interval__duration.%ds="@get('/endpoint')">
16        %s
17    </div>
18`, duration, currentTime))
```

--------------------------------

### Go SDK for SSE Patching

Source: https://data-star.dev/docs.md

This Go code utilizes the Datastar SDK to generate Server-Sent Events for patching DOM elements. It sends an initial HTML snippet, pauses, and then sends an updated one.

```go
import (
    "github.com/starfederation/datastar-go/datastar"
    time
)

// Creates a new `ServerSentEventGenerator` instance.
sse := datastar.NewSSE(w,r)

// Patches elements into the DOM.
sse.PatchElements(
    `<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>`
)

time.Sleep(1 * time.Second)

sse.PatchElements(
    `<div id="hal">Waiting for an order...</div>`
)
```

--------------------------------

### Stream SSE events in Go

Source: https://data-star.dev/guide/backend_requests

Initializes a ServerSentEventGenerator to stream DOM and signal updates.

```go
 1import ("github.com/starfederation/datastar-go/datastar")
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4sse := datastar.NewSSE(w,r)
 5
 6// Patches elements into the DOM.
 7sse.PatchElements(
 8    `<div id="question">What do you put in a toaster?</div>`
 9)
10
11// Patches signals.
12sse.PatchSignals([]byte(`{response: '', answer: 'bread'}`))
```

--------------------------------

### Rust SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Implements SSE for patching elements and executing a script using `datastar-rs` and `tokio`.

```rust
use datastar::prelude::*;
use async_stream::stream;
use core::time::Duration;

Sse(stream! {
    yield PatchElements::new("<div id='indicator'>Redirecting in 3 seconds...</div>").into();
    tokio::time::sleep(core::time::Duration::from_secs(3)).await;
    yield ExecuteScript::new("window.location = '/guide'").into();
});
```

--------------------------------

### Implement CQRS pattern for state updates

Source: https://data-star.dev/how_tos/prevent_sse_connections_closing

Use a fat morph approach to send the complete state of the content area, ensuring resilience against connection interruptions.

```html
<div data-init="@get('/cqrs_endpoint')"></div>
<div id="main">
    ...
</div>
```

--------------------------------

### String Codec Transformations

Source: https://data-star.dev/reference/rocket

Shows how to chain string manipulation methods like `trim`, `lower`, `kebab`, `suffix`, and `default` to create a robust string prop. This is useful for normalizing user input for attributes like slugs or CSS sizes.

```javascript
props: ({ string }) => ({
  slug: string.trim.lower.kebab.maxLength(48),
  cssSize: string.trim.suffix('px').default('16px'),
  title: string.trim.title.default('Untitled'),
})
```

--------------------------------

### HTML Structure for Two-Way Binding

Source: https://data-star.dev/examples/web_component

This HTML sets up input binding and displays the output from a custom web component. Use this to bind input values and listen for events from custom elements.

```html
<label>
    Reversed
    <input type="text" value="Your Name" data-bind:_name/>
</label>
<span data-signals:_reversed data-text="$_reversed"></span>
<reverse-component
    data-on:reverse="$_reversed = evt.detail.value"
    data-attr:name="$_name">
</reverse-component>
```

--------------------------------

### Sync signals with query string parameters using data-query-string

Source: https://data-star.dev/docs.md

Synchronizes signal values with URL query parameters, supporting filtering and browser history management.

```html
<div data-query-string></div>
```

```html
<div data-query-string="{include: /foo/, exclude: /bar/}"></div>
```

```html
<div data-query-string__filter__history></div>
```

--------------------------------

### Patch Signals via Go SDK

Source: https://data-star.dev/guide/reactive_signals

Using the Go Datastar SDK to send signal patches over an SSE connection.

```go
 1import (
 2    "github.com/starfederation/datastar-go/datastar"
 3)
 4
 5// Creates a new `ServerSentEventGenerator` instance.
 6sse := datastar.NewSSE(w, r)
 7
 8// Patches signals
 9sse.PatchSignals([]byte(`{hal: 'Affirmative, Dave. I read you.'}`))
10
11time.Sleep(1 * time.Second)
12
13sse.PatchSignals([]byte(`{hal: '...'}`))
```

--------------------------------

### Clojure SSE Response with Patch Signals

Source: https://data-star.dev/docs.md

Generates an SSE response in Clojure that patches signals, waits for a second, and then patches them again. Requires Data-Star SDK and an HTTP-Kit adapter.

```clojure
;; Import the SDK's api and your adapter
(require
  '[starfederation.datastar.clojure.api :as d*]
  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])

;; in a ring handler
(defn handler [request]
  ;; Create an SSE response
  (->sse-response request
                  {on-open
                   (fn [sse]
                     ;; Patches signal.
                     (d*/patch-signals! sse "{hal: 'Affirmative, Dave. I read you.'}")
                     (Thread/sleep 1000)
                     (d*/patch-signals! sse "{hal: '...'}"))})
```

--------------------------------

### Implement Rocket Conditional Panel

Source: https://data-star.dev/examples/rocket_conditional

Uses Datastar signals to drive component props for conditional rendering.

```html
<div data-signals='{"step":0,"showDetails":false}'>
    <conditional-panel
        data-attr:step="$step"
        data-attr:show-details="$showDetails"
    ></conditional-panel>
</div>
```

--------------------------------

### Usage of my-counter component

Source: https://data-star.dev/examples/rocket_counter

Instantiate the counter component with a specific count prop.

```html
<my-counter count="7"></my-counter>
<my-counter count="11"></my-counter>
```

--------------------------------

### Display Counter Changes

Source: https://data-star.dev/examples/on_signal_patch

Initial state for tracking counter changes.

```json
{"counterChanges":[]}
```

--------------------------------

### Pro Action: @clipboard()

Source: https://data-star.dev/reference/actions

The `@clipboard()` Pro action allows you to easily copy text to the user's clipboard, with support for Base64 encoded content.

```APIDOC
## Pro Action: `@clipboard()`

### Description
Copies the provided text to the clipboard. The optional second parameter, when set to `true`, indicates that the text is Base64 encoded and should be decoded before copying. This is useful for handling special characters or complex data.

### Syntax
`@clipboard(text: string, isBase64?: boolean)`

### Examples
```html
<!-- Copy plain text -->
<button data-on:click="@clipboard('Hello, world!')"></button>

<!-- Copy base64 encoded text (will decode before copying) -->
<button data-on:click="@clipboard('SGVsbG8sIHdvcmxkIQ==', true)"></button>
```
```

--------------------------------

### Binary Prop API

Source: https://data-star.dev/reference/rocket

The bin codec decodes base64 string input into Uint8Array.

```APIDOC
## bin

### Description
Decodes base64 string input into Uint8Array and encodes bytes back into base64.

### Members
- **default(value)**: Supplies fallback bytes.
```

--------------------------------

### Delay Initialization with data-init__delay

Source: https://data-star.dev/reference/attributes

Add a delay to the `data-init` expression using the `__delay` modifier. This allows for deferred initialization, specified in milliseconds or seconds.

```html
<div data-init__delay.500ms="$count = 1"></div>
```

--------------------------------

### Implement QR Code Component in HTML

Source: https://data-star.dev/examples/rocket_qr_code

Use the qr-code custom element with data-signals to bind configuration properties like text, size, and colors.

```html
<div data-signals='{"qrText":"Hello World","qrSize":200,"qrColorDark":"#000000","qrColorLight":"#ffffff","qrErrorLevel":"L"}'>
    <qr-code
        data-attr:text="$qrText"
        data-attr:size="$qrSize"
        data-attr:error-level="$qrErrorLevel"
        data-attr:color-dark="$qrColorDark"
        data-attr:color-light="$qrColorLight"
    ></qr-code>
</div>
```

--------------------------------

### data-match-media

Source: https://data-star.dev/reference

Sets a signal based on whether a media query matches, keeping it in sync with changes.

```APIDOC
## data-match-media

### Description
Sets a signal to whether a media query matches and keeps it in sync whenever the query changes.

### Usage
`<div data-match-media:is-dark="'prefers-color-scheme: dark'"></div>`

### Notes
The query value can be written as `prefers-color-scheme: dark` or `(prefers-color-scheme: dark)`. For complex queries, use explicit media-query syntax.
```

--------------------------------

### Conditional Rendering with Datastar Expressions

Source: https://data-star.dev/docs.md

Conditionally displays 'Ready' or 'Waiting' based on the truthiness of the '$landingGearRetracted' signal using the ternary operator. Also shows using logical OR for visibility and logical AND for triggering actions.

```html
// Output one of two values, depending on the truthiness of a signal
<div data-text="$landingGearRetracted ? 'Ready' : 'Waiting'"></div>

// Show a countdown if the signal is truthy or the time remaining is less than 10 seconds
<div data-show="$landingGearRetracted || $timeRemaining < 10">
    Countdown
</div>

// Only send a request if the signal is truthy
<button data-on:click="$landingGearRetracted && @post('/launch')">
    Launch
</button>
```

--------------------------------

### HTML Structure for Signals

Source: https://data-star.dev/docs.md

This HTML snippet shows how to bind frontend signals to elements and trigger backend actions on user interaction.

```html
<div data-signals:hal="'...'" >
    <button data-on:click="@get('/endpoint')">
        HAL, do you read me?
    </button>
    <div data-text="$hal"></div>
</div>
```

--------------------------------

### Sequential SSE Patch Signals

Source: https://data-star.dev/docs.md

Demonstrates sending multiple SSE 'datastar-patch-signals' events in a stream to update a signal, pause, and then update it again.

```sse
event: datastar-patch-signals
data: signals {hal: 'Affirmative, Dave. I read you.'}

// Wait 1 second

event: datastar-patch-signals
data: signals {hal: '...'}


```

--------------------------------

### data-bind for Custom Elements with __prop and __event

Source: https://data-star.dev/reference

Bind to a custom element's state using `__prop` for the property and `__event` for syncing changes. Defaults to `value` and `change` for generic custom elements.

```html
<my-toggle data-bind:is-checked__prop.checked__event.change></my-toggle>
```

--------------------------------

### Read signals in Python

Source: https://data-star.dev/docs.md

Uses the FastAPI helper to read signals as a dictionary from the request.

```python
from datastar_py.fastapi import datastar_response, read_signals

@app.get("/updates")
@datastar_response
async def updates(request: Request):
    # Retrieve a dictionary with the current state of the signals from the frontend
    signals = await read_signals(request)
```

--------------------------------

### Clojure SSE Redirect Implementation

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Uses `datastar.clojure.api` to send SSE events for patching elements and executing a redirect script.

```clojure
(require
  '[starfederation.datastar.clojure.api :as d*]
  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]
  '[some.hiccup.library :refer [html]])


(defn handle [ring-request]
  (->sse-response ring-request
    {on-open
      (fn [sse]
        (d*/patch-elements! sse
          (html [:div#indicator "Redirecting in 3 seconds..."]))
        (Thread/sleep 3000)
        (d*/execute-script! sse "window.location = \"/guide\"")
        (d*/close-sse! sse)}))
```

--------------------------------

### Implement two-way data binding with data-bind

Source: https://data-star.dev/reference/attributes

Use data-bind to synchronize input elements with signals. It supports various input types and automatic type preservation.

```html
<input data-bind:foo />
```

```html
<input data-bind="foo" />
```

```html
<!-- Both of these create the signal `$fooBar` -->
<input data-bind:foo-bar />
<input data-bind="fooBar" />
```

```html
<input data-bind:foo-bar value="baz" />
```

```html
<div data-signals:foo-bar="'fizz'">
    <input data-bind:foo-bar value="baz" />
</div>
```

```html
<div data-signals:foo-bar="0">
    <select data-bind:foo-bar>
        <option value="10">10</option>
    </select>
</div>
```

```html
<div data-signals:foo-bar="[]">
    <input data-bind:foo-bar type="checkbox" value="fizz" />
    <input data-bind:foo-bar type="checkbox" value="baz" />
</div>
```

```html
<input type="file" data-bind:files multiple />
```

--------------------------------

### Implement Bulk Update Table

Source: https://data-star.dev/examples/bulk_update

Uses data-signals to manage checkbox selections and trigger bulk PUT requests to server endpoints.

```html
 1<div
 2    id="demo"
 3    data-signals__ifmissing="{_fetching: false, selections: Array(4).fill(false)}"
 4>
 5    <table>
 6        <thead>
 7            <tr>
 8                <th>
 9                    <input
10                        type="checkbox"
11                        data-bind:_all
12                        data-on:change="$selections = Array(4).fill($_all)"
13                        data-effect="$selections; $_all = $selections.every(Boolean)"
14                        data-attr:disabled="$_fetching"
15                    />
16                </th>
17                <th>Name</th>
18                <th>Email</th>
19                <th>Status</th>
20            </tr>
21        </thead>
22        <tbody>
23            <tr>
24                <td>
25                    <input
26                        type="checkbox"
27                        data-bind:selections
28                        data-attr:disabled="$_fetching"
29                    />
30                </td>
31                <td>Joe Smith</td>
32                <td>joe@smith.org</td>
33                <td>Active</td>
34            </tr>
35            <!-- More rows... -->
36        </tbody>
37    </table>
38    <div role="group">
39        <button
40            class="success"
41            data-on:click="@put('/examples/bulk_update/activate')"
42            data-indicator:_fetching
43            data-attr:disabled="$_fetching"
44        >
45            <i class="pixelarticons:user-plus"></i>
46            Activate
47        </button>
48        <button
49            class="error"
50            data-on:click="@put('/examples/bulk_update/deactivate')"
51            data-indicator:_fetching
52            data-attr:disabled="$_fetching"
53        >
54            <i class="pixelarticons:user-x"></i>
55            Deactivate
56        </button>
57    </div>
58</div>
```

--------------------------------

### Patch Signals via Clojure SDK

Source: https://data-star.dev/guide/reactive_signals

Implementation of signal patching using the Clojure Datastar SDK within a Ring handler.

```clojure
 1;; Import the SDK's api and your adapter
 2(require
 3  '[starfederation.datastar.clojure.api :as d*]
 4  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
 5
 6;; in a ring handler
 7(defn handler [request]
 8  ;; Create an SSE response
 9  (->sse-response request
10                  {on-open
11                   (fn [sse]
12                     ;; Patches signal.
13                     (d*/patch-signals! sse "{hal: 'Affirmative, Dave. I read you.'}")
14                     (Thread/sleep 1000)
15                     (d*/patch-signals! sse "{hal: '...'}"))}))
```

--------------------------------

### Go: Server-Side Handler for Loading More Data

Source: https://data-star.dev/how_tos/load_more_list_items

Handles requests to load more data using Datastar in Go. It reads offset signals, patches elements with new items, and updates signals or removes the load more button.

```go
1import (
2    "fmt"
3    "net/http"
4
5    "github.com/go-chi/chi/v5"
6    "github.com/starfederation/datastar-go/datastar"
7)
8
9type OffsetSignals struct {
10    Offset int `json:"offset"`
11}
12
13signals := &OffsetSignals{}
14if err := datastar.ReadSignals(r, signals); err != nil {
15    http.Error(w, err.Error(), http.StatusBadRequest)
16}
17
18max := 5
19limit := 1
20offset := signals.Offset
21
22sse := datastar.NewSSE(w, r)
23
24if offset < max {
25    newOffset := offset + limit
26    sse.PatchElements(fmt.Sprintf(`<div>Item %d</div>`, newOffset),
27        datastar.WithSelectorID("list"),
28        datastar.WithModeAppend(),
29    )
30    if newOffset < max {
31        sse.PatchSignals([]byte(fmt.Sprintf(`{offset: %d}`, newOffset)))
32    } else {
33        sse.RemoveElements(`#load-more`)
34    }
35}

```

--------------------------------

### Render All Nodes

Source: https://data-star.dev/examples/rocket_flow

Iterates through all nodes, ensures their groups are created, and positions them. Schedules edge rendering afterwards. Only runs if there are nodes to render.

```javascript
    const renderNodes = () => {
      if (!nodes.size) return
      for (const entry of nodes.values()) {
        ensureNodeGroup(entry)
        positionNode(entry)
      }
      scheduleEdgeRender()
    }
```

--------------------------------

### Define Rocket Component with Props and Render Function

Source: https://data-star.dev/reference/rocket

Use this pattern to define a Rocket component, specifying props with codecs for data transformation and a render function for UI output. Defaults are applied if attributes are not provided.

```javascript
1rocket('demo-badge', {
  props: ({ string, bool, number }) => ({
    label: string.trim.default('New'),
    tone: string.lower.default('neutral'),
    visible: bool.default(true),
    priority: number.clamp(0, 5),
  }),
  render({ html, props: { label, tone, visible, priority } }) {
    return html`
      <span
        data-show="${visible}"
        data-attr:data-tone="${tone}"
        data-text="${label + ' #' + priority}">
      </span>
    `
  },
})

const badge = document.querySelector('demo-badge')

// Property write:
badge.priority = 7

// Reflected attribute after encoding:
// <demo-badge priority="5"></demo-badge>

// Attribute write:
badge.setAttribute('label', '  shipped  ')

// Decoded prop value in setup/render:
// props.label === 'shipped'
```

--------------------------------

### Read signals in Go

Source: https://data-star.dev/docs.md

Uses the datastar-go package to read signals from an HTTP request into a struct.

```go
import ("github.com/starfederation/datastar-go/datastar")

type Signals struct {
    Foo struct {
        Bar string `json:"bar"`
    } `json:"foo"`
}

signals := &Signals{}
if err := datastar.ReadSignals(request, signals); err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
}
```

--------------------------------

### PHP: Redirect with Server-Sent Events

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Use ServerSentEventGenerator to patch HTML and initiate a redirect after a delay.

```php
$sse = new ServerSentEventGenerator();
$sse->patchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`);
sleep(3);
$sse->location('/guide');
```

--------------------------------

### Clojure: Patch Elements and Signals via SSE

Source: https://data-star.dev/docs.md

Use this snippet in a Clojure controller action to create an SSE response. It demonstrates patching elements and signals into the DOM.

```clojure
;; Import the SDK's api and your adapter
(require
 '[starfederation.datastar.clojure.api :as d*]
 '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])

;; in a ring handler
(defn handler [request]
  ;; Create an SSE response
  (->sse-response request
                  {on-open
                   (fn [sse]
                     ;; Patches elements into the DOM
                     (d*/patch-elements! sse
                                         "<div id=\"question\">What do you put in a toaster?</div>")

                     ;; Patches signals
                     (d*/patch-signals! sse "{response: '', answer: 'bread'}"))})
```

--------------------------------

### Nesting Signals with Object Syntax

Source: https://data-star.dev/guide/backend_requests

Employ object syntax in the `data-signals` attribute for a more structured way to represent nested signals.

```html
1<div data-signals="{foo: {bar: 1}}"></div>
```

--------------------------------

### Implement Rocket Virtual Scroll

Source: https://data-star.dev/examples/rocket_virtual_scroll

Use the virtual-scroll element to initialize the component with a data URL, initial index, and buffer size.

```html
<virtual-scroll
    id="my-rocket-virtual-scroll"
    data-attr:url="'/examples/rocket_virtual_scroll/items'"
    data-attr:initial-index="20"
    data-attr:buffer-size="20"
></virtual-scroll>
```

--------------------------------

### Pro Action: @fit()

Source: https://data-star.dev/reference/actions

The `@fit()` Pro action performs linear interpolation to map a value from one range to another, with options for clamping and rounding.

```APIDOC
## Pro Action: `@fit()`

### Description
Linearly interpolates a value from a source range (`oldMin`, `oldMax`) to a target range (`newMin`, `newMax`). Optional parameters `shouldClamp` and `shouldRound` control the output behavior.

### Syntax
`@fit(v: number, oldMin: number, oldMax: number, newMin: number, newMax: number, shouldClamp?: boolean, shouldRound?: boolean)`

### Examples
```html
<!-- Convert a 0-100 slider to 0-255 RGB value -->
<div>
    <input type="range" min="0" max="100" value="50" data-bind:slider-value>
    <div data-computed:rgb-value="@fit($sliderValue, 0, 100, 0, 255)">
        RGB Value: <span data-text="$rgbValue"></span>
    </div>
</div>

<!-- Convert Celsius to Fahrenheit -->
<div>
    <input type="number" data-bind:celsius value="20" />
    <div data-computed:fahrenheit="@fit($celsius, 0, 100, 32, 212)">
        <span data-text="$celsius"></span>°C = <span data-text="$fahrenheit.toFixed(1)"></span>°F
    </div>
</div>

<!-- Map mouse position to element opacity (clamped) -->
<div
    data-signals:mouse-x="0"
    data-computed:opacity="@fit($mouseX, 0, window.innerWidth, 0, 1, true)"
    data-on:mousemove__window="$mouseX = evt.clientX"
    data-attr:style="'opacity: ' + $opacity"
>
    Move your mouse horizontally to change opacity
</div>
```
```

--------------------------------

### Clojure SDK for SSE Patching

Source: https://data-star.dev/docs.md

This Clojure code uses the Datastar SDK to generate SSE responses. It demonstrates patching elements into the DOM, pausing, and then patching again with updated content.

```clojure
;; Import the SDK's api and your adapter
(require
 '[starfederation.datastar.clojure.api :as d*]
 '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])

;; in a ring handler
(defn handler [request]
  ;; Create an SSE response
  (->sse-response request
                  {on-open
                   (fn [sse]
                     ;; Patches elements into the DOM
                     (d*/patch-elements! sse
                                         "<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
                     (Thread/sleep 1000)
                     (d*/patch-elements! sse
                                         "<div id=\"hal\">Waiting for an order...</div>"))})
```

--------------------------------

### Return SSE Events with Ruby DatastarResponse

Source: https://data-star.dev/guide/backend_requests

Construct a DatastarResponse in Ruby that includes multiple SSE patch elements and signals.

```ruby
return DatastarResponse([
    SSE.patch_elements('<div id="question">...</div>'),
    SSE.patch_elements('<div id="instructions">...</div>'),
    SSE.patch_signals({"answer": "...", "prize": "..."})
])
```

--------------------------------

### Listen to and Dispatch Custom Events

Source: https://data-star.dev/examples/custom_event

Uses data-on to capture custom events and updates a signal with the event detail. The script demonstrates dispatching a custom event periodically.

```html
<p
    id="foo"
    data-signals:_event-details
    data-on:myevent="$_eventDetails = evt.detail"
    data-text="`Last Event Details: ${$_eventDetails}`"
></p>
<script>
    const foo = document.getElementById("foo");
    setInterval(() => {
        foo.dispatchEvent(
            new CustomEvent("myevent", {
                detail: JSON.stringify({
                    eventTime: new Date().toLocaleTimeString(),
                }),
            })
        );
    }, 1000);
</script>
```

--------------------------------

### Show Loading Indicator with data-indicator

Source: https://data-star.dev/reference/attributes

Use `data-indicator:fetching` to create a boolean signal that is true while a fetch request is in flight. This signal can control loading indicators or disable elements.

```html
<button data-on:click="@get('/endpoint')"
        data-indicator:fetching
></button>
```

```html
<button data-on:click="@get('/endpoint')"
        data-indicator:fetching
        data-attr:disabled="$fetching"
></button>
<div data-show="$fetching">Loading...</div>
```

```html
<button data-indicator="fetching"></button>
```

```html
<div data-indicator:fetching data-init="@get('/endpoint')"></div>
```

--------------------------------

### Handle events with data-on

Source: https://data-star.dev/guide/reactive_signals

Use data-on to attach event listeners to elements. Event names are converted to kebab case.

```html
1<input data-bind:foo />
2<button data-on:click="$foo = ''">
3    Reset
4</button>
```

```html
1<div data-on:my-event="$foo = ''">
2    <input data-bind:foo />
3</div>
```

--------------------------------

### Read signals in Ruby

Source: https://data-star.dev/docs.md

Initializes the Datastar object with request and response, then accesses signals via the signals hash.

```ruby
# Setup with request
datastar = Datastar.new(request:, response:)

# Read signals
some_signal = datastar.signals[:some_signal]
```

--------------------------------

### Define a custom web component with Rocket

Source: https://data-star.dev/docs.md

Define a custom web component named 'demo-counter' using the Rocket API. This includes defining props, setting up instance state, and rendering the component's DOM structure.

```javascript
rocket('demo-counter', {
  mode: 'light',
  props: ({ number, string }) => ({
    count: number.step(1).min(0),
    label: string.trim.default('Counter'),
  }),
  setup({ $$, observeProps, props }) {
    $$.count = props.count
    observeProps(() => {
      $$.count = props.count
    }, 'count')
  },
  render({ html, props: { count, label } }) {
    return html`
      <div class="stack gap-2">
        <button
          type="button"
          data-on:click="$$count += 1"
          data-text="${label} + ': ' + $$count"></button>
        <template data-if="$$count !== ${count}">
          <button type="button" data-on:click="$$count = ${count}">Reset</button>
        </template>
      </div>
    `
  },
})
```

--------------------------------

### Include Datastar via CDN

Source: https://data-star.dev/guide/getting_started

Use this script tag to quickly include Datastar from a CDN. Ensure you are using the correct version.

```html
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0/bundles/datastar.js"></script>
```

--------------------------------

### Initialize Mapbox Map

Source: https://data-star.dev/examples/rocket_openfreemap

Initializes a new Mapbox GL JS map instance. This code should be run when the map container element is available. It configures the map's style, center, zoom, and other interaction properties.

```javascript
map = new maplibregl.Map({
        style: props.styleUrl,
        center: props.center,
        zoom: props.zoom,
        bearing: props.bearing,
        pitch: props.pitch,
        container: refs.mapNode,
        cooperativeGestures: true,
        dragRotate: props.dragRotate,
      })
```

--------------------------------

### Match Media Query with Dark Mode

Source: https://data-star.dev/reference/attributes

Sets a signal to indicate if the 'prefers-color-scheme: dark' media query matches. The theme signal is computed based on this match.

```html
<div
    data-match-media:is-dark="'prefers-color-scheme: dark'"
    data-computed:theme="$isDark ? 'dark' : 'light'"
></div>
```

--------------------------------

### Manifest API

Source: https://data-star.dev/reference/rocket

The `manifest` API allows you to add documentation metadata that Rocket cannot infer from the DOM alone. It's used to document slots and events, enabling tooling to describe the full public surface of a component.

```APIDOC
## Manifest API

### Description
Adds documentation metadata for slots and events that Rocket cannot infer from the DOM.

### Method
Not applicable (Configuration object property)

### Endpoint
Not applicable

### Parameters
#### Request Body
- **manifest** (object) - Optional - An object containing `slots` and `events` arrays.
  - **slots** (array) - Optional - An array of slot definitions.
    - **name** (string) - Required - The name of the slot.
    - **description** (string) - Optional - A description of the slot.
  - **events** (array) - Optional - An array of event definitions.
    - **name** (string) - Required - The name of the event.
    - **kind** (string) - Optional - The type of event ('event' or 'custom-event').
    - **bubbles** (boolean) - Optional - Whether the event bubbles.
    - **composed** (boolean) - Optional - Whether the event is composed.
    - **description** (string) - Optional - A description of the event.

### Request Example
```json
{
  "manifest": {
    "slots": [
      { "name": "default", "description": "Dialog body content." },
      { "name": "footer", "description": "Action row content." }
    ],
    "events": [
      {
        "name": "close",
        "kind": "custom-event",
        "bubbles": true,
        "composed": true,
        "description": "Fired when the dialog requests dismissal."
      }
    ]
  }
}
```

### Response
#### Success Response (200)
Not applicable (This is a configuration object, not an API endpoint response)

#### Response Example
Not applicable
```

--------------------------------

### Setting inline styles with data-style

Source: https://data-star.dev/reference

Manage inline CSS styles reactively using expressions.

```html
<div data-style:display="$hiding && 'none'"></div>
<div data-style:background-color="$red ? 'red' : 'blue'"></div>
```

```html
<div data-style="{
    display: $hiding ? 'none' : 'flex',
    'background-color': $red ? 'red' : 'green'
}"></div>
```

```html
<!-- When $x is false, color remains red from inline style -->
<div style="color: red;" data-style:color="$x && 'green'"></div>

<!-- When $hiding is true, display becomes none; when false, reverts to flex from inline style -->
<div style="display: flex;" data-style:display="$hiding && 'none'"></div>
```

--------------------------------

### C# ASP.NET Core: Server-Side Handler for Loading More Data

Source: https://data-star.dev/how_tos/load_more_list_items

Implements a 'load more' endpoint using Datastar in ASP.NET Core. It reads offset signals, patches elements, and updates signals or removes the button as needed.

```csharp
1using System.Text.Json;
2using StarFederation.Datastar;
3using StarFederation.Datastar.DependencyInjection;
4
5public class Program
6{
7    public record OffsetSignals(int offset);
8
9    public static void Main(string[] args)
10    {
11        var builder = WebApplication.CreateBuilder(args);
12        builder.Services.AddDatastar();
13        var app = builder.Build();
14
15        app.MapGet("/more", async (IDatastarService datastarService) =>
16        {
17            var max = 5;
18            var limit = 1;
19            var signals = await datastarService.ReadSignalsAsync<OffsetSignals>();
20            var offset = signals.offset;
21            if (offset < max)
22            {
23                var newOffset = offset + limit;
24                await datastarService.PatchElementsAsync($"<div>Item {newOffset}</div>", new()
25                {
26                    Selector = "#list",
27                    PatchMode = PatchElementsMode.Append,
28                });
29                if (newOffset < max)
30                    await datastarService.PatchSignalsAsync(new OffsetSignals(newOffset));
31                else
32                    await datastarService.RemoveElementAsync("#load-more");
33            }
34        });
35
36        app.Run();
37    }
38}

```

--------------------------------

### Persist Signal with Custom Key

Source: https://data-star.dev/reference/attributes

Persists signal values in local storage using a custom storage key ('mykey' in this case) instead of the default 'datastar'.

```html
<div data-persist:mykey></div>
```

--------------------------------

### Patch Signals via PHP SDK

Source: https://data-star.dev/guide/reactive_signals

Using the PHP Datastar SDK to patch signals.

```php
 1use starfederation\datastar\ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4$sse = new ServerSentEventGenerator();
 5
 6// Patches signals.
 7$sse->patchSignals(['hal' => 'Affirmative, Dave. I read you.']);
 8
 9sleep(1);
10
11$sse->patchSignals(['hal' => '...']);
```

--------------------------------

### Patch DOM elements with Ruby

Source: https://data-star.dev/guide/getting_started

Uses the Datastar::Dispatcher to stream updates within a Rack environment.

```ruby
require 'datastar'

# Create a Datastar::Dispatcher instance

datastar = Datastar.new(request:, response:)

# In a Rack handler, you can instantiate from the Rack env
# datastar = Datastar.from_rack_env(env)

# Start a streaming response
datastar.stream do |sse|
  # Patches elements into the DOM.
  sse.patch_elements %(<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>)

  sleep 1

  sse.patch_elements %(<div id="hal">Waiting for an order...</div>)
end
```

--------------------------------

### C# ASP.NET Core Patch Signals

Source: https://data-star.dev/docs.md

Adds Data-Star as a service and demonstrates patching signals asynchronously in an ASP.NET Core application. Includes a delay before patching again.

```csharp
using StarFederation.Datastar.DependencyInjection;

// Adds Datastar as a service
builder.Services.AddDatastar();

app.MapGet("/hal", async (IDatastarService datastarService) =>
{
    // Patches signals.
    await datastarService.PatchSignalsAsync(new { hal = "Affirmative, Dave. I read you" });

    await Task.Delay(TimeSpan.FromSeconds(3));

    await datastarService.PatchSignalsAsync(new { hal = "..." });
});
```

--------------------------------

### Redirect with Delay using SSE in C#

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Use this to redirect the client to a new URL after a delay, displaying a message during the wait. Requires IDatastarService.

```csharp
using StarFederation.Datastar.DependencyInjection;

app.MapGet("/redirect", async (IDatastarService datastarService) =>
{
    await datastarService.PatchElementsAsync("<div id=\"indicator\">Redirecting in 3 seconds...</div>");
    await Task.Delay(TimeSpan.FromSeconds(3));
    await datastarService.ExecuteScriptAsync("setTimeout(() => window.location = \"/guide\");");
});

```

--------------------------------

### Implement Bad Apple video streaming with Datastar

Source: https://data-star.dev/examples/bad_apple

Uses a label element with data-signals to manage frame content and percentage, updating the DOM in real-time via server-sent events.

```html
 1<label
 2    data-signals="{_percentage: 0, _contents: 'bad apple frames go here'}"
 3    data-init="@get('/examples/bad_apple/updates')"
 4>
 5    <span data-text="`Percentage: ${$_percentage.toFixed(2)}%`"></span>
 6    <input
 7        type="range"
 8        min="0"
 9        max="100"
10        step="0.01"
11        disabled
12        style="cursor: default"
13        data-attr:value="$_percentage"
14    />
15</label>
16<pre style="line-height: 100%" data-text="$_contents"></pre>
```

--------------------------------

### Patching Elements with SDKs

Source: https://data-star.dev/guide

Use language-specific SDKs to stream patch events to the client.

```clojure
 1;; Import the SDK's api and your adapter
 2(require
 3 '[starfederation.datastar.clojure.api :as d*]
 4 '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
 5
 6;; in a ring handler
 7(defn handler [request]
 8  ;; Create an SSE response
 9  (->sse-response request
10                  {on-open
11                   (fn [sse]
12                     ;; Patches elements into the DOM
13                     (d*/patch-elements! sse
14                                         "<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
15                     (Thread/sleep 1000)
16                     (d*/patch-elements! sse
17                                         "<div id=\"hal\">Waiting for an order...</div>"))}))
```

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3// Adds Datastar as a service
 4builder.Services.AddDatastar();
 5
 6app.MapGet("/", async (IDatastarService datastarService) =>
 7{
 8    // Patches elements into the DOM.
 9    await datastarService.PatchElementsAsync(@"<div id=""hal"">I’m sorry, Dave. I’m afraid I can’t do that.</div>");
10
11    await Task.Delay(TimeSpan.FromSeconds(1));
12
13    await datastarService.PatchElementsAsync(@"<div id=""hal"">Waiting for an order...</div>");
14});
```

```go
 1import (
 2    "github.com/starfederation/datastar-go/datastar"
 3    time
 4)
 5
 6// Creates a new `ServerSentEventGenerator` instance.
 7sse := datastar.NewSSE(w,r)
 8
 9// Patches elements into the DOM.
10sse.PatchElements(
11    `<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>`
12)
13
14time.Sleep(1 * time.Second)
15
16sse.PatchElements(
17    `<div id="hal">Waiting for an order...</div>`
18)
```

```java
 1import starfederation.datastar.utils.ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
 5ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);
 6
 7// Patches elements into the DOM.
 8generator.send(PatchElements.builder()
 9    .data("<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
10    .build()
11);
12
13Thread.sleep(1000);
14
15generator.send(PatchElements.builder()
16    .data("<div id=\"hal\">Waiting for an order...</div>")
17    .build()
18);
```

```kotlin
 1val generator = ServerSentEventGenerator(response)
 2
 3generator.patchElements(
```

--------------------------------

### Use Interval Execution

Source: https://data-star.dev/reference/attributes

Executes an expression at a default one-second interval.

```html
<div data-on-interval="$count++"></div>
```

--------------------------------

### DBMon HTML Structure

Source: https://data-star.dev/examples/dbmon

This HTML snippet defines the structure for the DBMon demo, including input fields for mutation rate and FPS, and a table to display database cluster information. It uses Datastar-specific attributes for data binding and event handling.

```html
<div
    id="demo"
    data-init="@get('/examples/dbmon/updates')"
    data-signals:_editing__ifmissing="false"
>
    <p>
        Average render time for entire page: { renderTime }
    </p>
    <div role="group">
        <label>
            Mutation Rate %
            <input
                type="number"
                min="0"
                max="100"
                value="20"
                data-on:focus="$_editing = true"
                data-on:blur="@put('/examples/dbmon/inputs'); $_editing = false"
                data-attr:data-bind:mutation-rate="$_editing"
                data-attr:data-bind:_mutation-rate="!$_editing"
            />
        </label>
        <label>
            FPS
            <input
                type="number"
                min="1"
                max="144"
                value="60"
                data-on:focus="$_editing = true"
                data-on:blur="@put('/examples/dbmon/inputs'); $_editing = false"
                data-attr:data-bind:fps="$_editing"
                data-attr:data-bind:_fps="!$_editing"
            />
        </label>
    </div>
    <table style="table-layout: fixed; width: 100%; word-break: break-all">
        <tbody>
            <!-- Dynamic rows generated by server -->
            <tr>
                <td>cluster1</td>
                <td style="background-color: var(--_active-color)" class="success">
                    8
                </td>
                <td aria-description="SELECT blah from something">
                    12ms
                </td>
                <!-- More query cells... -->
            </tr>
            <!-- More database rows... -->
        </tbody>
    </table>
</div>
```

--------------------------------

### Stream SSE events in Python

Source: https://data-star.dev/guide/backend_requests

Returns a DatastarResponse containing patch elements and signals.

```python
1from datastar_py import ServerSentEventGenerator as SSE
2from datastar_py.litestar import DatastarResponse
3
4async def endpoint():
5    return DatastarResponse([
6        SSE.patch_elements('<div id="question">What do you put in a toaster?</div>'),
7        SSE.patch_signals({"response": "", "answer": "bread"})
8    ])
```

--------------------------------

### Reading Signals in PHP

Source: https://data-star.dev/guide/backend_requests

Use the `ServerSentEventGenerator::readSignals()` static method in PHP to read all signals from the current request.

```php
1use starfederation\datastar\ServerSentEventGenerator;
2
3// Reads all signals from the request.
4$signals = ServerSentEventGenerator::readSignals();
```

--------------------------------

### Handle attribute casing for signals

Source: https://data-star.dev/guide/reactive_signals

Demonstrates how hyphenated attribute names are converted to camelCase signals.

```html
<!-- Both of these create the signal `$fooBar` -->
<input data-bind:foo-bar />
<input data-bind="fooBar" />
```

--------------------------------

### Sync Query String with History and Filter

Source: https://data-star.dev/reference/attributes

Enables history support for query string synchronization, adding a new history entry on each signal change. It also filters out empty values when syncing to the query string.

```html
<div data-query-string__filter__history></div>
```

--------------------------------

### Handle Events with data-on

Source: https://data-star.dev/reference

Attaches event listeners to elements. The 'evt' variable is available within the expression context.

```html
<button data-on:click="$foo = ''">Reset</button>
```

```html
<div data-on:my-event="$foo = evt.detail"></div>
```

--------------------------------

### Patch Signals via Python SDK

Source: https://data-star.dev/guide/reactive_signals

Using the Python Datastar SDK with Sanic to stream signal patches.

```python
1from datastar_py import ServerSentEventGenerator as SSE
2from datastar_py.sanic import datastar_response
3
4@app.get('/do-you-read-me')
5@datastar_response
6async def open_doors(request):
7    yield SSE.patch_signals({"hal": "Affirmative, Dave. I read you."})
8    await asyncio.sleep(1)
9    yield SSE.patch_signals({"hal": "..."})
```

--------------------------------

### Format numbers and dates with @intl()

Source: https://data-star.dev/reference/actions

Use the @intl() helper to format numbers as currency or dates according to specific locale settings.

```html
<!-- Converts a number to a formatted USD currency string in the user’s locale -->
<div data-text="@intl('number', 1000000, {style: 'currency', currency: 'USD'})"></div>

<!-- Converts a date to a formatted string in the specified locale -->
<div data-text="@intl('datetime', new Date(), {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'}, 'de-AT')"></div>
```

--------------------------------

### Stream SSE events in C#

Source: https://data-star.dev/guide/backend_requests

Registers Datastar as a service and uses the IDatastarService to patch DOM elements and signals.

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3// Adds Datastar as a service
 4builder.Services.AddDatastar();
 5
 6app.MapGet("/", async (IDatastarService datastarService) =>
 7{
 8    // Patches elements into the DOM.
 9    await datastarService.PatchElementsAsync(@"<div id=""question"">What do you put in a toaster?</div>");
10
11    // Patches signals.
12    await datastarService.PatchSignalsAsync(new { response = "", answer = "bread" });
13});
```

--------------------------------

### PHP SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Uses `ServerSentEventGenerator` to send SSE events for patching elements and executing a JavaScript redirect.

```php
use starfederation\datastar\ServerSentEventGenerator;

$sse = new ServerSentEventGenerator();
$sse->patchElements(`
    <div id="indicator">Redirecting in 3 seconds...</div>
`);
sleep(3);
$sse->executeScript(`
    window.location = "/guide"
`);
```

--------------------------------

### Manage global signals with data-signals

Source: https://data-star.dev/guide/reactive_signals

Use data-signals to patch global signals. Hyphenated names are converted to camel case, and dot-notation supports nested signals.

```html
1<div data-signals:foo-bar="1"></div>
```

```html
1<div data-signals:form.baz="2"></div>
```

```html
1<div data-signals:foo-bar="1"
2     data-text="$fooBar"
3></div>
```

```html
1<div data-signals="{fooBar: 1, form: {baz: 2}}"></div>
```

--------------------------------

### Patch Signals via Kotlin SDK

Source: https://data-star.dev/guide/reactive_signals

Using the Kotlin Datastar SDK to patch signals.

```kotlin
 1val generator = ServerSentEventGenerator(response)
 2
 3generator.patchSignals(
 4    signals = """{"hal": "Affirmative, Dave. I read you."}""",
 5)
 6
 7Thread.sleep(ONE_SECOND)
 8
 9generator.patchSignals(
10    signals = """{"hal": "..."}""",
11)
```

--------------------------------

### Create element references with data-ref

Source: https://data-star.dev/docs.md

Defines a signal that references the DOM element. The reference can be defined via attribute key or value.

```html
<div data-ref:foo></div>
```

```html
<div data-ref="foo"></div>
```

```html
$foo is a reference to a <span data-text="$foo.tagName"></span> element
```

--------------------------------

### Read signals in C#

Source: https://data-star.dev/docs.md

Uses the Datastar dependency injection service to deserialize signals into a strongly-typed record.

```csharp
using StarFederation.Datastar.DependencyInjection;

// Adds Datastar as a service
builder.Services.AddDatastar();

public record Signals
{
    [JsonPropertyName("foo")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public FooSignals? Foo { get; set; } = null;

    public record FooSignals
    {
        [JsonPropertyName("bar")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Bar { get; set; }
    }
}

app.MapGet("/read-signals", async (IDatastarService datastarService)
{
    Signals? mySignals = await datastarService.ReadSignalsAsync<Signals>();
    var bar = mySignals?.Foo?.Bar;
});
```

--------------------------------

### Initialize and Reset Virtual Scroll State

Source: https://data-star.dev/examples/rocket_virtual_scroll

Logic for initializing the viewport, setting up mutation observers, and resetting scroll state variables.

```javascript
if (!hasInitializedScroll && viewport) {
        viewport.addEventListener('scroll', () => {
          checkScroll()
          clearTimeout(scrollTimeout)
          scrollTimeout = setTimeout(checkScroll, 25)
        })
        if (props.initialIndex > 0 && viewport.scrollTop === 0) {
          viewport.scrollTop = props.initialIndex * avgItemHeight
        }
        hasInitializedScroll = true
      }
    }

    const reset = () => {
      if (
        !viewport ||
        !spacer ||
        !blocks.A ||
        !blocks.B ||
        !blocks.C ||
        !host.id
      ) {
        return
      }
      blockAStartIndex = Math.max(0, props.initialIndex - props.bufferSize)
      blockBStartIndex = props.initialIndex
      blockCStartIndex = props.initialIndex + props.bufferSize
      blockAY = 0
      blockBY = 0
      blockCY = 0
      avgItemHeight = 50
      scrollHeight = 0
      isLoading = false
      blockPositions = ['A', 'B', 'C']
      measuredItems = 0
      totalMeasuredHeight = 0
      hasInitializedScroll = false
      lastProcessedScroll = 0
      clearJumpTimeout()
      spacer.style.height = '0px'
      for (const name of ['A', 'B', 'C']) {
        blocks[name]?.replaceChildren()
        blocks[name]?.style.setProperty('transform', 'translateY(0px)')
        lastBlockContent[name] = ''
      }
      viewport.scrollTop = props.initialIndex * avgItemHeight
      viewport.style.height = `${host.offsetHeight || 600}px`
      setHeights()
      loadBlock(blockAStartIndex, 'all')
    }

    const init = () => {
      viewport = /** @type {HTMLElement | null} */ (refs.viewport)
      spacer = /** @type {HTMLElement | null} */ (refs.spacer)
      blocks = {
        A: /** @type {HTMLElement | null} */ (refs.blockA),
        B: /** @type {HTMLElement | null} */ (refs.blockB),
        C: /** @type {HTMLElement | null} */ (refs.blockC),
      }
      if (!viewport || !spacer || !blocks.A || !blocks.B || !blocks.C) return

      viewport.style.height = `${host.offsetHeight || 600}px`
      observer?.disconnect()
      observer = new MutationObserver(checkBlocksLoaded)
      observer.observe(host, {
        childList: true,
        subtree: true,
        characterData: true,
      })
      setTimeout(reset, 50)
    }

    init()

    observeProps(reset)

    cleanup(() => {
      observer?.disconnect()
      clearJumpTimeout()
      clearTimeout(scrollTimeout)
    })
```

--------------------------------

### Custom Web Components (`rocket()`)

Source: https://data-star.dev/docs.md

The `rocket()` function is a Pro feature for defining custom web components using Data Star.

```APIDOC
## `rocket()` Function

### Description
Defines a custom web component using Data Star’s `rocket` API. It handles reactivity, local signal scoping, action dispatch, and DOM application.

### Signature
`rocket(tagName, { mode, props, setup, render })`

### Parameters
- **tagName** (string) - Required - The tag name for the custom element.
- **options** (object) - Required - Configuration object for the custom element.
  - **mode** (string) - Optional - The rendering mode (e.g., 'light').
  - **props** (function) - Required - A function that defines the public props of the component using codecs (e.g., `number`, `string`).
  - **setup** (function) - Optional - A function to define non-DOM instance behavior. Receives `$$`, `observeProps`, and `props` as arguments.
  - **render** (function) - Required - A function that returns the component's DOM structure using `html` tagged template literal. Receives `html` and `props` as arguments.

### Example Usage
```javascript
rocket('demo-counter', {
  mode: 'light',
  props: ({ number, string }) => ({
    count: number.step(1).min(0),
    label: string.trim.default('Counter'),
  }),
  setup({ $$, observeProps, props }) {
    $$.count = props.count;
    observeProps(() => {
      $$.count = props.count;
    }, 'count');
  },
  render({ html, props: { count, label } }) {
    return html`
      <div class="stack gap-2">
        <button
          type="button"
          data-on:click="$$count += 1"
          data-text="${label} + ': ' + $$count"></button>
        <template data-if="$$count !== ${count}">
          <button type="button" data-on:click="$$count = ${count}">Reset</button>
        </template>
      </div>
    `;
  },
});
```

### Example in HTML
```html
<script type="module">
  import { rocket } from '/bundles/datastar-pro.js';
  // define demo-counter here
</script>

<demo-counter count="5" label="Inventory"></demo-counter>
```
```

--------------------------------

### Patch Signals via Java SDK

Source: https://data-star.dev/guide/reactive_signals

Using the Java Datastar SDK to send signal patches via a ServerSentEventGenerator.

```java
 1import starfederation.datastar.utils.ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
 5ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);
 6
 7// Patches signals.
 8generator.send(PatchSignals.builder()
 9    .data("{\"hal\": \"Affirmative, Dave. I read you.\"}")
10    .build()
11);
12
13Thread.sleep(1000);
14
15generator.send(PatchSignals.builder()
16    .data("{\"hal\": \"...\"}")
17    .build()
18);
```

--------------------------------

### data-init

Source: https://data-star.dev/reference/attributes

Executes an expression when the attribute is initialized or modified.

```APIDOC
## data-init

### Description
Runs an expression when the attribute is initialized (page load, DOM patch, or attribute modification).

### Modifiers
- `__delay`: Delays the execution (e.g., .500ms, .1s).
- `__viewtransition`: Wraps the expression in `document.startViewTransition()`.
```

--------------------------------

### Create Element Reference Signal (Key)

Source: https://data-star.dev/reference/attributes

Use `data-ref:signalName` to create a signal that references the element. The signal name is specified directly in the attribute key.

```html
<div data-ref:foo></div>
```

--------------------------------

### Listen for Enter or Ctrl + L Keydown Events Globally

Source: https://data-star.dev/how_tos/bind_keydown_events_to_specific_keys

Combine conditions to trigger an alert for either the 'Enter' key or the 'Ctrl + L' combination.

```html
<div data-on:keydown__window="(evt.key === 'Enter' || (evt.ctrlKey && evt.key === 'l')) && alert('Key pressed')"></div>
```

--------------------------------

### Read signals in PHP

Source: https://data-star.dev/docs.md

Uses the ServerSentEventGenerator helper to read all signals from the current request.

```php
use starfederation\datastar\ServerSentEventGenerator;

// Reads all signals from the request.
$signals = ServerSentEventGenerator::readSignals();
```

--------------------------------

### Go SSE Patch Signals

Source: https://data-star.dev/docs.md

Creates a Server-Sent Event generator in Go and uses it to patch signals, with a short delay between updates.

```go
import (
    "github.com/starfederation/datastar-go/datastar"
)

// Creates a new `ServerSentEventGenerator` instance.
sse := datastar.NewSSE(w, r)

// Patches signals
sse.PatchSignals([]byte(`{hal: 'Affirmative, Dave. I read you.'}`))

time.Sleep(1 * time.Second)

sse.PatchSignals([]byte(`{hal: '...'}`))
```

--------------------------------

### Interval Timer (data-on-interval)

Source: https://data-star.dev/docs.md

Runs an expression at a regular interval, configurable via duration modifiers.

```APIDOC
## data-on-interval

### Description
Runs an expression repeatedly at a set interval.

### Modifiers
- __duration: Set interval duration (.500ms, .1s, .leading).
- __viewtransition: Wrap in document.startViewTransition().

### Request Example
<div data-on-interval__duration.500ms="$count++"></div>
```

--------------------------------

### C# ASP.NET Core SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Utilizes `IDatastarService` to asynchronously patch elements and execute a script for redirection.

```csharp
using StarFederation.Datastar.DependencyInjection;

app.MapGet("/redirect", async (IDatastarService datastarService) =>
{
    await datastarService.PatchElementsAsync("<div id=\"indicator\">Redirecting in 3 seconds...</div>");
    await Task.Delay(TimeSpan.FromSeconds(3));
    await datastarService.ExecuteScriptAsync("window.location = \"/guide\";");
});
```

--------------------------------

### Clojure SSE Redirect with setTimeout Workaround

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Demonstrates using `setTimeout` within `executeScript` to prevent URL replacement in Firefox history.

```clojure
(require
  '[starfederation.datastar.clojure.api :as d*]
  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]
  '[some.hiccup.library :refer [html]])


(defn handle [ring-request]
  (->sse-response ring-request
    {on-open
      (fn [sse]

```

--------------------------------

### Calling External Functions with Arguments

Source: https://data-star.dev/guide/datastar_expressions

Use data attributes to bind input values to function arguments and capture the return value in a signal. This pattern is useful for encapsulating logic in external scripts.

```html
1<div data-signals:result>
2    <input data-bind:foo
3        data-on:input="$result = myfunction($foo)"
4    >
5    <span data-text="$result"></span>
6</div>
```

--------------------------------

### Apply Event Modifiers

Source: https://data-star.dev/reference/attributes

Demonstrates the use of event modifiers like window attachment, debouncing, and casing on standard DOM events.

```html
<button data-on:click__window__debounce.500ms.leading="$foo = ''"></button>
<div data-on:my-event__case.camel="$foo = ''"></div>
```

--------------------------------

### Defining the Target Patch Element

Source: https://data-star.dev/guide/getting_started

The backend returns HTML content that matches an existing element ID in the DOM for morphing.

```html
1<div id="hal">
2    I’m sorry, Dave. I’m afraid I can’t do that.
3</div>
```

--------------------------------

### Stream SSE events in Clojure

Source: https://data-star.dev/guide/backend_requests

Uses the http-kit adapter to patch elements and signals within a Ring handler.

```clojure
 1;; Import the SDK's api and your adapter
 2(require
 3 '[starfederation.datastar.clojure.api :as d*]
 4 '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
 5
 6;; in a ring handler
 7(defn handler [request]
 8  ;; Create an SSE response
 9  (->sse-response request
10                  {on-open
11                   (fn [sse]
12                     ;; Patches elements into the DOM
13                     (d*/patch-elements! sse
14                                         "<div id=\"question\">What do you put in a toaster?</div>")
15
16                     ;; Patches signals
17                     (d*/patch-signals! sse "{response: '', answer: 'bread'}"))}))
```

--------------------------------

### Dynamic Polling Frequency in C#

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses Datastar Dependency Injection to map an endpoint that patches elements with a dynamic duration.

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3app.MapGet("/endpoint", async (IDatastarService datastarService) =>
 4{
 5    var currentTime = DateTime.Now.ToString("yyyy-MM-dd hh:mm:ss");
 6    var currentSeconds = DateTime.Now.Second;
 7    var duration = currentSeconds < 50 ? 5 : 1;
 8    await datastarService.PatchElementsAsync($"""
 9        <div id="time" data-on-interval__duration.{duration}s="@get('/endpoint')">
10            {currentTime}
11        </div>
12    """);
13});
```

--------------------------------

### Trigger Backend Action via Button

Source: https://data-star.dev/guide/datastar_expressions

Uses a button to trigger a backend endpoint request.

```html
<button data-on:click="@get('/endpoint')">
    What are you talking about, HAL?
</button>
```

--------------------------------

### Patch Signals via C# SDK

Source: https://data-star.dev/guide/reactive_signals

Using the C# Datastar SDK to patch signals within an ASP.NET Core endpoint.

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3// Adds Datastar as a service
 4builder.Services.AddDatastar();
 5
 6app.MapGet("/hal", async (IDatastarService datastarService) =>
 7{
 8    // Patches signals.
 9    await datastarService.PatchSignalsAsync(new { hal = "Affirmative, Dave. I read you" });
10
11    await Task.Delay(TimeSpan.FromSeconds(3));
12
13    await datastarService.PatchSignalsAsync(new { hal = "..." });
14});
```

--------------------------------

### Stream SSE events in Ruby

Source: https://data-star.dev/guide/backend_requests

Uses the Datastar dispatcher to stream patches within a block.

```ruby
 1require 'datastar'
 2
 3# Create a Datastar::Dispatcher instance
 4
 5datastar = Datastar.new(request:, response:)
 6
 7# In a Rack handler, you can instantiate from the Rack env
 8# datastar = Datastar.from_rack_env(env)
 9
10# Start a streaming response
11datastar.stream do |sse|
12  # Patches elements into the DOM
13  sse.patch_elements %(<div id="question">What do you put in a toaster?</div>)
14
15  # Patches signals
16  sse.patch_signals(response: '', answer: 'bread')
17end
```

--------------------------------

### Python Sanic SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Leverages `datastar_py` and Sanic to yield SSE events for updating the DOM and executing a redirect script.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

@app.get("/redirect")
@datastar_response
async def redirect_from_backend():
    yield SSE.patch_elements('<div id="indicator">Redirecting in 3 seconds...</div>')
    await asyncio.sleep(3)
    yield SSE.execute_script('window.location = "/guide"')
```

--------------------------------

### data-on

Source: https://data-star.dev/reference/attributes

Attaches event listeners to elements to execute expressions.

```APIDOC
## data-on

### Description
Attaches an event listener to an element, executing an expression whenever the event is triggered. Provides an `evt` variable representing the event object. `data-on:submit` automatically prevents default form submission.
```

--------------------------------

### Stream SSE events in PHP

Source: https://data-star.dev/guide/backend_requests

Instantiates a ServerSentEventGenerator to patch DOM elements and signals.

```php
 1use starfederation\datastar\ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4$sse = new ServerSentEventGenerator();
 5
 6// Patches elements into the DOM.
 7$sse->patchElements(
 8    '<div id="question">What do you put in a toaster?</div>'
 9);
10
11// Patches signals.
12$sse->patchSignals(['response' => '', 'answer' => 'bread']);
```

--------------------------------

### data-query-string

Source: https://data-star.dev/reference

Syncs query string parameters to signal values.

```APIDOC
## data-query-string

### Description
Syncs query string params to signal values on page load, and syncs signal values to query string params on change.

### Modifiers
- `__filter` - Filters out empty values.
- `__history` - Enables history support.
```

--------------------------------

### Reading Nested Signals in C#

Source: https://data-star.dev/guide/backend_requests

Configure Datastar services and define a C# record to read nested signals like `foo.bar` from incoming requests using `IDatastarService`.

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3// Adds Datastar as a service
 4builder.Services.AddDatastar();
 5
 6public record Signals
 7{
 8    [JsonPropertyName("foo")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
 9    public FooSignals? Foo { get; set; } = null;
10
11    public record FooSignals
12    {
13        [JsonPropertyName("bar")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
14        public string? Bar { get; set; }
15    }
16}
17
18app.MapGet("/read-signals", async (IDatastarService datastarService) =>
19{
20    Signals? mySignals = await datastarService.ReadSignalsAsync<Signals>();
21    var bar = mySignals?.Foo?.Bar;
22});
```

--------------------------------

### Kotlin SSE Patch Signals

Source: https://data-star.dev/docs.md

Demonstrates patching signals using ServerSentEventGenerator in Kotlin, with a constant for the sleep duration.

```kotlin
val generator = ServerSentEventGenerator(response)

generator.patchSignals(
    signals = """{"hal": "Affirmative, Dave. I read you."} """,
)

Thread.sleep(ONE_SECOND)

generator.patchSignals(
    signals = """{"hal": "..."} """,
)
```

--------------------------------

### Perform PUT request

Source: https://data-star.dev/reference/actions

Sends a PUT request to the backend.

```html
<button data-on:click="@put('/endpoint')"></button>
```

--------------------------------

### Datastar Free Version Convenience Attributes

Source: https://data-star.dev/essays/greedy_developer

These Datastar attributes can be used in the free version to replicate Pro features. The first replaces the current URL on load and whenever a page variable changes. The second scrolls an element into view.

```html
1<!-- Replaces the current URL on load and whenever $page changes. -->
2<div data-effect="window.history.replaceState({}, '', '/page/' + $page)"></div>
```

```html
3
4<!-- Scrolls the element into view. -->
5<div data-init="el.scrollIntoView()"></div>
```

--------------------------------

### Default Request Cancellation Behavior

Source: https://data-star.dev/docs.md

Demonstrates the default behavior where rapid clicks on a button cancel previous pending requests.

```html
<!-- Clicking this button multiple times will cancel previous requests (default behavior) -->
<button data-on:click="@get('/slow-endpoint')">Load Data</button>
```

--------------------------------

### Render Current Time with Interval Update

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Combines interval updates with rendering dynamic content like the current time. The backend should respond with a `datastar-patch-elements` event to update the content.

```html
<div id="time"
     data-on-interval__duration.5s="@get('/endpoint')"
>
     {{ now }}
</div>
```

--------------------------------

### Register Edge Entry and Handle Selection

Source: https://data-star.dev/examples/rocket_flow

Registers an edge entry, updates its key, and sets up event listeners for pointer interactions. It handles edge selection by dispatching a custom event and applying selection classes.

```javascript
const registerEdgeEntry = (entry, previousKey = entry.key) => {
      entry.key = makeEdgeKey(entry.sourceId, entry.targetId, entry.id)
      if (
        previousKey &&
        previousKey !== entry.key &&
        edgesByKey.get(previousKey) === entry
      ) {
        edgesByKey.delete(previousKey)
      }
      if (entry.key) edgesByKey.set(entry.key, entry)
      if (entry.group) {
        if (entry.sourceId) entry.group.dataset.sourceId = entry.sourceId
        else delete entry.group.dataset.sourceId
        if (entry.targetId) entry.group.dataset.targetId = entry.targetId
        else delete entry.group.dataset.targetId
        if (entry.id) entry.group.dataset.edgeId = entry.id
        else delete entry.group.dataset.edgeId
        if (entry.key) entry.group.dataset.edgeKey = entry.key
        else delete entry.group.dataset.edgeKey
      }
      if (entry.group && !edgeSelectionBoundGroups.has(entry.group)) {
        edgeSelectionBoundGroups.add(entry.group)
        entry.group.addEventListener('pointerdown', (evt) => {
          evt.stopPropagation()
          evt.preventDefault()
          if (!entry.key) registerEdgeEntry(entry)
          if (!entry.key) return
          selectedEdgeKey = entry.key
          applyEdgeSelectionClasses()
          host.dispatchEvent(
            new CustomEvent('flow-edge-select', {
              detail: {
                id: entry.id ?? '',
                sourceId: entry.sourceId ?? '',
                targetId: entry.targetId ?? '',
              },
              bubbles: true,
              composed: true,
            }),
          )
          try {
            host.focus({ preventScroll: true })
          } catch {}
        })
      }
      applyEdgeSelectionClasses()
    }
```

--------------------------------

### Include Aliased Datastar Bundle

Source: https://data-star.dev/reference/attributes

Loads the aliased version of the Datastar library to avoid conflicts with legacy libraries.

```html
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0/bundles/datastar-aliased.js"></script>
```

--------------------------------

### Dynamic Polling Frequency in Rust

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses the Datastar prelude and chrono to stream patched elements.

```rust
 1use datastar::prelude::*;
 2use chrono::Local;
 3use async_stream::stream;
 4
 5let current_time = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
 6let current_seconds = Local::now().second();
 7let duration = if current_seconds < 50 {
 8    5
 9} else {
10    1
11};
12
13Sse(stream! {
14    yield PatchElements::new(
15        format!(
16            "<div id='time' data-on-interval__duration.{}s='@get(\"/endpoint\")'>{}</div>",
17            duration,
18            current_time,
19        )
20    ).into();
21})
```

--------------------------------

### Create computed signals

Source: https://data-star.dev/docs.md

Define read-only signals that update automatically when dependencies change.

```html
<div data-computed:foo="$bar + $baz"></div>
```

```html
<div data-computed:foo="$bar + $baz"></div>
<div data-text="$foo"></div>
```

```html
<div data-computed="{foo: () => $bar + $baz}"></div>
```

```html
<div data-computed:my-signal__case.kebab="$bar + $baz"></div>
```

--------------------------------

### Handle DataStar Fetch Events

Source: https://data-star.dev/reference/actions

Listen for `datastar-fetch` events on an element to react to different stages of a fetch request, such as errors.

```html
<div data-on:datastar-fetch="
    evt.detail.type === 'error' && console.log('Fetch error encountered')
"></div>
```

--------------------------------

### Implement Custom Element Class

Source: https://data-star.dev/guide/datastar_expressions

Defines a standard HTMLElement that observes attributes and dispatches custom events.

```javascript
class MyComponent extends HTMLElement {
    static get observedAttributes() {
        return ['src'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        const value = `You entered: ${newValue}`;
        this.dispatchEvent(
            new CustomEvent('mycustomevent', {detail: {value}})
        );
    }
}

customElements.define('my-component', MyComponent);
```

--------------------------------

### Sync Filtered Query String Params to Signals

Source: https://data-star.dev/reference/attributes

Synchronizes query string parameters to signal values, filtering based on include and exclude regular expressions. This allows selective syncing.

```html
<div data-query-string="{include: /foo/, exclude: /bar/}"></div>
```

--------------------------------

### Patch DOM elements with Python

Source: https://data-star.dev/guide/getting_started

Uses the datastar_py library with Sanic to yield patch events.

```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

@app.get('/open-the-bay-doors')
@datastar_response
async def open_doors(request):
    yield SSE.patch_elements('<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>')
    await asyncio.sleep(1)
    yield SSE.patch_elements('<div id="hal">Waiting for an order...</div>')
```

--------------------------------

### Toggling Nested Signals

Source: https://data-star.dev/docs.md

Use the toggleAll action with regex patterns to manipulate multiple nested signals simultaneously.

```html
<div data-signals="{menu: {isOpen: {desktop: false, mobile: false}}}">
    <button data-on:click="@toggleAll({include: /^menu\.isOpen\./})">
        Open/close menu
    </button>
</div>
```

--------------------------------

### Sync Query String Params to Signals

Source: https://data-star.dev/reference/attributes

Synchronizes query string parameters with signal values on page load and updates the query string when signals change. An empty div indicates default behavior.

```html
<div data-query-string></div>
```

--------------------------------

### Server-Sent Events for Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Backend sends SSE events to first update an indicator and then append a script tag to redirect the page after a delay.

```sse
event: datastar-patch-elements
data: elements <div id="indicator">Redirecting in 3 seconds...</div>

// Wait 3 seconds

event: datastar-patch-elements
data: selector body
data: mode append
data: elements <script>window.location.href = "/guide"</script>


```

--------------------------------

### Clojure: Server-Side Handler for Loading More Data

Source: https://data-star.dev/how_tos/load_more_list_items

Handles incoming requests, reads signals, and patches elements or signals to implement a "load more" feature. Closes the SSE connection after processing.

```clojure
1(require
2  '[starfederation.datastar.clojure.api :as d*]
3  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]
4  '[some.hiccup.library :refer [html]]
5  '[some.json.library :refer [read-json-str write-json-str]]))
6
7
8(def max-offset 5)
9
10(defn handler [ring-request]
11  (->sse-response ring-request
12    {on-open
13     (fn [sse]
14       (let [d*-signals (-> ring-request d*/get-signals read-json-str)
15             offset (get d*-signals "offset")
16             limit 1
17             new-offset (+ offset limit)]
18
19         (d*/patch-elements! sse
20                             (html [:div "Item " new-offset])
21                             {d*/selector   "#list"
22                              d*/merge-mode d*/mm-append})
23
24         (if (< new-offset max-offset)
25           (d*/patch-signals! sse (write-json-str {"offset" new-offset}))
26           (d*/remove-fragment! sse "#load-more"))
27
28         (d*/close-sse! sse)))}))

```

--------------------------------

### Set All Matching Signals with @setAll()

Source: https://data-star.dev/reference/actions

The @setAll() action sets the value of signals that match a provided filter. It can target all signals or specific ones using include and exclude regular expressions.

```html
<!-- Sets the `foo` signal only -->
<div data-signals:foo="false">
    <button data-on:click="@setAll(true, {include: /^foo$/})"></button>
</div>
```

```html
<!-- Sets all signals starting with `user.` -->
<div data-signals="{user: {name: '', nickname: ''}}">
    <button data-on:click="@setAll('johnny', {include: /^user\./})"></button>
</div>
```

```html
<!-- Sets all signals except those ending with `_temp` -->
<div data-signals="{data: '', data_temp: '', info: '', info_temp: ''}">
    <button data-on:click="@setAll('reset', {include: /.*/, exclude: /_temp$/})"></button>
</div>
```

--------------------------------

### Implement a Counter Component with Rocket

Source: https://data-star.dev/reference/rocket

Defines a component with typed props and local state managed via Datastar attributes.

```javascript
 1rocket('demo-stepper', {
 2  mode: 'light',
 3  props: ({ number, string }) => ({
 4    start: number.min(0),
 5    step: number.min(1).default(1),
 6    label: string.trim.default('Count'),
 7  }),
 8  setup({ $$, props }) {
 9    $$.count = props.start
10  },
11  render({ html, props: { label, step } }) {
12    return html`
13      <section class="stack gap-2">
14        <h3>${label}</h3>
15        <div class="row gap-2">
16          <button data-on:click="$$count -= ${step}" data-attr:disabled="$$count <= 0">-</button>
17          <output data-text="$$count"></output>
18          <button data-on:click="$$count += ${step}">+</button>
19        </div>
20      </section>
21    `
22  },
23})
```

--------------------------------

### Loop Rendering with Rocket

Source: https://data-star.dev/docs.md

Employ `data-for` to render lists from iterables. It supports custom aliases for item and index, and accepts any Datastar iterable expression.

```javascript
rocket('demo-letter-list', {
  mode: 'light',
  setup({ $$ }) {
    $$.letters = ['A', 'B', 'C']
  },
  render: ({ html }) => html`
    <ul>
      <template data-for="letter, row in $$letters">
        <li>
          <strong data-text="row + 1"></strong>
          <span data-text="letter"></span>
        </li>
      </template>
    </ul>
  `,
})
```

--------------------------------

### Handle Node Registration and Updates

Source: https://data-star.dev/examples/rocket_flow

Functions to register new nodes or update existing node properties like position, dimensions, and content.

```javascript
const onNodeRegister = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
      hideFlowChild(target)
      const detail =
        /** @type {CustomEvent<Record<string, any>>} */ (evt).detail ?? {}
      const entry = nodes.get(target) ?? {
        el: target,
        group: null,
        x: 0,
        y: 0,
        width: DEFAULT_NODE_WIDTH,
        height: DEFAULT_NODE_HEIGHT,
      }
      entry.x = detail.x
      entry.y = detail.y
      entry.width = detail.width
      entry.height = detail.height
      updateNodeId(entry, detail.id ?? target.getAttribute('id'))
      nodes.set(target, entry)
      ensureNodeGroup(entry)
      if (detail.content) applyNodeContent(entry, detail.content)
      scheduleNodeRender()
      positionNode(entry)
    }
```

```javascript
const onNodeUpdate = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
      const entry = nodes.get(target)
      if (!entry) return
      const detail =
        /** @type {CustomEvent<Record<string, any>>} */ (evt).detail ?? {}
      if ('x' in detail) entry.x = detail.x
      if ('y' in detail) entry.y = detail.y
      if ('width' in detail) entry.width = detail.width
      if ('height' in detail) entry.height = detail.height
      if ('id' in detail)
        updateNodeId(entry, detail.id ?? target.getAttribute('id'))
      if (detail.content) applyNodeContent(entry, detail.content)
      scheduleNodeRender()
      positionNode(entry)
    }
```

--------------------------------

### Node.js SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Uses `node:http` and `ServerSentEventGenerator` to stream SSE events for patching and redirecting.

```javascript
import { createServer } from "node:http";
import { ServerSentEventGenerator } from "../npm/esm/node/serverSentEventGenerator.js";

const server = createServer(async (req, res) => {

  ServerSentEventGenerator.stream(req, res, async (sse) => {
    sse.patchElements(`
      <div id="indicator">Redirecting in 3 seconds...</div>
    `);

    setTimeout(() => {
      sse.executeScript(`window.location = "/guide"`);
    }, 3000);
  });
});
```

--------------------------------

### Progressive Load HTML Structure

Source: https://data-star.dev/examples/progressive_load

The HTML structure includes a trigger button with Datastar attributes and target containers for progressively loaded content.

```html
 1<div>
 2    <div class="actions">
 3        <button
 4            id="load-button"
 5            data-signals:load-disabled="false"
 6            data-on:click="$loadDisabled=true; @get('/examples/progressive_load/updates')"
 7            data-attr:disabled="$loadDisabled"
 8            data-indicator:progressive-Load
 9        >
10            Load
11        </button>
12        <!-- Indicator element -->
13    </div>
14    <p>
15        Each part is loaded randomly and progressively.
16    </p>
17</div>
18<div id="Load">
19    <header id="header">Welcome to my blog</header>
20    <section id="article">
21        <h4>This is my article</h4>
22        <section id="articleBody">
23            <p>
24                Lorem ipsum dolor sit amet...
25            </p>
26        </section>
27    </section>
28    <section id="comments">
29        <h5>Comments</h5>
30        <p>
31            This is the comments section. It will also be progressively loaded as you scroll down.
32        </p>
33        <ul id="comments-list">
34            <li id="1">
35                <img src="https://avatar.iran.liara.run/username?username=example" alt="Avatar" class="avatar"/>
36                This is a comment...
37            </li>
38            <!-- More comments loaded progressively -->
39        </ul>
40    </section>
41    <div id="footer">Hope you like it</div>
42</div>
```

--------------------------------

### Set HTML Response Headers with DataStar

Source: https://data-star.dev/reference/actions

When returning HTML, set `Content-Type` to `text/html` and use `datastar-selector` and `datastar-mode` headers to specify target elements and patching behavior.

```javascript
response.headers.set('Content-Type', 'text/html')
response.headers.set('datastar-selector', '#my-element')
response.headers.set('datastar-mode', 'inner')
response.body = '<p>New content</p>'
```

--------------------------------

### Datastar Click Event Binding

Source: https://data-star.dev/

Demonstrates binding a click event to an API endpoint using Datastar's data-on:click attribute.

```html
<button data-on:click="@get('/endpoint')">
    Open the pod bay doors, HAL.
</button>

<div id="hal">Waiting for an order...</div>
```

--------------------------------

### String Codec

Source: https://data-star.dev/docs.md

Details on the `string` codec, its normalization pipeline, and available members.

```APIDOC
## `string`

`string` is the most composable codec. It is useful on its own, but it also acts as a normalization pipeline any time a value eventually needs to become text.

Without an explicit `.default(...)`, the zero value is `""`.

| Member | Effect | Example |
|---|---|---|
| `.trim` | Removes surrounding whitespace. | `" Ada "` becomes `"Ada"`. |
| `.upper` | Uppercases the string. | `"ion"` becomes `"ION"`. |
| `.lower` | Lowercases the string. | `"Rocket"` becomes `"rocket"`. |
| `.kebab` | Converts to kebab case. | `"Demo Button"` becomes `"demo-button"`. |
| `.camel` | Converts to camel case. | `"rocket button"` becomes `"rocketButton"`. |
| `.snake` | Converts to snake case. | `"Rocket Button"` becomes `"rocket_button"`. |
| `.pascal` | Converts to Pascal case. | `"rocket button"` becomes `"RocketButton"`. |
| `.title` | Title-cases each word. | `"hello world"` becomes `"Hello World"`. |
| `.prefix(value)` | Adds a prefix if missing. | `"42"` with `prefix('#')` becomes `"#42"`. |
| `.suffix(value)` | Adds a suffix if missing. | `"24"` with `suffix('px')` becomes `"24px"`. |
| `.maxLength(n)` | Truncates to `n` characters. | `"abcdef"` with `maxLength(4)` becomes `"abcd"`. |
| `.default(value)` | Supplies a fallback string. | Missing values can become `"Anonymous"`. |

```javascript
props: ({ string }) => ({
  slug: string.trim.lower.kebab.maxLength(48),
  cssSize: string.trim.suffix('px').default('16px'),
  title: string.trim.title.default('Untitled'),
})
```
```

--------------------------------

### Publish Rocket Manifests

Source: https://data-star.dev/reference/rocket

Posts the full manifest document as JSON to a specified endpoint. Rocket sorts components by tag and includes version and timestamp information.

```APIDOC
## POST /api/rocket/manifests

### Description
Publishes the full manifest document as JSON to the specified endpoint. Rocket sorts components by tag and includes a top-level `version` and `generatedAt` timestamp.

### Method
POST

### Endpoint
`/api/rocket/manifests`

### Parameters
#### Query Parameters
None

#### Request Body
- **manifestDocument** (object) - Required - The full manifest document containing component data.
  - **version** (string) - Top-level version of the manifest.
  - **generatedAt** (string) - Timestamp of when the manifest was generated.
  - **components** (array) - An array of component manifest entries.
    - **tag** (string) - The component's tag name.
    - **props** (object) - Inferred prop metadata.
    - **slots** (array) - Manually documented slot metadata.
    - **events** (array) - Manually documented event metadata.

### Request Example
```json
{
  "version": "1.0.0",
  "generatedAt": "2023-10-27T10:00:00Z",
  "components": [
    {
      "tag": "demo-dialog",
      "props": {
        "title": {"type": "string", "default": "Dialog"},
        "open": {"type": "boolean"}
      },
      "slots": [
        { "name": "default", "description": "Dialog body content." },
        { "name": "footer", "description": "Action row content." }
      ],
      "events": [
        {
          "name": "close",
          "kind": "custom-event",
          "bubbles": true,
          "composed": true,
          "description": "Fired when the dialog requests dismissal."
        }
      ]
    }
  ]
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message of successful publication.

#### Response Example
```json
{
  "message": "Manifest published successfully."
}
```
```

--------------------------------

### Java: Server-Sent Event Generator for SSE

Source: https://data-star.dev/docs.md

This Java snippet shows how to use the ServerSentEventGenerator to send SSE, patching elements and signals to the client.

```java
import starfederation.datastar.utils.ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);

// Patches elements into the DOM.
generator.send(PatchElements.builder()
    .data("<div id=\"question\">What do you put in a toaster?</div>")
    .build()
);

// Patches signals.
generator.send(PatchSignals.builder()
    .data("{\"response\": \"\", \"answer\": \"bread\"}")
    .build()
);
```

--------------------------------

### Patch Signals via Ruby SDK

Source: https://data-star.dev/guide/reactive_signals

Using the Ruby Datastar SDK to patch signals within a streaming response.

```ruby
 1require 'datastar'
 2
 3# Create a Datastar::Dispatcher instance
 4
 5datastar = Datastar.new(request:, response:)
 6
 7# In a Rack handler, you can instantiate from the Rack env
 8# datastar = Datastar.from_rack_env(env)
 9
10# Start a streaming response
11datastar.stream do |sse|
12  # Patches signals
13  sse.patch_signals(hal: 'Affirmative, Dave. I read you.')
14
15  sleep 1
16
17  sse.patch_signals(hal: '...')
18end
```

--------------------------------

### Define Custom Host Properties

Source: https://data-star.dev/reference/rocket

Adds read-only properties or imperative methods to the host element.

```javascript
 1rocket('demo-host-methods', {
  setup({ defineHostProp }) {
    defineHostProp('version', {
      get() {
        return '1'
      },
    })
    defineHostProp('reset', {
      value() {
        console.log('reset')
      },
    })
  },
})
```

--------------------------------

### POST /endpoint

Source: https://data-star.dev/reference/actions

Sends a POST request to the specified URI. Signals are sent as a JSON body by default.

```APIDOC
## POST /endpoint

### Description
Sends a POST request to the backend. Works similarly to the GET method but uses a JSON body for signals.

### Method
POST

### Endpoint
/endpoint

### Request Example
<button data-on:click="@post('/endpoint')"></button>
```

--------------------------------

### Conditional Rendering with Rocket

Source: https://data-star.dev/docs.md

Use `data-if`, `data-else-if`, and `data-else` for conditional rendering. Only one branch is mounted at a time, and inactive branches are removed from the DOM.

```javascript
rocket('demo-status', {
  mode: 'light',
  setup({ $$ }) {
    $$.step = 0
  },
  render: ({ html }) => html`
    <div class="stack gap-2">
      <button type="button" data-on:click="$$step = ($$step + 1) % 3">Next</button>

      <template data-if="$$step === 0">
        <p>Idle</p>
      </template>
      <template data-else-if="$$step === 1">
        <p>Loading</p>
      </template>
      <template data-else>
        <p>Ready</p>
      </template>
    </div>
  `,
})
```

--------------------------------

### TodoMVC HTML Structure

Source: https://data-star.dev/examples/todomvc

The main HTML section for the TodoMVC application, utilizing Datastar attributes for data initialization, event handling, and server-side updates.

```html
 1<section
 2    id="todomvc"
 3    data-init="@get('/examples/todomvc/updates')"
 4>
 5    <header id="todo-header">
 6        <input
 7            type="checkbox"
 8            data-on:click__prevent="@post('/examples/todomvc/-1/toggle')"
 9            data-init="el.checked = false"
10        />
11        <input
12            id="new-todo"
13            type="text"
14            placeholder="What needs to be done?"
15            data-signals:input
16            data-bind:input
17            data-on:keydown="
18                evt.key === 'Enter' && $input.trim() && @patch('/examples/todomvc/-1') && ($input = '');
19            "
20        />
21    </header>
22    <ul id="todo-list">
23        <!-- Todo items are dynamically rendered here -->
24    </ul>
25    <div id="todo-actions">
26        <span>
27            <strong>0</strong> items pending
28        </span>
29        <button class="small info" data-on:click="@put('/examples/todomvc/mode/0')">
30            All
31        </button>
32        <button class="small" data-on:click="@put('/examples/todomvc/mode/1')">
33            Pending
34        </button>
35        <button class="small" data-on:click="@put('/examples/todomvc/mode/2')">
36            Completed
37        </button>
38        <button class="error small" aria-disabled="true">
39            Delete
40        </button>
41        <button class="warning small" data-on:click="@put('/examples/todomvc/reset')">
42            Reset
43        </button>
44    </div>
45</section>
```

--------------------------------

### POST Request

Source: https://data-star.dev/docs.md

Sends a POST request to the backend. Signals are sent as a JSON body by default. Supports options like `openWhenHidden` and `contentType`.

```APIDOC
## POST /endpoint

### Description
Sends a `POST` request to the backend. Works similarly to `@get()` but uses the POST HTTP method. Signals are sent as a JSON body by default.

### Method
POST

### Endpoint
`/endpoint`

### Parameters
#### Query Parameters
- **openWhenHidden** (boolean) - Optional - If true, the SSE connection remains open when the page is hidden.
- **contentType** (string) - Optional - Sets the `Content-Type` header. Can be 'form' for `application/x-www-form-urlencoded`.

### Request Example
```html
<button data-on:click="@post('/endpoint')"></button>
```

### Response
#### Success Response (200)
- **Datastar SSE events** (array) - Zero or more SSE events from the backend.
```

--------------------------------

### Initialize Expressions with data-init

Source: https://data-star.dev/reference/attributes

The `data-init` attribute executes an expression when the element is initialized in the DOM. This can occur on page load, DOM patching, or attribute modification.

```html
<div data-init="$count = 1"></div>
```

--------------------------------

### Dynamic Polling Frequency in Python

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses DatastarResponse and ServerSentEventGenerator to handle the endpoint request.

```python
 1from datastar_py import ServerSentEventGenerator as SSE
 2from datastar_py.sanic import DatastarResponse
 3
 4@app.get("/endpoint")
 5async def endpoint():
 6    current_time = datetime.now()
 7    duration = 5 if current_time.seconds < 50 else 1
 8
 9    return DatastarResponse(SSE.patch_elements(f"""
10        <div id="time" data-on-interval__duration.{duration}s="@get('/endpoint')">
11            {current_time:%Y-%m-%d %H:%M:%S}
12        </div>
13    """))
```

--------------------------------

### Render SVG Components with Rocket

Source: https://data-star.dev/reference/rocket

Uses the svg helper to handle namespaces while maintaining Datastar expression support.

```javascript
 1rocket('demo-meter-ring', {
 2  props: ({ number, string }) => ({
 3    value: number.clamp(0, 100),
 4    stroke: string.default('#0f172a'),
 5  }),
 6  render({ html, svg, props: { value, stroke } }) {
 7    const circumference = 2 * Math.PI * 28
 8
 9    return html`
10      <figure class="stack gap-2">
11        ${svg`
12          <svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">
13            <circle cx="32" cy="32" r="28" fill="none" stroke="#e5e7eb" stroke-width="8"></circle>
14            <circle
15              cx="32"
16              cy="32"
17              r="28"
18              fill="none"
19              stroke="${stroke}"
20              stroke-width="8"
21              stroke-dasharray="${circumference}"
22              stroke-dashoffset="${circumference - (value / 100) * circumference}"
23              transform="rotate(-90 32 32)"></circle>
24          </svg>
25        `}
26        <figcaption>${value}%</figcaption>
27      </figure>
28    `
29  },
30})
```

--------------------------------

### Log Signal Patch Changes

Source: https://data-star.dev/reference/attributes

Use `data-on-signal-patch` to execute an expression when any signal is patched. The `patch` variable is available for details.

```html
<div data-on-signal-patch="console.log('A signal changed!')"></div>
```

```html
<div data-on-signal-patch="console.log('Signal patch:', patch)"></div>
```

--------------------------------

### Kotlin SSE Redirect

Source: https://data-star.dev/how_tos/redirect_the_page_from_the_backend

Employs `ServerSentEventGenerator` to send SSE events for updating the UI and triggering a client-side redirect.

```kotlin
val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements =
        """
        <div id="indicator">Redirecting in 3 seconds...</div>
        """.trimIndent(),
)

Thread.sleep(3 * ONE_SECOND)

generator.executeScript(
    script = "window.location.href = '/success'",
)
```

--------------------------------

### Configure Loading Indicator

Source: https://data-star.dev/guide/backend_requests

Uses the data-indicator attribute to toggle a signal during an active request, useful for showing loading states.

```html
<div id="question"></div>
<button
    data-on:click="@get('/actions/quiz')"
    data-indicator:fetching
>
    Fetch a question
</button>
<div data-class:loading="$fetching" class="indicator"></div>
```

--------------------------------

### Computed Signal Creation

Source: https://data-star.dev/reference/attributes

Create a read-only computed signal named `foo` by combining signals `$bar` and `$baz` using `data-computed`.

```html
1<div data-computed:foo="$bar + $baz"></div>
```

--------------------------------

### JSON and JS Prop API

Source: https://data-star.dev/reference/rocket

Codecs for parsing JSON and JavaScript-like object syntax.

```APIDOC
## json / js

### Description
- **json**: Parses JSON text and clones structured values.
- **js**: Accepts JavaScript-like object syntax for more forgiving parsing.

### Members
- **default(value)**: Supplies a fallback object or array.
```

--------------------------------

### Reading Signals in FastAPI (Python)

Source: https://data-star.dev/guide/backend_requests

Employ the `datastar_response` decorator and `read_signals` utility in FastAPI to asynchronously read frontend signals from an incoming request.

```python
1from datastar_py.fastapi import datastar_response, read_signals
2
3@app.get("/updates")
4@datastar_response
5async def updates(request: Request):
6    # Retrieve a dictionary with the current state of the signals from the frontend
7    signals = await read_signals(request)
```

--------------------------------

### Execute Script via SSE Event

Source: https://data-star.dev/guide/datastar_expressions

Sends a script tag within a datastar-patch-elements SSE event to execute code.

```text
event: datastar-patch-elements
data: elements <div id="hal">
data: elements     <script>alert('This mission is too important for me to allow you to jeopardize it.')</script>
data: elements </div>

```

--------------------------------

### Implement a Counter Component with Rocket

Source: https://data-star.dev/docs.md

Uses typed props for the public API and local signals for state management. Datastar attributes are used directly for event handling and data binding.

```javascript
rocket('demo-stepper', {
  mode: 'light',
  props: ({ number, string }) => ({
    start: number.min(0),
    step: number.min(1).default(1),
    label: string.trim.default('Count'),
  }),
  setup({ $$, props }) {
    $$.count = props.start
  },
  render({ html, props: { label, step } }) {
    return html`
      <section class="stack gap-2">
        <h3>${label}</h3>
        <div class="row gap-2">
          <button data-on:click="$$count -= ${step}" data-attr:disabled="$$count <= 0">-</button>
          <output data-text="$$count"></output>
          <button data-on:click="$$count += ${step}">+</button>
        </div>
      </section>
    `
  },
})
```

--------------------------------

### data-init

Source: https://data-star.dev/docs.md

The `data-init` attribute executes an expression when the attribute is initialized, which can occur on page load, when an element is patched into the DOM, or when the attribute is modified.

```APIDOC
## `data-init`

### Description
Executes an expression when the attribute is initialized.

### Usage
```html
<div data-init="$count = 1"></div>
```

### Modifiers
#### `__delay`
Delays the execution of the event listener.
- `.500ms`: Delay for 500 milliseconds.
- `.1s`: Delay for 1 second.

```html
<div data-init__delay.500ms="$count = 1"></div>
```

#### `__viewtransition`
Wraps the expression in `document.startViewTransition()` if the View Transition API is available.
```

--------------------------------

### @setAll() Action

Source: https://data-star.dev/reference/actions

Sets the value of all matching signals to the provided expression.

```APIDOC
## @setAll()

### Description
Sets the value of all matching signals (or all signals if no filter is used) to the expression provided in the first argument.

### Parameters
- **value** (any) - Required - The value to set the signals to.
- **filter** (object) - Optional - An object with 'include' (RegExp) and 'exclude' (RegExp) properties to match signal paths.

### Request Example
<button data-on:click="@setAll(true, {include: /^foo$/})"></button>
```

--------------------------------

### data-persist

Source: https://data-star.dev/reference

Persists signals in local or session storage.

```APIDOC
## data-persist

### Description
Persists signals in local storage. Useful for storing values between page loads.

### Modifiers
- `__session` - Persists signals in session storage instead of local storage.
```

--------------------------------

### Upload Files with Multipart Form Data

Source: https://data-star.dev/docs.md

Use a form with `enctype="multipart/form-data"` and `@post()` with `contentType: 'form'` to upload files.

```html
<form enctype="multipart/form-data">
    <input type="file" name="file" />
    <button data-on:click="@post('/endpoint', {contentType: 'form'})></button>
</form>
```

--------------------------------

### Asynchronous External Script Integration

Source: https://data-star.dev/docs.md

Handles asynchronous operations by dispatching a custom event that Datastar listens for to update signals.

```html
<div data-signals:result>
    <input data-bind:foo
           data-on:input="myfunction(el, $foo)"
           data-on:mycustomevent__window="$result = evt.detail.value"
    >
    <span data-text="$result"></span>
</div>
```

```javascript
async function myfunction(element, data) {
    const value = await new Promise((resolve) => {
        setTimeout(() => resolve(`You entered: ${data}`), 1000);
    });
    element.dispatchEvent(
        new CustomEvent('mycustomevent', {detail: {value}})
    );
}
```

--------------------------------

### @peek() Action

Source: https://data-star.dev/reference/actions

Allows accessing signals without subscribing to their changes in expressions.

```APIDOC
## @peek()

### Description
Allows accessing signals without subscribing to their changes in expressions. The expression will not be re-evaluated when the signal accessed via @peek() changes.

### Parameters
- **callable** (function) - Required - A function that returns the value of the signal to be accessed.

### Request Example
<div data-text="$foo + @peek(() => $bar)"></div>
```

--------------------------------

### Implement Event Bubbling with Datastar

Source: https://data-star.dev/examples/event_bubbling

Uses a single data-on:click listener on a parent container to handle clicks for multiple child buttons. The logic uses evt.target.closest to identify the specific button clicked even if a nested element is the target.

```html
 1<div id="demo">
 2  Key pressed: <span data-text="$key"></span>
 3  <div id="event-bubbling-container" data-on:click="$key = evt.target.closest('button[data-id]')?.dataset.id ?? $key">
 4    <button data-id="KEY ELSE" class="gray">KEY<br/>ELSE</button>
 5    <button data-id="CM">CM</button>
 6    <button data-id="OM">OM</button>
 7    <button data-id="FETCH">FETCH</button>
 8    <button data-id="SET">SET</button>
 9    <button data-id="EXEC">EXEC</button>
10    <button data-id="TEST ALARM" class="gray">TEST<br/>ALARM</button>
11    <button data-id="3">3</button>
12    <button data-id="2">2</button>
13    <button data-id="1">1</button>
14    <button data-id="ENTER">ENTER</button>
15    <button data-id="CLEAR">CLEAR</button>
16  </div>
17</div>
18
19<style>
20  #event-bubbling-container {
21    pointer-events: none;
22
23    button {
24      user-select: none;
25
26      * {
27        pointer-events: none;
28        user-select: none;
29      }
30    }
31  }
32</style>
```

--------------------------------

### Define Attribute Evaluation Order

Source: https://data-star.dev/reference/attributes

Demonstrates ensuring an indicator signal is created before a fetch request is initialized by ordering attributes.

```html
<div data-indicator:fetching data-init="@get('/endpoint')"></div>
```

--------------------------------

### Array Prop API

Source: https://data-star.dev/reference/rocket

The array codec supports homogeneous arrays and tuples.

```APIDOC
## array

### Description
Creates a homogeneous array with one codec or a tuple with multiple codecs.

### Forms
- **array(codec)**: Every item is decoded with the same codec.
- **array(codecA, codecB, codecC)**: Tuple where each position has its own codec.
```

--------------------------------

### Create and patch signals with data-signals

Source: https://data-star.dev/docs.md

Use data-signals to patch signals into the existing signals. Hyphenated names are converted to camel case. Signals can be nested using dot-notation or objects.

```html
<div data-signals:foo-bar="1"></div>
```

```html
<div data-signals:form.baz="2"></div>
```

```html
<div data-signals:foo-bar="1"
     data-text="$fooBar"
></div>
```

```html
<div data-signals="{fooBar: 1, form: {baz: 2}}"></div>
```

--------------------------------

### Patch DOM elements with PHP

Source: https://data-star.dev/guide/getting_started

Uses the ServerSentEventGenerator to stream HTML updates to the client.

```php
use starfederation\datastar\ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
$sse = new ServerSentEventGenerator();

// Patches elements into the DOM.
$sse->patchElements(
    '<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>'
);

sleep(1);

$sse->patchElements(
    '<div id="hal">Waiting for an order...</div>'
);
```

--------------------------------

### Listen for Enter Keydown Event Globally

Source: https://data-star.dev/how_tos/bind_keydown_events_to_specific_keys

Conditionally trigger an alert only when the 'Enter' key is pressed using `evt.key`. The `evt` variable provides access to the event object.

```html
<div data-on:keydown__window="evt.key === 'Enter' && alert('Key pressed')"></div>
```

--------------------------------

### Copy Text to Clipboard with @clipboard()

Source: https://data-star.dev/reference/actions

Use the `@clipboard()` action to copy plain text or Base64 encoded text to the user's clipboard.

```html
<!-- Copy plain text -->
<button data-on:click="@clipboard('Hello, world!')"></button>

<!-- Copy base64 encoded text (will decode before copying) -->
<button data-on:click="@clipboard('SGVsbG8sIHdvcmxkIQ==', true)"></button>
```

--------------------------------

### Display Signal Value with Datastar Expression

Source: https://data-star.dev/docs.md

Renders the value of a 'foo' signal in a div using a Datastar expression. The signal is initialized with the value '1'.

```html
<div data-signals:foo="1">
    <div data-text="$foo"></div>
</div>
```

--------------------------------

### Persist Signal in Session Storage with Custom Key

Source: https://data-star.dev/reference/attributes

Persists signals using a custom key ('mykey') in session storage instead of local storage. This data will be cleared when the browser session ends.

```html
<!-- Persists signals using a custom key `mykey` in session storage -->
<div data-persist:mykey__session></div>
```

--------------------------------

### Executing Scripts via SSE Events

Source: https://data-star.dev/docs.md

Scripts can be executed by embedding them within datastar-patch-elements SSE events or by appending them to the document body.

```text
event: datastar-patch-elements
data: elements <div id="hal">
data: elements     <script>alert('This mission is too important for me to allow you to jeopardize it.')</script>
data: elements </div>
```

```text
event: datastar-patch-elements
data: mode append
data: selector body
data: elements <script>alert('This mission is too important for me to allow you to jeopardize it.')</script>
```

--------------------------------

### PHP: Server-Sent Event Generator for SSE

Source: https://data-star.dev/docs.md

This PHP snippet illustrates using the ServerSentEventGenerator to patch elements and signals for Server-Sent Events.

```php
use starfederation\datastar\ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
$sse = new ServerSentEventGenerator();

// Patches elements into the DOM.
$sse->patchElements(
    '<div id="question">What do you put in a toaster?</div>'
);

// Patches signals.
$sse->patchSignals(['response' => '', 'answer' => 'bread']);
```

--------------------------------

### data-class with Multiple Classes and Expressions

Source: https://data-star.dev/reference

Apply multiple classes to an element based on different expressions. Each key-value pair in the object defines a class name and its corresponding condition.

```html
<div data-class="{success: $foo != '', 'font-bold': $foo == 'strong'}"></div>
```

--------------------------------

### Web Component Integration

Source: https://data-star.dev/docs.md

Uses custom elements to encapsulate logic, passing data via attributes and receiving updates through custom events.

```html
<div data-signals:result="''">
    <input data-bind:foo />
    <my-component
        data-attr:src="$foo"
        data-on:mycustomevent="$result = evt.detail.value"
    ></my-component>
    <span data-text="$result"></span>
</div>
```

```javascript
class MyComponent extends HTMLElement {
    static get observedAttributes() {
        return ['src'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        const value = `You entered: ${newValue}`;
        this.dispatchEvent(
            new CustomEvent('mycustomevent', {detail: {value}})
        );
    }
}

customElements.define('my-component', MyComponent);
```

--------------------------------

### Attach event listener with data-on

Source: https://data-star.dev/docs.md

Use data-on to attach an event listener and run an expression when the event is triggered. Works with any valid event name, including custom events. Event names are converted to kebab case.

```html
<input data-bind:foo />
<button data-on:click="$foo = ''">
    Reset
</button>
```

```html
<div data-on:my-event="$foo = ''">
    <input data-bind:foo />
</div>
```

--------------------------------

### Two-Way Binding for Nested Signals

Source: https://data-star.dev/guide/backend_requests

Utilize `data-bind` with dot notation to establish two-way binding for nested signals, synchronizing input elements with signal state.

```html
1<input data-bind:foo.bar />
```

--------------------------------

### Rocket Component Implementation

Source: https://data-star.dev/examples/rocket_copy_button

Defines the copy-button component using the Datastar rocket function, managing clipboard interaction and visual state.

```javascript
 1import { rocket } from 'datastar'
 2
 3rocket('copy-button', {
 4  mode: 'light',
 5  props: ({ string }) => ({
 6    code: string,
 7  }),
 8  setup({ $$, cleanup, host, props }) {
 9    $$.copied = false
10    let timer = 0
11
12    host.addEventListener('click', onClick)
13
14    cleanup(() => {
15      clearTimeout(timer)
16      host.removeEventListener('click', onClick)
17    })
18
19    async function onClick(evt) {
20      if (!(evt.target instanceof Element)) return
21      if (!evt.target.closest('button.copy-button')) return
22      await navigator.clipboard.writeText(props.code ?? '')
23      $$.copied = true
24      clearTimeout(timer)
25      timer = setTimeout(() => {
26        $$.copied = false
27      }, 2000)
28    }
29  },
30  render: ({ html }) => html`
31    <div class="copy-button-wrapper">
32      <button
33        class="copy-button small"
34        type="button"
35        title="Copy code"
36      >
37        <iconify-icon
38          noobserver
39          data-attr:icon="'pixelarticons:' + ($$copied ? 'section-copy' : 'copy')"
40        ></iconify-icon>
41      </button>
42      <span data-show="$$copied" class="copy-popover">Copied!</span>
43    </div>
44  `,
45})
```

--------------------------------

### rocket(tag, options)

Source: https://data-star.dev/reference/rocket

Registers a new custom element with the browser. The tag must contain a hyphen and be unique.

```APIDOC
## rocket(tag, options)

### Description
Registers a custom web component using the Datastar Rocket API. This function defines the component's behavior, props, and rendering logic.

### Parameters
- **tag** (string) - Required - The custom element tag name (must contain a hyphen).
- **options** (RocketDefinition) - Optional - An object defining the component lifecycle, props, and rendering behavior.

### Request Example
```javascript
rocket('demo-user-card', {
  props: ({ string }) => ({
    name: string.default('Anonymous'),
  }),
  render({ html, props: { name } }) {
    return html`<p>${name}</p>`
  },
})
```
```

--------------------------------

### SortableJS Integration with Data-Star

Source: https://data-star.dev/examples/sortable

This snippet initializes SortableJS on a container and dispatches a custom 'reordered' event when the list order changes. The event detail includes the old and new positions, which are used to update a Data-Star signal.

```html
<div data-signals:order-info="'Initial order'" data-text="$orderInfo"></div>
<div id="sortContainer" data-on:reordered="$orderInfo = event.detail.orderInfo">
    <button>Item 1</button>
    <button>Item 2</button>
    <button>Item 3</button>
    <button>Item 4</button>
    <button>Item 5</button>
</div>

<script type="module">
    import Sortable from 'https://cdn.jsdelivr.net/npm/sortablejs/+esm'
    new Sortable(sortContainer, {
        animation: 150,
        ghostClass: 'opacity-25',
        onEnd: (evt) => {
            sortContainer.dispatchEvent(
                new CustomEvent('reordered', {detail: {
                    orderInfo: `Moved from position ${evt.oldIndex + 1} to ${evt.newIndex + 1}`
                }})
            )
        }
    })
</script>
```

--------------------------------

### Perform PATCH request

Source: https://data-star.dev/reference/actions

Sends a PATCH request to the backend.

```html
<button data-on:click="@patch('/endpoint')"></button>
```

--------------------------------

### Stream SSE events in Rust

Source: https://data-star.dev/guide/backend_requests

Uses the Sse wrapper and async_stream to yield patch events.

```rust
 1use datastar::prelude::*;
 2use async_stream::stream;
 3
 4Sse(stream! {
 5    // Patches elements into the DOM.
 6    yield PatchElements::new("<div id='question'>What do you put in a toaster?</div>").into();
 7
 8    // Patches signals.
 9    yield PatchSignals::new("{response: '', answer: 'bread'}").into();
10})
```

--------------------------------

### @toggleAll() Action

Source: https://data-star.dev/reference/actions

Toggles the boolean value of all matching signals.

```APIDOC
## @toggleAll()

### Description
Toggles the boolean value of all matching signals (or all signals if no filter is used).

### Parameters
- **filter** (object) - Optional - An object with 'include' (RegExp) and 'exclude' (RegExp) properties to match signal paths.

### Request Example
<button data-on:click="@toggleAll({include: /^is/})"></button>
```

--------------------------------

### Persist signals to storage with data-persist

Source: https://data-star.dev/docs.md

Saves signals to local or session storage, with options for filtering keys and custom storage identifiers.

```html
<div data-persist></div>
```

```html
<div data-persist="{include: /foo/, exclude: /bar/}"></div>
```

```html
<div data-persist:mykey></div>
```

```html
<!-- Persists signals using a custom key `mykey` in session storage -->
<div data-persist:mykey__session></div>
```

--------------------------------

### List Rendering with data-for

Source: https://data-star.dev/reference/rocket

Iterates over collections to render repeated DOM elements. Supports custom aliases for items and indices.

```javascript
 1rocket('demo-letter-list', {
 2  mode: 'light',
 3  setup({ $$ }) {
 4    $$.letters = ['A', 'B', 'C']
 5  },
 6  render: ({ html }) => html`
 7    <ul>
 8      <template data-for="letter, row in $$letters">
 9        <li>
10          <strong data-text="row + 1"></strong>
11          <span data-text="letter"></span>
12        </li>
13      </template>
14    </ul>
15  `,
16})
```

--------------------------------

### Rocket Component Manifest Structure

Source: https://data-star.dev/docs.md

Defines the structure for documenting component slots and events. Use this to provide metadata that Rocket cannot infer from the DOM alone.

```typescript
manifest?: {
  slots?: Array<{
    name: string
    description?: string
  }>
  events?: Array<{
    name: string
    kind?: 'event' | 'custom-event'
    bubbles?: boolean
    composed?: boolean
    description?: string
  }>
}
```

--------------------------------

### Datastar Error Handling

Source: https://data-star.dev/docs.md

Explains Datastar's built-in error handling for runtime errors, including console logs and context-aware error pages.

```APIDOC
## Error Handling

Datastar has built-in error handling and reporting for runtime errors. When a data attribute is used incorrectly, for example `data-text-foo`, the following error message is logged to the browser console.

```
Uncaught datastar runtime error: textKeyNotAllowed
More info: https://data-star.dev/errors/key_not_allowed?metadata=%7B%22plugin%22%3A%7B%22name%22%3A%22text%22%2C%22type%22%3A%22attribute%22%7D%2C%22element%22%3A%7B%22id%22%3A%22%22%2C%22tag%22%3A%22DIV%22%7D%2C%22expression%22%3A%7B%22rawKey%22%3A%22textFoo%22%2C%22key%22%3A%22foo%22%2C%22value%22%3A%22%22%2C%22fnContent%22%3A%22%22%7D%7D
Context: {
    "plugin": {
        "name": "text",
        "type": "attribute"
    },
    "element": {
        "id": "",
        "tag": "DIV"
    },
    "expression": {
        "rawKey": "textFoo",
        "key": "foo",
        "value": "",
        "fnContent": ""
    }
}
```

The “More info” link takes you directly to a context-aware error page that explains the error and provides correct sample usage. See [the error page for the example above](https://data-star.dev/errors/key_not_allowed?metadata=%7B%22plugin%22%3A%7B%22name%22%3A%22text%22%2C%22type%22%3A%22attribute%22%7D%2C%22element%22%3A%7B%22id%22%3A%22%22%2C%22tag%22%3A%22DIV%22%7D%2C%22expression%22%3A%7B%22rawKey%22%3A%22textFoo%22%2C%22key%22%3A%22foo%22%2C%22value%22%3A%22%22%2C%22fnContent%22%3A%22%22%7D%7D), and all available error messages in the sidebar menu.
```

--------------------------------

### Send SSE Events with Go Datastar SSE

Source: https://data-star.dev/guide/backend_requests

Use the SSE object in Go to patch elements and signals. Ensure signals are sent as byte slices.

```go
sse.PatchElements(`<div id="question">...</div>`)
sse.PatchElements(`<div id="instructions">...</div>`)
sse.PatchSignals([]byte(`{answer: '...', prize: '...'}`))
```

--------------------------------

### HTML for Color Throb Animation

Source: https://data-star.dev/examples/animations

This HTML snippet demonstrates a div with a stable ID that can be used with CSS transitions for color throbbing effects. Ensure the ID remains consistent across content swaps for Datastar to apply transitions.

```html
<div
    id="color-throb"
    style="color: var(--blue-8); background-color: var(--orange-5);"
>
    blue on orange
</div>
```

--------------------------------

### Create Animated SVG Morph Sequence

Source: https://data-star.dev/examples/svg_morphing

This Go code creates an animation effect by performing a sequence of SVG morphs with delays. Each `sse.PatchElements` call updates the SVG, and `time.Sleep` controls the timing between updates.

```go
1svgMorphingRouter.Get("/animated_morph", func(w http.ResponseWriter, r *http.Request) {
2    sse := datastar.NewSSE(w, r)
3
4    // First morph
5    sse.PatchElements(`<svg id="animated-demo"><circle cx="50" cy="50" r="30" fill="red" /></svg>`)
6    time.Sleep(500 * time.Millisecond)
7
8    // Second morph
9    sse.PatchElements(`<svg id="animated-demo"><circle cx="50" cy="50" r="45" fill="orange" /></svg>`)
10    time.Sleep(500 * time.Millisecond)
11
12    // Third morph
13    sse.PatchElements(`<svg id="animated-demo"><circle cx="50" cy="50" r="60" fill="yellow" /></svg>`)
14    time.Sleep(500 * time.Millisecond)
15
16    // Reset
17    sse.PatchElements(`<svg id="animated-demo"><circle cx="50" cy="50" r="20" fill="green" /></svg>`)
18})

```

--------------------------------

### Dynamic Polling Frequency in Ruby

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses Datastar to patch elements with a dynamic duration fragment.

```ruby
 1datastar = Datastar.new(request:, response:)
 2
 3now = Time.now
 4current_time = now.strftime('%Y-%m-%d %H:%M:%S')
 5current_seconds = now.strftime('%S').to_i
 6duration = current_seconds < 50 ? 5 : 1
 7
 8datastar.patch_elements <<~FRAGMENT
 9    <div id="time"
10         data-on-interval__duration.#{duration}s="@get('/endpoint')"
11    >
12        #{current_time}
13    </div>
14FRAGMENT
```

--------------------------------

### observeProps(callback, propNames?)

Source: https://data-star.dev/reference/rocket

Watches for changes in component props to trigger imperative side effects.

```APIDOC
## observeProps(callback, propNames?)

### Description
Registers a callback to be executed when specific props change. The callback receives the full normalized props object and a changes object.

### Parameters
- **callback** (function) - Required - Function called with `(props, changes)`.
- **propNames** (Array<string>) - Optional - List of specific props to watch. If omitted, all props are watched.
```

--------------------------------

### Implement an Alert Action Plugin

Source: https://data-star.dev/examples/custom_plugin

Define a custom action plugin named 'alert' that triggers a JavaScript alert with a given value. This action can be invoked using the '@alert' syntax.

```javascript
1action({
    name: 'alert',
    apply(ctx, value) {
        alert(value)
    }
})
```

--------------------------------

### Stream SSE events in Java

Source: https://data-star.dev/guide/backend_requests

Uses HttpServletResponseAdapter and ServerSentEventGenerator to send patch events.

```java
 1import starfederation.datastar.utils.ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
 5ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);
 6
 7// Patches elements into the DOM.
 8generator.send(PatchElements.builder()
 9    .data("<div id=\"question\">What do you put in a toaster?</div>")
10    .build()
11);
12
13// Patches signals.
14generator.send(PatchSignals.builder()
15    .data("{\"response\": \"\", \"answer\": \"\"}")
16    .build()
17);
```

--------------------------------

### Send POST Request with Datastar

Source: https://data-star.dev/guide/backend_requests

Use the @post() directive to send data to a server endpoint for processing via a POST request.

```html
<button data-on:click="@post('/actions/quiz')">
    Submit answer
</button>
```

--------------------------------

### Observe Property Changes

Source: https://data-star.dev/reference/rocket

Performs imperative updates when specific component properties change.

```javascript
 1rocket('demo-video-frame', {
  props: ({ string, number }) => ({
    src: string.trim,
    currentTime: number.min(0),
  }),
  mode: 'light',
  renderOnPropChange: false,
  onFirstRender({ refs, observeProps }) {
    observeProps((props, changes) => {
      if (!(refs.video instanceof HTMLVideoElement)) {
        return
      }
      if ('src' in changes) {
        refs.video.src = props.src
      }
      if ('currentTime' in changes) {
        refs.video.currentTime = props.currentTime
      }
    })
  },
  render({ html, props: { src } }) {
    return html`<video data-ref:video controls src="${src}"></video>`
  },
})
```

--------------------------------

### Synchronous External Script Integration

Source: https://data-star.dev/docs.md

Uses a direct function call within a data-on attribute to process input and return a result.

```html
<div data-signals:result>
    <input data-bind:foo
        data-on:input="$result = myfunction($foo)"
    >
    <span data-text="$result"></span>
</div>
```

```javascript
function myfunction(data) {
    return `You entered: ${data}`;
}
```

--------------------------------

### JS Object Prop Decoders

Source: https://data-star.dev/reference/rocket

Parse JavaScript-like object syntax for more flexible configuration literals.

```javascript
props: ({ js }) => ({
  config: js.default(() => ({
    scale: 1,
    axis: { x: true, y: true },
  })),
})
```

--------------------------------

### Patching signals with data-signals

Source: https://data-star.dev/reference

Use data-signals to add, update, or remove signals. Values defined later in the DOM tree override earlier ones.

```html
<div data-signals:foo="1"></div>
```

```html
<div data-signals:foo.bar="1"></div>
```

```html
<div data-signals="{foo: {bar: 1, baz: 2}}"></div>
```

```html
<div data-signals="{foo: null}"></div>
```

--------------------------------

### DRY Button Clicks with Templating Loop

Source: https://data-star.dev/how_tos/keep_datastar_code_dry

Further reduces repetition by using a templating loop to generate multiple buttons, each with the same backend action. This is useful for dynamic lists of items.

```html
{% set labels = ['Click me', 'No, click me!', 'Click us all!'] %}
{% for label in labels %}
    <button data-on:click="@get('/endpoint')">{{ label }}</button>
{% endfor %}
```

--------------------------------

### Sync Markers with Clustering Logic

Source: https://data-star.dev/examples/rocket_openfreemap

Synchronizes map markers with clustering configuration. It determines whether to enable clustering based on zoom level and configuration, and either ensures cluster layers are set up or removes them to render individual DOM markers.

```javascript
const syncMarkers = () => {
      if (!map) return
      const clusterConfig = {
        enabled: props.cluster === true,
        maxZoom: Math.round(props.clusterMaxZoom),
        radius: Math.round(props.clusterRadius),
      }
      const clusterConfigKey = JSON.stringify([
        clusterConfig.enabled,
        clusterConfig.maxZoom,
        clusterConfig.radius,
      ])
      const zoom = map.getZoom()
      const shouldCluster =
        clusterConfig.enabled &&
        markerEntries.length > 1 &&
        (Number.isFinite(zoom) ? zoom : clusterConfig.maxZoom) <=
          clusterConfig.maxZoom

      if (shouldCluster) {
        if (!map.isStyleLoaded()) return
        if (clusterConfigKey !== prevAppliedClusterConfig) {
          removeClusterLayersAndSource()
          prevAppliedClusterConfig = clusterConfigKey
        }
        ensureClusterLayersAndData(clusterConfig)
        removeDomMarkers()
        return
      }

      removeClusterLayersAndSource()
      prevAppliedClusterConfig = clusterConfigKey
      renderDomMarkers()
    }
```

--------------------------------

### Fluent Codec Pattern for Prop Definition

Source: https://data-star.dev/reference/rocket

Define component props using a fluent API for codecs, chaining transformations like trim, lower, kebab case, clamping, and type-specific decoding. Defaults can be set at any point in the chain.

```javascript
props: ({ string, number, object, array, oneOf }) => ({
  slug: string.trim.lower.kebab.maxLength(48),
  progress: number.clamp(0, 100).step(5),
  theme: oneOf('light', 'dark', 'system').default('system'),
  tags: array(string.trim.lower),
  profile: object({
    name: string.trim.default('Anonymous'),
    age: number.min(0),
  }),
})
```

--------------------------------

### Rust SSE Stream with Patch Signals

Source: https://data-star.dev/guide/reactive_signals

Implement a Server-Sent Events stream in Rust using `async_stream`. This snippet shows how to yield `PatchSignals` with JSON payloads and includes a delay between signals.

```rust
use async_stream::stream;
use datastar::prelude::*;
use std::thread;
use std::time::Duration;

Sse(stream! {
    // Patches signals.
    yield PatchSignals::new("{hal: 'Affirmative, Dave. I read you.'}").into();

    thread::sleep(Duration::from_secs(1));

    yield PatchSignals::new("{hal: '...'} ").into();
})
```

--------------------------------

### Implement an Alert Attribute Plugin

Source: https://data-star.dev/examples/custom_plugin

Implement a custom attribute plugin named 'alert'. This plugin attaches a click event listener to an element, triggering an alert with the returned value when clicked. It requires a 'denied' key with a 'must' value and returns a value.

```javascript
1attribute({
    name: 'alert',
    requirement: {
        key: 'denied',
        value: 'must',
    },
    returnsValue: true,
    apply({ el, rx }) {
        const callback = () => alert(rx())
        el.addEventListener('click', callback)
        return () => el.removeEventListener('click', callback)
    }
})
```

--------------------------------

### Register Rocket Component with Manifest

Source: https://data-star.dev/reference/rocket

Register a Rocket component, providing props, manifest details for slots and events, and the render function. The manifest includes descriptions for slots and custom events.

```javascript
import { publishRocketManifests, rocket } from '/bundles/datastar-pro.js'

rocket('demo-dialog', {
  props: ({ string, bool }) => ({
    title: string.default('Dialog'),
    open: bool,
  }),
  manifest: {
    slots: [
      { name: 'default', description: 'Dialog body content.' },
      { name: 'footer', description: 'Action row content.' },
    ],
    events: [
      {
        name: 'close',
        kind: 'custom-event',
        bubbles: true,
        composed: true,
        description: 'Fired when the dialog requests dismissal.',
      },
    ],
  },
  render({ html, props: { title, open } }) {
    return html`
      <section data-show="${open}">
        <header>${title}</header>
        <slot></slot>
        <footer><slot name="footer"></slot></footer>
      </section>
    `
  },
})

const manifest = customElements.get('demo-dialog')?.manifest?.()

await publishRocketManifests({
  endpoint: '/api/rocket/manifests',
})
```

--------------------------------

### Patch DOM elements with Rust

Source: https://data-star.dev/guide/getting_started

Uses the datastar crate to yield patch events within an async stream.

```rust
use async_stream::stream;
use datastar::prelude::*;
use std::thread;
use std::time::Duration;

Sse(stream! {
    // Patches elements into the DOM.
    yield PatchElements::new("<div id='hal'>I’m sorry, Dave. I’m afraid I can’t do that.</div>").into();

    thread::sleep(Duration::from_secs(1));

    yield PatchElements::new("<div id='hal'>Waiting for an order...</div>").into();
})
```

--------------------------------

### Patching Elements with Java SDK

Source: https://data-star.dev/guide/getting_started

Use the ServerSentEventGenerator to send PatchElements builder objects to the client.

```java
 1import starfederation.datastar.utils.ServerSentEventGenerator;
 2
 3// Creates a new `ServerSentEventGenerator` instance.
 4AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
 5ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);
 6
 7// Patches elements into the DOM.
 8generator.send(PatchElements.builder()
 9    .data("<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
10    .build()
11);
12
13Thread.sleep(1000);
14
15generator.send(PatchElements.builder()
16    .data("<div id=\"hal\">Waiting for an order...</div>")
17    .build()
18);
```

--------------------------------

### Backend Response for Interval Updates

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

A sample `datastar-patch-elements` event response from the backend. This event contains the updated HTML for the specified element, ensuring the frontend reflects the latest data.

```text
event: datastar-patch-elements
data: elements <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
data: elements     {{ now }}
data: elements </div>

```

--------------------------------

### Persist Filtered Signals in Local Storage

Source: https://data-star.dev/reference/attributes

Persists signals in local storage, filtering them based on provided include and exclude regular expressions. This allows selective persistence of signal values.

```html
<div data-persist="{include: /foo/, exclude: /bar/}"></div>
```

--------------------------------

### Enable Node Dragging

Source: https://data-star.dev/examples/rocket_flow

Attaches event listeners to enable dragging functionality for a flow node. Requires 'pointermove', 'pointerup', and 'pointercancel' event handlers.

```javascript
        const move = (event) => {
          if (event.pointerId !== pointerId) return
          entry.x =
            drag.startX +
            (event.clientX - drag.startClientX) *
              (metrics.worldWidth / metrics.screenWidth)
          entry.y =
            drag.startY +
            (event.clientY - drag.startClientY) *
              (metrics.worldHeight / metrics.screenHeight)
          positionNode(entry)
          emitNodeEvent(entry, 'flow-node-drag', {
            pointerId,
            origin: { x: drag.startX, y: drag.startY },
          })
        }

        const finish = (event, type) => {
          if (event.pointerId !== pointerId) return
          activeNodeDrags.delete(pointerId)
          try {
            entry.group.releasePointerCapture(pointerId)
          } catch {}
          entry.group.classList.remove('is-dragging')
          entry.group.style.cursor = 'grab'
          root.removeEventListener('pointermove', move, true)
          root.removeEventListener('pointerup', end, true)
          root.removeEventListener('pointercancel', cancel, true)
          if (type === 'cancel') {
            emitNodeEvent(entry, 'flow-node-drag-cancel', {
              pointerId,
              origin: { x: drag.startX, y: drag.startY },
            })
            return
          }
          const detail = {
            pointerId,
            origin: { x: drag.startX, y: drag.startY },
            source: 'drag',
            x: entry.x,
            y: entry.y,
          }
          emitNodeEvent(entry, 'flow-node-drag-end', detail)
          try {
            entry.el.setAttribute('x', String(entry.x))
            entry.el.setAttribute('y', String(entry.y))
          } catch {}
          emitNodeEvent(entry, 'flow-node-update', detail)
        }

        const end = (event) => finish(event, 'end')
        const cancel = (event) => finish(event, 'cancel')
        root.addEventListener('pointermove', move, true)
        root.addEventListener('pointerup', end, true)
        root.addEventListener('pointercancel', cancel, true)
```

--------------------------------

### Yield SSE Events in Ruby

Source: https://data-star.dev/guide/backend_requests

Yield patch elements and patch signals in Ruby using their respective builder classes.

```ruby
yield PatchElements::new("<div id='question'>...</div>").into()
yield PatchElements::new("<div id='instructions'>...</div>").into()
yield PatchSignals::new("{answer: '...', prize: '...'}").into()
```

--------------------------------

### data-on-resize

Source: https://data-star.dev/reference

Runs an expression whenever an element’s dimensions change.

```APIDOC
## data-on-resize

### Description
Runs an expression whenever an element’s dimensions change.

### Modifiers
- `__debounce` - Debounce the event listener.
- `__throttle` - Throttle the event listener.
```

--------------------------------

### Execute expressions on requestAnimationFrame with data-on-raf

Source: https://data-star.dev/docs.md

Runs an expression on every animation frame, with optional throttling modifiers.

```html
<div data-on-raf="$count++"></div>
```

```html
<div data-on-raf__throttle.10ms="$count++"></div>
```

--------------------------------

### Toggle classes with data-class

Source: https://data-star.dev/guide/reactive_signals

Use data-class to add or remove CSS classes based on expression evaluation. Class names are converted to kebab case.

```html
1<input data-bind:foo-bar />
2<button data-class:success="$fooBar != ''">
3    Save
4</button>
```

```html
1<button data-class:font-bold="$fooBar == 'strong'">
2    Save
3</button>
```

```html
1<button data-class="{success: $fooBar != '', 'font-bold': $fooBar == 'strong'}">
2    Save
3</button>
```

--------------------------------

### Flow Component CSS Styles

Source: https://data-star.dev/examples/rocket_flow

Base styles for the flow host, SVG container, and edge path rendering.

```css
    <style>
      :host {
        display: block;
        position: relative;
      }

      .flow-root {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
      }

      svg.flow-svg {
        display: block;
        width: 100%;
        height: 100%;
        cursor: grab;
        background: #eef2ff;
        touch-action: none;
        user-select: none;
      }

      svg.flow-svg.is-dragging {
        cursor: grabbing;
      }

      .flow-edge path {
        stroke: #64748b;
        stroke-width: 1.5;
        fill: none;
        stroke-linecap: round;
        stroke-linejoin: round;
      }

      .flow-edge path.is-animated {
        stroke-dasharray: 6 4;
        animation: flow-edge-dash 1.2s linear infinite;
      }

      .flow-edge text {
        fill: #475569;
        font-size: 12px;
        font-weight: 500;
```

--------------------------------

### data-computed for Simple Expression

Source: https://data-star.dev/reference

Create a read-only computed signal from a simple expression. The signal updates automatically when dependencies change.

```html
<div data-computed:foo="$bar + $baz"></div>
```

--------------------------------

### Patching multiple signals with data-signals

Source: https://data-star.dev/reference/attributes

Patch multiple signals using a JavaScript object notation or JSON within the `data-signals` attribute.

```html
<div data-signals="{foo: {bar: 1, baz: 2}}"></div>
```

--------------------------------

### Patching Elements with C# SDK

Source: https://data-star.dev/guide/getting_started

Use the IDatastarService to perform asynchronous element patching within an ASP.NET Core endpoint.

```csharp
 1using StarFederation.Datastar.DependencyInjection;
 2
 3// Adds Datastar as a service
 4builder.Services.AddDatastar();
 5
 6app.MapGet("/", async (IDatastarService datastarService) =>
 7{
 8    // Patches elements into the DOM.
 9    await datastarService.PatchElementsAsync(@"<div id=""hal"">I’m sorry, Dave. I’m afraid I can’t do that.</div>");
10
11    await Task.Delay(TimeSpan.FromSeconds(1));
12
13    await datastarService.PatchElementsAsync(@"<div id=""hal"">Waiting for an order...</div>");
14});
```

--------------------------------

### Interpolate Value Between Ranges with @fit()

Source: https://data-star.dev/reference/actions

The `@fit()` action linearly interpolates a value from one range to another, with options to clamp the result within the new range or round it to the nearest integer.

```html
<!-- Convert a 0-100 slider to 0-255 RGB value -->
<div>
    <input type="range" min="0" max="100" value="50" data-bind:slider-value>
    <div data-computed:rgb-value="@fit($sliderValue, 0, 100, 0, 255)">
        RGB Value: <span data-text="$rgbValue"></span>
    </div>
</div>

<!-- Convert Celsius to Fahrenheit -->
<div>
    <input type="number" data-bind:celsius value="20" />
    <div data-computed:fahrenheit="@fit($celsius, 0, 100, 32, 212)">
        <span data-text="$celsius"></span>°C = <span data-text="$fahrenheit.toFixed(1)"></span>°F
    </div>
</div>

<!-- Map mouse position to element opacity (clamped) -->
<div
    data-signals:mouse-x="0"
    data-computed:opacity="@fit($mouseX, 0, window.innerWidth, 0, 1, true)"
    data-on:mousemove__window="$mouseX = evt.clientX"
    data-attr:style="'opacity: ' + $opacity"
>
    Move your mouse horizontally to change opacity
</div>
```

--------------------------------

### data-indicator

Source: https://data-star.dev/reference/attributes

Creates a signal that tracks the status of a fetch request, useful for loading indicators.

```APIDOC
## data-indicator

### Description
Creates a signal and sets its value to `true` while a fetch request is in flight, otherwise `false`. The signal can be used to show a loading indicator or disable elements.

### Modifiers
- `__case`: Converts the casing of the signal name (.camel, .kebab, .snake, .pascal).
```

--------------------------------

### Rocket Definition Fields

Source: https://data-star.dev/reference/rocket

Overview of the configuration fields available when defining a Rocket component.

```APIDOC
## Rocket Definition Fields

### Description
Configuration fields used within the `rocket` definition object to control component lifecycle and behavior.

### Fields
- **props** (object) - Defines public props, decoding, defaults, and attribute reflection.
- **manifest** (object) - Adds slot and event metadata to the component manifest.
- **setup** (function) - Runs once per instance to create local state, observers, and timers.
- **onFirstRender** (function) - Runs after initial render when DOM refs are available.
- **render** (function) - Returns the component DOM using `html` or `svg` templates.
- **mode** ('open' | 'closed' | 'light') - Determines the DOM mounting strategy (Shadow DOM vs Light DOM).
- **renderOnPropChange** (boolean) - Controls if prop updates trigger re-rendering.
```

--------------------------------

### Date Codec

Source: https://data-star.dev/docs.md

Details on the `date` codec for decoding props into `Date` objects.

```APIDOC
## `date`

`date` decodes a prop into a `Date`. Invalid input falls back to a valid date object rather than leaving the component with an unusable value.

Without an explicit `.default(...)`, the zero value is a fresh valid `Date` created at decode time.

| Member | Effect | Notes |
|---|---|---|
| `.default(value)` | Supplies the fallback date. | Prefer a factory like `() => new Date()` to create a fresh timestamp per instance. |

```javascript
props: ({ date }) => ({
  startAt: date.default(() => new Date()),
  endAt: date.default(() => new Date(Date.now() + 60_000)),
})
```
```

--------------------------------

### Handle Keydown for Deletion

Source: https://data-star.dev/examples/rocket_flow

Listens for keydown events, specifically 'Backspace' or 'Delete', when an edge is selected. This is intended to trigger the deletion of the selected edge. Further implementation for edge deletion logic is expected.

```javascript
const handleKeydown = (evt) => {
      if (!selectedEdgeKey || (evt.key !== 'Backspace' && evt.key !== 'Delete'))

```

--------------------------------

### Define onFirstRender Hook

Source: https://data-star.dev/reference/rocket

The `onFirstRender` hook runs once per connected instance after initial rendering and ref population. Use it for tasks dependent on rendered DOM or `data-ref:*` refs, such as DOM measurements or focus management.

```typescript
1onFirstRender?: (context: SetupContext<InferProps<Defs>> & { refs: Record<string, any> }) => void
```

--------------------------------

### Control Signal Name Casing for References

Source: https://data-star.dev/reference/attributes

Use the `__case` modifier with `data-ref` to control the casing of the generated signal name. `.kebab` sets the casing to kebab-case.

```html
<div data-ref:my-signal__case.kebab></div>
```

--------------------------------

### Host Accessor Overrides

Source: https://data-star.dev/reference/rocket

Methods to customize how properties are accessed on the host element or to define entirely new host properties.

```APIDOC
## overrideProp(name, getter?, setter?)

### Description
Overrides the default host accessor for a specific prop. Useful for native-like form wrappers where the host property should mirror an inner control.

### Parameters
- **name** (string) - Required - The name of the prop to override.
- **getter** (function) - Optional - A function receiving `getDefault` that returns the custom value.
- **setter** (function) - Optional - A function receiving `value` and `setDefault` to handle custom assignment logic.

## defineHostProp(name, descriptor)

### Description
Defines a new property on the host element that is not a Rocket prop, such as read-only properties or imperative methods.

### Parameters
- **name** (string) - Required - The name of the host property.
- **descriptor** (PropertyDescriptor) - Required - The standard JavaScript property descriptor.
```

--------------------------------

### Define Rocket Component with Conditional Rendering

Source: https://data-star.dev/examples/rocket_conditional

This snippet defines a Rocket component named 'conditional-panel'. It uses props for 'step' and 'showDetails' to control the rendered content, demonstrating conditional rendering based on the 'step' prop.

```javascript
import { rocket } from 'datastar'

rocket('conditional-panel', {
  props: ({ number, bool }) => ({
    step: number.step(1).min(0).max(2),
    showDetails: bool,
  }),
  render: ({ html, props: { step, showDetails } }) => html`
    <section>
      <style>
        :host {
          display: block;
          --_outline-width: var(--size-1);
          --_shadow-width: var(--size-px-1);
          --_dark-color: var(--gray-3);
          --_shadow-color: var(--gray-4);
          --_color: var(--gray-5);
          --_active-color: var(--gray-6);
          --_text-color: var(--gray-12);
        }

        section {
          display: grid;
          gap: 0.75rem;
        }

        header {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
        }

        button {
          display: inline-flex;
          position: relative;
          align-self: flex-start;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: var(--font-size-2);
          font-family: var(--font-pixel);
          -webkit-font-smoothing: none;
          -moz-osx-font-smoothing: auto;
          text-transform: uppercase;
          padding: var(--size-2) var(--size-4) calc(var(--size-2) + var(--_shadow-width));
          border: 0;
          background-color: var(--_color);
          color: var(--_text-color);
          box-shadow: inset calc(-1 * var(--_shadow-width)) calc(-1 * var(--_shadow-width)) 0 0 var(--_shadow-color);
        }

        button:hover:not(:disabled, [aria-disabled='true']) {
          color: var(--_text-color);
          background-color: var(--_active-color);
        }

        button:active:not(:disabled, [aria-disabled='true']) {
          box-shadow: inset var(--_shadow-width) var(--_shadow-width) 0 0 var(--_shadow-color);
          padding: calc(var(--size-2) + var(--_shadow-width)) calc(var(--size-4) - var(--_shadow-width)) var(--size-2) calc(var(--size-4) + var(--_shadow-width));
        }

        button:focus-visible {
          outline: 2px solid var(--blue-6);
          outline-offset: 2px;
        }

        button::before,
        button::after {
          content: '';
          position: absolute;
          width: 100%;
          height: 100%;
          box-sizing: content-box;
        }

        button::before {
          top: calc(-1 * var(--_outline-width));
          left: 0;
          border-top: var(--_outline-width) var(--_dark-color) solid;
          border-bottom: var(--_outline-width) var(--_dark-color) solid;
        }

        button::after {
          top: 0;
          left: calc(-1 * var(--_outline-width));
          border-left: var(--_outline-width) var(--_dark-color) solid;
          border-right: var(--_outline-width) var(--_dark-color) solid;
        }

        [data-branch] {
          padding: 0.9rem 1rem;
          border-radius: 0.75rem;
          border: 1px solid var(--gray-5);
          background: var(--gray-1);
          color: var(--gray-12);

          strong,
          p {
            color: inherit;
          }

          p {
            margin: 0.35rem 0 0;
          }
        }

        [data-branch='loading'] {
          border-color: var(--amber-6);
          background: var(--amber-1);
          color: var(--amber-12);
        }

        [data-branch='ready'] {
          border-color: var(--green-6);
          background: var(--green-1);
          color: var(--green-12);
        }

        aside {
          margin-top: 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: 0.75rem;
          background: var(--green-2);
          color: var(--slate-12);
          border: 1px solid var(--green-6);
          line-height: 1.5;

          code {
            color: var(--green-11);
            background: var(--green-3);
            padding: 0.1rem 0.35rem;
            border-radius: 0.35rem;
          }
        }

        .callout {
          margin-top: 0.75rem;
        }
      </style>

      <header>
        <strong>${step === 0 ? 'State: Idle' : step === 1 ? 'State: Loading' : 'State: Ready'}</strong>
      </header>

      <div>
        ${step === 0
          ? html`
              <div data-branch="idle">
                <strong>Idle</strong>
                <p>
                  This branch exists only while the condition is true. Switching away
                  unmounts it completely.
                </p>

```

--------------------------------

### data-on-raf

Source: https://data-star.dev/reference

Runs an expression on every requestAnimationFrame event.

```APIDOC
## data-on-raf

### Description
Runs an expression on every `requestAnimationFrame` event.

### Modifiers
- `__throttle` - Throttle the event listener.
  - `.500ms` / `.1s` - Throttle duration.
  - `.noleading` - Throttle without leading edge.
  - `.trailing` - Throttle with trailing edge.
```

--------------------------------

### Datastar Actions

Source: https://data-star.dev/docs.md

Details on Datastar actions (helper functions) that can be safely used in Datastar expressions, prefixed with '@'.

```APIDOC
### Actions

Datastar provides actions (helper functions) that can be used in Datastar expressions.

> The `@` prefix designates actions that are safe to use in expressions. This is a security feature that prevents arbitrary JavaScript from being executed in the browser. Datastar uses [`Function()` constructors](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/Function) to create and execute these actions in a secure and controlled sandboxed environment.

### `@peek()`

> `@peek(callable: () => any)`

Allows accessing signals without subscribing to their changes in expressions.

```html
<div data-text="$foo + @peek(() => $bar)"></div>
```

In the example above, the expression in the `data-text` attribute will be re-evaluated whenever `$foo` changes, but it will *not* be re-evaluated when `$bar` changes, since it is evaluated inside the `@peek()` action.

### `@setAll()`

> `@setAll(value: any, filter?: {include: RegExp, exclude?: RegExp})`

Sets the value of all matching signals (or all signals if no filter is used) to the expression provided in the first argument. The second argument is an optional filter object with an `include` property that accepts a regular expression to match signal paths. You can optionally provide an `exclude` property to exclude specific patterns.

> The [Datastar Inspector](https://data-star.dev/pro#datastar-inspector) can be used to inspect and filter current signals and view signal patch events in real-time.

```html
<!-- Sets the `foo` signal only -->
<div data-signals:foo="false">
    <button data-on:click="@setAll(true, {include: /^foo$/})"></button>
</div>

<!-- Sets all signals starting with `user.` -->
<div data-signals="{user: {name: '', nickname: ''}}">
    <button data-on:click="@setAll('johnny', {include: /^user\./})"></button>
</div>

<!-- Sets all signals except those ending with `_temp` -->
<div data-signals="{data: '', data_temp: '', info: '', info_temp: ''}">
    <button data-on:click="@setAll('reset', {include: /.*/, exclude: /_temp$/})"></button>
</div>
```

### `@toggleAll()`

> `@toggleAll(filter?: {include: RegExp, exclude?: RegExp})`

Toggles the boolean value of all matching signals (or all signals if no filter is used). The argument is an optional filter object with an `include` property that accepts a regular expression to match signal paths. You can optionally provide an `exclude` property to exclude specific patterns.

> The [Datastar Inspector](https://data-star.dev/pro#datastar-inspector) can be used to inspect and filter current signals and view signal patch events in real-time.

```html
<!-- Toggles the `foo` signal only -->
<div data-signals:foo="false">
    <button data-on:click="@toggleAll({include: /^foo$/})"></button>
</div>

<!-- Toggles all signals starting with `is` -->
<div data-signals="{isOpen: false, isActive: true, isEnabled: false}">
    <button data-on:click="@toggleAll({include: /^is/})"></button>
</div>

<!-- Toggles signals starting with `settings.` -->
<div data-signals="{settings: {darkMode: false, autoSave: true}}">
    <button data-on:click="@toggleAll({include: /^settings\./})"></button>
</div>
```
```

--------------------------------

### Conditional Class Application with data-class

Source: https://data-star.dev/docs.md

Apply or remove CSS classes based on Datastar expressions using `data-class:className`. Hyphenated class names are converted to kebab case. Multiple classes can be managed with an object literal.

```html
<input data-bind:foo-bar />
<button data-class:success="$fooBar != ''">
    Save
</button>
```

```html
<button data-class:font-bold="$fooBar == 'strong'">
    Save
</button>
```

```html
<button data-class="{success: $fooBar != '', 'font-bold': $fooBar == 'strong'}">
    Save
</button>
```

--------------------------------

### Stream SSE Events with JavaScript

Source: https://data-star.dev/guide/backend_requests

Stream patch elements and signals using the stream object in JavaScript. Signals can be passed as an object.

```javascript
stream.patchElements('<div id="question">...</div>');
stream.patchElements('<div id="instructions">...</div>');
stream.patchSignals({'answer': '...', 'prize': '...'});
```

--------------------------------

### Display Contact Details and Edit Controls

Source: https://data-star.dev/examples/click_to_edit

This HTML structure displays contact information and provides 'Edit' and 'Reset' buttons. The 'Edit' button triggers fetching the editing UI, while 'Reset' initiates a reset action.

```html
<div id="demo">
    <p>First Name: John</p>
    <p>Last Name: Doe</p>
    <p>Email: joe@blow.com</p>
    <div role="group">
        <button
            class="info"
            data-indicator:_fetching
            data-attr:disabled="$_fetching"
            data-on:click="@get('/examples/click_to_edit/edit')"
        >
            Edit
        </button>
        <button
            class="warning"
            data-indicator:_fetching
            data-attr:disabled="$_fetching"
            data-on:click="@patch('/examples/click_to_edit/reset')"
        >
            Reset
        </button>
    </div>
</div>
```

--------------------------------

### Handle Edge Registration and Updates

Source: https://data-star.dev/examples/rocket_flow

Functions to register new edges or update existing edge properties.

```javascript
const onEdgeRegister = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
      hideFlowChild(target)
      const detail =
        /** @type {CustomEvent<Record<string, any>>} */ (evt).detail ?? {}
      const entry = edges.get(target) ?? {
        el: target,
        group: null,
        path: null,
        labelEl: null,
        sourceId: '',
        targetId: '',
        label: '',
        animated: false,
        id: '',
      }
      entry.sourceId = (
        detail.source ??
        detail.sourceId ??
        target.getAttribute('source') ??
        ''
      ).trim()
      entry.targetId = (
        detail.target ??
        detail.targetId ??
        target.getAttribute('target') ??
        ''
      ).trim()
      entry.label = detail.label ?? target.getAttribute('label') ?? ''
      entry.animated = Boolean(
        detail.animated ?? target.hasAttribute('animated'),
      )
      entry.id = (detail.id ?? target.getAttribute('id') ?? '').trim()
      edges.set(target, entry)
      ensureEdgeGraphics(entry)
      registerEdgeEntry(entry)
      scheduleEdgeRender()
    }
```

```javascript
const onEdgeUpdate = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
```

--------------------------------

### Bind classes conditionally

Source: https://data-star.dev/docs.md

Add or remove classes based on expression evaluation or key-value pairs.

```html
<div data-class:font-bold="$foo == 'strong'"></div>
```

```html
<div data-class="{success: $foo != '', 'font-bold': $foo == 'strong'}"></div>
```

```html
<div data-class:my-class__case.camel="$foo"></div>
```

--------------------------------

### HTML Response Headers

Source: https://data-star.dev/reference/actions

When returning HTML (text/html), DataStar supports optional response headers for targeting and patching elements.

```APIDOC
## HTML Response Headers

### Description
When returning HTML (`text/html`), the server can optionally include the following response headers to control how the content is patched into the DOM.

### Response Headers
- **`datastar-selector`** (string) - A CSS selector for the target elements to patch.
- **`datastar-mode`** (string) - How to patch the elements (`outer`, `inner`, `remove`, `replace`, `prepend`, `append`, `before`, `after`). Defaults to `outer`.
- **`datastar-use-view-transition`** (boolean) - Whether to use the View Transition API when patching elements.

### Request Example
```javascript
response.headers.set('Content-Type', 'text/html')
response.headers.set('datastar-selector', '#my-element')
response.headers.set('datastar-mode', 'inner')
response.body = '<p>New content</p>'
```
```

--------------------------------

### Morph Multiple SVG Elements

Source: https://data-star.dev/examples/svg_morphing

This Go snippet demonstrates updating multiple SVG elements simultaneously with random colors and sizes in a single `sse.PatchElements` call. Ensure the parent SVG has the correct ID.

```go
1svgMorphingRouter.Get("/multiple_elements", func(w http.ResponseWriter, r *http.Request) {
2    sse := datastar.NewSSE(w, r)
3    color1 := svgColors[rand.N(len(svgColors))]
4    color2 := svgColors[rand.N(len(svgColors))]
5    color3 := svgColors[rand.N(len(svgColors))]
6    r1 := 10 + rand.N(20) // radius 10-30
7    r2 := 10 + rand.N(20)
8    r3 := 10 + rand.N(20)
9    sse.PatchElements(fmt.Sprintf(`<svg id="multi-demo">
10        <circle cx="30" cy="30" r="%d" fill="%s" />
11        <circle cx="70" cy="30" r="%d" fill="%s" />
12        <circle cx="50" cy="70" r="%d" fill="%s" />
13    </svg>`, r1, color1, r2, color2, r3, color3))
14})

```

--------------------------------

### Dynamic Polling Frequency in Clojure

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses the Datastar Clojure API to patch elements with a dynamic interval duration.

```clojure
 1(require
 2  '[starfederation.datastar.clojure.api :as d*]
 3  '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
 4  '[some.hiccup.library :refer [html]])
 5
 6(import
 7  'java.time.format.DateTimeFormatter
 8  'java.time.LocalDateTime)
 9
10(def date-time-formatter (DateTimeFormatter/ofPattern "YYYY-MM-DD HH:mm:ss"))
11(def seconds-formatter (DateTimeFormatter/ofPattern "ss"))
12
13(defn handle [ring-request]
14  (->sse-response ring-request
15    {on-open
16     (fn [sse]
17       (let [now (LocalDateTime/now)
18             current-time (LocalDateTime/.format now date-time-formatter)
19             seconds (LocalDateTime/.format now seconds-formatter)
20             duration (if (neg? (compare seconds "50"))
21                         "5"
22                         "1")]
23         (d*/patch-elements! sse
24           (html [:div#time {(str "data-on-interval__duration." duration "s")
25                             (d*/sse-get "/endpoint")}
26                   current-time]))))}))
27
28         (d*/close-sse! sse))}))
```

--------------------------------

### Send SSE Events with C# Datastar Service

Source: https://data-star.dev/guide/backend_requests

Utilize the DatastarService in C# to asynchronously patch elements and signals via SSE.

```csharp
datastarService.PatchElementsAsync(@"<div id=\"question\">...</div>");
datastarService.PatchElementsAsync(@"<div id=\"instructions\">...</div>");
datastarService.PatchSignalsAsync(new { answer = "...", prize = "..." } );
```

--------------------------------

### Schedule Node Rendering

Source: https://data-star.dev/examples/rocket_flow

Schedules the rendering of nodes using requestAnimationFrame to optimize performance. Prevents multiple render calls within the same frame.

```javascript
    const scheduleNodeRender = () => {
      if (graphFrame) return
      graphFrame = requestAnimationFrame(() => {
        graphFrame = 0
        renderNodes()
      })
    }
```

--------------------------------

### Configure Content Security Policy for Datastar

Source: https://data-star.dev/reference/security

When using a Content Security Policy (CSP), 'unsafe-eval' must be allowed for scripts, as Datastar evaluates expressions using a Function() constructor. This meta tag enables 'unsafe-eval'.

```html
<meta http-equiv="Content-Security-Policy"
    content="script-src 'self' 'unsafe-eval';"
>
```

--------------------------------

### data-ref

Source: https://data-star.dev/reference/attributes

Creates a new signal that is a reference to the element on which the data attribute is placed.

```APIDOC
## data-ref

### Description
Creates a new signal that is a reference to the element on which the data attribute is placed. This allows you to easily access and manipulate DOM elements via signals.

### Method
N/A (Attribute-based)

### Endpoint
N/A

### Parameters
#### Attributes
- **data-ref** (string) - Required - The name of the signal to create, which will reference the element. Can be specified as the attribute key or value.

#### Modifiers
Modifiers allow you to modify behavior when defining references using a key.
- **__case** - Converts the casing of the signal name.
  - `.camel` - Camel case: `mySignal` (default)
  - `.kebab` - Kebab case: `my-signal`
  - `.snake` - Snake case: `my_signal`
  - `.pascal` - Pascal case: `MySignal`

### Request Example
```html
<div data-ref:foo></div>
<div data-ref="foo"></div>
$foo is a reference to a <span data-text="$foo.tagName"></span> element
<div data-ref:my-signal__case.kebab></div>
```

### Response
N/A (Attribute-based behavior)
```

--------------------------------

### Map Component Styles

Source: https://data-star.dev/examples/rocket_openfreemap

CSS styles for the map container and custom marker elements.

```css
:host {
        display: block;
        width: 100%;
        height: 100%;
        min-height: 320px;
        position: relative;
        overflow: hidden;
        --rocket-openfreemap-marker-icon-bg: #ad1529;
        --rocket-openfreemap-marker-icon-fg: #ffffff;
        --rocket-openfreemap-marker-label-bg: rgba(20, 21, 23, 0.84);
        --rocket-openfreemap-marker-label-fg: #ffffff;
        --rocket-openfreemap-marker-border: rgba(255, 255, 255, 0.28);
      }

      .map-node {
        width: 100%;
        height: 100%;
        min-height: inherit;
      }

      .rocket-openfreemap-marker {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        transform: translateY(-8px);
      }

      .rocket-openfreemap-marker-icon {
        width: 3rem;
        height: 3rem;
        border-radius: 999px;
        background: var(--rocket-openfreemap-marker-icon-bg);
```

--------------------------------

### Attribute Casing for Signal Names

Source: https://data-star.dev/reference

Datastar applies attribute casing rules to signal names. Both `data-bind:foo-bar` and `data-bind="fooBar"` create the signal `$fooBar`.

```html
<!-- Both of these create the signal $fooBar -->
<input data-bind:foo-bar />
<input data-bind="fooBar" />
```

--------------------------------

### Rocket Render Type Definitions

Source: https://data-star.dev/docs.md

Defines the types for renderable values, context, and the render function itself. Supports primitive values, DOM nodes, iterables, and up to 8 typed arguments.

```typescript
type RocketPrimitiveRenderValue =
  | string
  | number
  | boolean
  | bigint
  | Date
  | null
  | undefined

type RocketComposedRenderValue =
  | RocketPrimitiveRenderValue
  | Node
  | Iterable<RocketComposedRenderValue>

type RocketRenderValue =
  | DocumentFragment
  | RocketPrimitiveRenderValue
  | Iterable<RocketComposedRenderValue>

type RocketRender<Props extends Record<string, any>> = {
  (context: RenderContext<Props>): RocketRenderValue
  <A1>(context: RenderContext<Props>, a1: A1): RocketRenderValue
  <A1, A2, A3, A4, A5, A6, A7, A8>(
    context: RenderContext<Props>,
    a1: A1,
    a2: A2,
    a3: A3,
    a4: A4,
    a5: A5,
    a6: A6,
    a7: A7,
    a8: A8,
  ): RocketRenderValue
}

render?: RocketRender<InferProps<Defs>>
```

--------------------------------

### Progress Bar HTML Structure

Source: https://data-star.dev/examples/progress_bar

Defines the SVG-based progress bar and the interaction trigger for restarting the process.

```html
 1<div id="progress-bar"
 2     data-init="@get('/examples/progress_bar/updates', {openWhenHidden: true})"
 3>
 4    <svg
 5        width="200"
 6        height="200"
 7        viewbox="-25 -25 250 250"
 8        style="transform: rotate(-90deg)"
 9    >
10        <circle
11            r="90"
12            cx="100"
13            cy="100"
14            fill="transparent"
15            stroke="#e0e0e0"
16            stroke-width="16px"
17            stroke-dasharray="565.48px"
18            stroke-dashoffset="565px"
19        ></circle>
20        <circle
21            r="90"
22            cx="100"
23            cy="100"
24            fill="transparent"
25            stroke="#6bdba7"
26            stroke-width="16px"
27            stroke-linecap="round"
28            stroke-dashoffset="282px"
29            stroke-dasharray="565.48px"
30        ></circle>
31        <text
32            x="44px"
33            y="115px"
34            fill="#6bdba7"
35            font-size="52px"
36            font-weight="bold"
37            style="transform:rotate(90deg) translate(0px, -196px)"
38        >50%</text>
39    </svg>
40
41    <div data-on:click="@get('/examples/progress_bar/updates', {openWhenHidden: true})">
42        <!-- When progress is 100% -->
43        <button>
44            Completed! Try again?
45        </button>
46    </div>
47</div>
```

--------------------------------

### PUT /endpoint

Source: https://data-star.dev/reference/actions

Sends a PUT request to the specified URI.

```APIDOC
## PUT /endpoint

### Description
Sends a PUT request to the backend.

### Method
PUT

### Endpoint
/endpoint

### Request Example
<button data-on:click="@put('/endpoint')"></button>
```

--------------------------------

### Button with Manual Loading Indicator Management

Source: https://data-star.dev/guide/the_tao_of_datastar

This snippet illustrates manual control over a loading indicator. The loading class is added to the button's parent element before the backend request is initiated, and it's expected to be removed when the DOM is updated from the backend.

```html
<div>
    <button data-on:click="el.classList.add('loading'); @post('/do_something')">
        Do something
        <span>Loading...</span>
    </button>
</div>
```

--------------------------------

### Nesting Signals with Dot Notation

Source: https://data-star.dev/guide/backend_requests

Use dot notation within the `data-signals` attribute to define nested signal structures.

```html
1<div data-signals:foo.bar="1"></div>
```

--------------------------------

### PUT Request

Source: https://data-star.dev/docs.md

Sends a PUT request to the backend. Signals are sent as a JSON body by default. Supports options like `openWhenHidden` and `contentType`.

```APIDOC
## PUT /endpoint

### Description
Sends a `PUT` request to the backend. Works similarly to `@get()` but uses the PUT HTTP method. Signals are sent as a JSON body by default.

### Method
PUT

### Endpoint
`/endpoint`

### Parameters
#### Query Parameters
- **openWhenHidden** (boolean) - Optional - If true, the SSE connection remains open when the page is hidden.
- **contentType** (string) - Optional - Sets the `Content-Type` header. Can be 'form' for `application/x-www-form-urlencoded`.

### Request Example
```html
<button data-on:click="@put('/endpoint')"></button>
```

### Response
#### Success Response (200)
- **Datastar SSE events** (array) - Zero or more SSE events from the backend.
```

--------------------------------

### data-scroll-into-view

Source: https://data-star.dev/reference

Scrolls the element into view.

```APIDOC
## data-scroll-into-view

### Description
Scrolls the element into view. Useful when updating the DOM from the backend.
```

--------------------------------

### Event Listeners (data-on)

Source: https://data-star.dev/docs.md

Handles standard DOM events with support for various modifiers to control event propagation, timing, and execution context.

```APIDOC
## data-on:[event]

### Description
Attaches an event listener to an element. Modifiers can be chained to alter behavior such as debouncing, throttling, or event propagation control.

### Modifiers
- __once: Only trigger once.
- __passive: Do not call preventDefault.
- __capture: Use capture phase.
- __case: Convert event casing (.camel, .kebab, .snake, .pascal).
- __delay: Delay execution (.500ms, .1s).
- __debounce: Debounce execution (.500ms, .1s, .leading, .notrailing).
- __throttle: Throttle execution (.500ms, .1s, .noleading, .trailing).
- __viewtransition: Wrap in document.startViewTransition().
- __window: Attach to window.
- __document: Attach to document.
- __outside: Trigger when event is outside element.
- __prevent: Call preventDefault.
- __stop: Call stopPropagation.

### Request Example
<button data-on:click__window__debounce.500ms.leading="$foo = ''"></button>
```

--------------------------------

### Stream SSE events in Kotlin

Source: https://data-star.dev/guide/backend_requests

Uses the ServerSentEventGenerator to patch elements and signals.

```kotlin
1val generator = ServerSentEventGenerator(response)
2
3generator.patchElements(
4    elements = """<div id="question">What do you put in a toaster?</div>""",
5)
6
7generator.patchSignals(
8    signals = """{"response": "", "answer": "bread"}""",
9)
```

--------------------------------

### Send SSE Events with Java Datastar Generator

Source: https://data-star.dev/guide/backend_requests

Employ the generator in Java to send patch elements and signals. Signals should be formatted as a JSON string.

```java
generator.send(PatchElements.builder()
    .data("<div id=\"question\">...</div>")
    .build()
);
generator.send(PatchElements.builder()
    .data("<div id=\"instructions\">...</div>")
    .build()
);
generator.send(PatchSignals.builder()
    .data("{\"answer\": \"...\", \"prize\": \"...\"}")
    .build()
);
```

--------------------------------

### Patching a single signal with data-signals

Source: https://data-star.dev/reference/attributes

Use `data-signals` to add, update, or remove a single signal. Values defined later in the DOM override earlier ones.

```html
<div data-signals:foo="1"></div>
```

--------------------------------

### Patching Elements with Kotlin SDK

Source: https://data-star.dev/guide/getting_started

Use the ServerSentEventGenerator instance to call the patchElements method.

```kotlin
 1val generator = ServerSentEventGenerator(response)
 2
 3generator.patchElements(

```

--------------------------------

### PHP SSE Patch Signals

Source: https://data-star.dev/docs.md

Uses the ServerSentEventGenerator in PHP to patch signals, with a sleep function to introduce a delay between updates.

```php
use starfederation\datastar\ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
$sse = new ServerSentEventGenerator();

// Patches signals.
$sse->patchSignals(['hal' => 'Affirmative, Dave. I read you.']);

sleep(1);

$sse->patchSignals(['hal' => '...']);
```

--------------------------------

### Setting a single CSS style with data-style

Source: https://data-star.dev/docs.md

Dynamically set a single CSS style property using an expression.

```html
<div data-style:display="$hiding && 'none'"></div>
```

--------------------------------

### Built-in Codec Registry

Source: https://data-star.dev/reference/rocket

Overview of the standard codecs available in the Rocket props registry for common data types.

```APIDOC
## Built-in Codec Registry

### Description
Rocket provides a set of built-in codecs for handling common data types like strings, numbers, booleans, dates, and structured JSON/JS objects.

### Codec Table
| Codec | Decoded type | Typical input |
|---|---|---|
| `string` | `string` | `" hello "` |
| `number` | `number` | `"42"` |
| `bool` | `boolean` | `"true"` |
| `date` | `Date` | `"2026-03-18T12:00:00.000Z"` |
| `json` | `any` | `'{"items":[1,2,3]}'` |
| `array(codec)` | `T[]` | `'["a","b"]'` |
| `object(shape)` | `Typed object` | `'{"x":10,"y":20}'` |
```

--------------------------------

### Rocket Mode Options

Source: https://data-star.dev/reference/rocket

Defines the possible values for the 'mode' option in a Rocket component definition, specifying where the component's DOM will be mounted.

```typescript
mode?: 'open' | 'closed' | 'light'

```

--------------------------------

### Send SSE Events with Python Datastar Generator

Source: https://data-star.dev/guide/backend_requests

Use the generator in Python to send patch elements and signals. Utilize triple-quoted strings for HTML and JSON data.

```python
generator.patchElements(
    elements = """<div id=\"question\">...</div>""",
)
generator.patchElements(
    elements = """<div id=\"instructions\">...</div>""",
)
generator.patchSignals(
    signals = "{\"answer\": \"...\", \"prize\": \"...\"}",
)
```

--------------------------------

### Implement Inline Validation Form in HTML

Source: https://data-star.dev/examples/inline_validation

Uses data-on:keydown__debounce to trigger server-side validation requests and data-bind to manage form state.

```html
<div id="demo">
    <label>
        Email Address
        <input
            type="email"
            required
            aria-live="polite"
            aria-describedby="email-info"
            data-bind:email
            data-on:keydown__debounce.500ms="@post('/examples/inline_validation/validate')"
        />
    </label>
    <p id="email-info" class="info">The only valid email address is "test@test.com".</p>
    <label>
        First Name
        <input
            type="text"
            required
            aria-live="polite"
            data-bind:first-name
            data-on:keydown__debounce.500ms="@post('/examples/inline_validation/validate')"
        />
    </label>
    <label>
        Last Name
        <input
            type="text"
            required
            aria-live="polite"
            data-bind:last-name
            data-on:keydown__debounce.500ms="@post('/examples/inline_validation/validate')"
        />
    </label>
    <button
        class="success"
        data-on:click="@post('/examples/inline_validation')"
    >
        <i class="material-symbols:person-add"></i>
        Sign Up
    </button>
</div>
```

--------------------------------

### Perform multipart form upload

Source: https://data-star.dev/reference/actions

Uses multipart/form-data encoding for file uploads within a form element.

```html
<form enctype="multipart/form-data">
    <input type="file" name="file" />
    <button data-on:click="@post('/endpoint', {contentType: 'form'})"></button>
</form>
```

--------------------------------

### Using Signal Properties

Source: https://data-star.dev/guide/datastar_expressions

Datastar expressions can access properties of signals, such as '.length' for strings. The expression is evaluated in a sandboxed context after converting the signal to its value.

```html
1<div data-text="$foo.length"></div>
```

--------------------------------

### Perform DELETE request

Source: https://data-star.dev/reference/actions

Sends a DELETE request to the backend.

```html
<button data-on:click="@delete('/endpoint')"></button>
```

--------------------------------

### Setting multiple CSS styles with data-style

Source: https://data-star.dev/docs.md

Set multiple CSS properties at once using a JavaScript object notation within the `data-style` attribute.

```html
<div data-style="{
    display: $hiding ? 'none' : 'flex',
    'background-color': $red ? 'red' : 'green'
}"></div>
```

--------------------------------

### Executing Side Effects with Data Effect

Source: https://data-star.dev/reference/attributes

Use `data-effect` to execute an expression, updating signal `$foo` whenever `$bar` or `$baz` change. This is for side effects only.

```html
1<div data-effect="$foo = $bar + $baz"></div>
```

--------------------------------

### Array and Tuple Prop Decoders

Source: https://data-star.dev/reference/rocket

Define homogeneous arrays or fixed-position tuples with specific codecs for each element.

```javascript
props: ({ array, string, number, bool }) => ({
  tags: array(string.trim.lower),
  point: array(number, number),
  localeSpec: array(
    string.lower.default('en'),
    number.min(1).default(1),
    bool,
  ).default(() => ['en', 1, false]),
})
```

--------------------------------

### Biome Configuration Override

Source: https://data-star.dev/reference/rocket

Disables the noTemplateCurlyInString lint rule to allow intentional template literals within Rocket source files.

```json
 1{
 2  "overrides": [
 3    {
 4      "includes": ["site/shared/static/rocket/**/*.js"],
 5      "linter": {
 6        "rules": {
 7          "suspicious": {
 8            "noTemplateCurlyInString": "off"
 9          }
10        }
11      }
12    }
13  ]
14}
```

--------------------------------

### Web Component for String Reversal

Source: https://data-star.dev/examples/web_component

Defines a custom web component that reverses a string provided via the 'name' attribute. It dispatches a 'reverse' event with the reversed string in its details. Ensure the component is defined using customElements.define.

```javascript
class ReverseComponent extends HTMLElement {
    static get observedAttributes() {
        return ["name"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        const value = [...newValue].toReversed().join("");
        this.dispatchEvent(new CustomEvent("reverse", { detail: { value } }));
    }
}

customElements.define("reverse-component", ReverseComponent);
```

--------------------------------

### Using data-computed with object syntax

Source: https://data-star.dev/errors/computed_expected_function

Each leaf value within the data-computed object must be defined as a function.

```html
<div data-computed="{foo: () => 1, bar: () => $foo + 1}"></div>
```

--------------------------------

### Rocket Component Definitions for Light and Shadow DOM

Source: https://data-star.dev/examples/rocket_projection

This JavaScript code defines two Rocket components, 'light-counter' and 'slot-counter'. It includes a helper function `rewriteRocketScopedChildren` to transform expressions for instance scope and configures component behavior, props, and rendering.

```javascript
 1import { rocket } from 'datastar'
 2
 3const rewriteRocketScopedChildren = (root, base) => {
 4  if (!base) return
 5  for (const node of root.querySelectorAll('*')) {
 6    for (const { name, value } of [...node.attributes]) {
 7      if (!name.startsWith('data-') || !value.includes('$$')) continue
 8      node.setAttribute(
 9        name,
10        value.replace(
11          /\$\$([a-zA-Z_\d]\w*(?:[.-]\w+)*)/g,
12          (_, path) => `$${'.'}${base}.${path}`,
13        ),
14      )
15    }
16  }
17}
18
19rocket('light-counter', {
20  mode: 'light',
21  props: ({ number }) => ({ clicks: number }),
22  setup({ $$, props }) {
23    $$.clicks = props.clicks
24  },
25  render: ({ html }) => html`
26    <div data-rocket-content>
27      <slot></slot>
28    </div>
29  `,
30})
31
32rocket('slot-counter', {
33  props: ({ number }) => ({ clicks: number }),
34  setup({ apply, host, $$, props }) {
35    $$.clicks = props.clicks
36    rewriteRocketScopedChildren(host, host.rocketSignalPath)
37    apply(host, false)
38  },
39  render: ({ html }) => html`
40    <div class="callout success">
41      <slot></slot>
42    </div>
43  `,
44})
```

--------------------------------

### Computed Signal with Callable Values

Source: https://data-star.dev/reference/attributes

Define computed signals using key-value pairs where values are functions that return reactive values.

```html
1<div data-computed="{foo: () => $bar + $baz}"></div>
```

--------------------------------

### Object Codec

Source: https://data-star.dev/reference/rocket

The `object` codec builds a typed nested object with configurable fields. Each field can have its own codec, allowing for complex data structures. Defaults can be specified for the object itself and for individual fields.

```APIDOC
## `object` codec

### Description
`object(shape)` builds a typed nested object. Each field has its own codec, so you can mix strings, numbers, booleans, arrays, and even nested objects inside a single prop. Without an explicit `.default(...)`, each field falls back to that field codec’s own default or zero value.

### Member
- `object(shape)`: Creates a fixed-key decoded object. Missing nested fields use their nested codec defaults when present.
- `.default(value)`: Supplies a fallback object. Prefer a factory to create per-instance objects.

### Example
```javascript
props: ({ object, string, number, bool, array }) => ({
  profile: object({
    id: string.trim,
    name: string.trim.default('Anonymous'),
    age: number.min(0),
    admin: bool,
    tags: array(string.trim.lower),
  }).default(() => ({
    id: '',
    name: 'Anonymous',
    age: 0,
    admin: false,
    tags: [],
  })),
})
```
```

--------------------------------

### Display Reactive JSON Signals with data-json-signals

Source: https://data-star.dev/reference/attributes

Use `data-json-signals` to display a reactive, stringified JSON representation of signals within an element's text content. This is helpful for debugging.

```html
<!-- Display all signals -->
<pre data-json-signals></pre>
```

```html
<!-- Only show signals that include "user" in their path -->
<pre data-json-signals="{include: /user/}"></pre>

<!-- Show all signals except those ending in "temp" -->
<pre data-json-signals="{exclude: /temp$/}"></pre>

<!-- Combine include and exclude filters -->
<pre data-json-signals="{include: /^app/, exclude: /password/}"></pre>
```

--------------------------------

### data-effect

Source: https://data-star.dev/reference/attributes

Executes an expression on page load and whenever any signals in the expression change.

```APIDOC
### `data-effect`

Executes an expression on page load and whenever any signals in the expression change. This is useful for performing side effects, such as updating other signals, making requests to the backend, or manipulating the DOM.

#### Example Usage
```html
<div data-effect="$foo = $bar + $baz"></div>
```
```

--------------------------------

### Default Node Dimensions

Source: https://data-star.dev/examples/rocket_flow

Default width and height values for nodes within the Rocket component.

```javascript
const DEFAULT_NODE_WIDTH = 120
const DEFAULT_NODE_HEIGHT = 48
```

--------------------------------

### Append Script via SSE Event

Source: https://data-star.dev/guide/datastar_expressions

Appends a script tag to the document body using an SSE event.

```text
event: datastar-patch-elements
data: mode append
data: selector body
data: elements <script>alert('This mission is too important for me to allow you to jeopardize it.')</script>

```

--------------------------------

### Append Item and Update Signals with DataStar

Source: https://data-star.dev/how_tos/load_more_list_items

Appends a new item to a list and updates the offset signal if the maximum number of items has not been reached. Otherwise, it removes the load more button.

```PHP
use starfederation\datastar\enums\ElementPatchMode;
use starfederation\datastar\ServerSentEventGenerator;

$signals = ServerSentEventGenerator::readSignals();

$max = 5;
$limit = 1;
$offset = $signals['offset'] ?? 1;

$sse = new ServerSentEventGenerator();

if ($offset < $max) {
    $newOffset = $offset + $limit;
    $sse->patchElements("<div>Item $newOffset</div>", [
        'selector' => '#list',
        'mode' => ElementPatchMode::Append,
    ]);
    if (newOffset < $max) {
        $sse->patchSignals(['offset' => $newOffset]);
    } else {
        $sse->removeElements('#load-more');
    }
}
```

--------------------------------

### Backend: Update Offset Signal Event

Source: https://data-star.dev/how_tos/load_more_list_items

A Datastar event to update client-side signals. Use this to synchronize state, such as the current offset, between the server and client.

```text
1event: datastar-patch-signals
2data: signals {offset: 2}
3

```

--------------------------------

### Node ID and Event Management

Source: https://data-star.dev/examples/rocket_flow

Synchronizes node dataset attributes and dispatches custom events for node interactions.

```javascript
const syncNodeDataset = (entry) => {
  if (!entry?.group) return
  if (entry.id) entry.group.dataset.nodeId = entry.id
  else delete entry.group.dataset.nodeId
}

const updateNodeId = (entry, nextId) => {
  const id = (nextId ?? '').trim()
  if (entry.id && nodesById.get(entry.id) === entry)
    nodesById.delete(entry.id)
  entry.id = id
  if (id) nodesById.set(id, entry)
  syncNodeDataset(entry)
}

const emitNodeEvent = (entry, type, extra = {}) => {
  if (!entry?.el) return
  entry.el.dispatchEvent(
    new CustomEvent(type, {
      detail: {
        instanceId: entry.el.rocketInstanceId,
        node: entry.el,
        x: entry.x,
        y: entry.y,
        ...extra,
      },
      bubbles: true,
      composed: true,
    }),
  )
}
```

--------------------------------

### Reading Nested Signals in Go

Source: https://data-star.dev/guide/backend_requests

Define a Go struct to represent nested signals and use the `datastar.ReadSignals` function to parse them from an incoming HTTP request.

```go
 1import ("github.com/starfederation/datastar-go/datastar")
 2
 3type Signals struct {
 4    Foo struct {
 5        Bar string `json:"bar"`
 6    } `json:"foo"`
 7}
 8
 9signals := &Signals{}
10if err := datastar.ReadSignals(request, signals); err != nil {
11    http.Error(w, err.Error(), http.StatusBadRequest)
12    return
13}
```

--------------------------------

### Format number as USD currency

Source: https://data-star.dev/docs.md

Use the @intl() function to format a number as USD currency according to the user's locale. Ensure the 'number' type and appropriate options are provided.

```html
<div data-text="@intl('number', 1000000, {style: 'currency', currency: 'USD'})"></div>
```

--------------------------------

### Multiple Statements in Datastar Expression

Source: https://data-star.dev/docs.md

Updates the '$landingGearRetracted' signal and then triggers a POST request using a single Datastar expression with multiple statements separated by a semicolon.

```html
<div data-signals:foo="1">
    <button data-on:click="$landingGearRetracted = true; @post('/launch')">
        Force launch
    </button>
</div>
```

--------------------------------

### datastar-patch-signals SSE Event

Source: https://data-star.dev/reference/sse_events

Handles patching of signals using Server-Sent Events. Allows updating existing signals or adding new ones.

```APIDOC
## SSE Event: datastar-patch-signals

### Description
Patches signals into the existing signals on the page. The `onlyIfMissing` line determines whether to update each signal with the new value only if a signal with that name does not yet exist. The `signals` line should be a valid `data-signals` attribute.

### Method
Server-Sent Event

### Endpoint
N/A (Server-Sent Event)

### Parameters
#### SSE Data Lines
- **`onlyIfMissing`** (boolean) - Optional - Determines whether to update a signal only if it does not yet exist.
- **`signals`** (object) - Required - A JSON object representing the signals to patch, where keys are signal names and values are their new values.

### Request Example
```
event: datastar-patch-signals
data: signals {foo: 1, bar: 2}

```

### Response
#### Success Response
N/A (Server-Sent Event stream)

#### Response Example
```
event: datastar-patch-signals
data: signals {foo: 1, bar: 2}

```

### Additional Examples

**Removing signals:**
```
event: datastar-patch-signals
data: signals {foo: null, bar: null}

```

**Patching with `onlyIfMissing` option:**
```
event: datastar-patch-signals
data: onlyIfMissing true
data: signals {foo: 1, bar: 2}

```
```

--------------------------------

### Listen for Ctrl + L Keydown Event Globally

Source: https://data-star.dev/how_tos/bind_keydown_events_to_specific_keys

Trigger an alert when the 'Ctrl' key is held down and the 'l' key is pressed, by checking `evt.ctrlKey` and `evt.key`.

```html
<div data-on:keydown__window="evt.ctrlKey && evt.key === 'l' && alert('Key pressed')"></div>
```

--------------------------------

### Reading Signals in Kotlin

Source: https://data-star.dev/guide/backend_requests

Define a Kotlin data class for signals and use `readSignals` with a provided `jsonUnmarshaller` to parse signals from a request.

```kotlin
 1@Serializable
 2data class Signals(
 3    val foo: String,
 4)
 5
 6val jsonUnmarshaller: JsonUnmarshaller<Signals> = { json -> Json.decodeFromString(json) }
 7
 8val request: Request =
 9    postRequest(
10        body =
11            """
12            {
13                "foo": "bar"
14            }
15            """.trimIndent(),
16    )
17
18val signals = readSignals(request, jsonUnmarshaller)
```

--------------------------------

### Toggle element visibility with data-show

Source: https://data-star.dev/guide/reactive_signals

Controls element display based on a boolean expression. Initial display: none is recommended to prevent content flashes.

```html
<input data-bind:foo-bar />
<button data-show="$fooBar != ''">
    Save
</button>
```

```html
<input data-bind:foo-bar />
<button data-show="$fooBar != ''" style="display: none">
    Save
</button>
```

--------------------------------

### Dynamic Polling Frequency in PHP

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses ServerSentEventGenerator to patch elements based on the current second.

```php
 1use starfederation\datastar\ServerSentEventGenerator;
 2
 3$currentTime = date('Y-m-d H:i:s');
 4$currentSeconds = date('s');
 5$duration = $currentSeconds < 50 ? 5 : 1;
 6
 7$sse = new ServerSentEventGenerator();
 8$sse->patchElements(`
 9    <div id="time"
10         data-on-interval__duration.${duration}s="@get('/endpoint')"
11    >
12        $currentTime
13    </div>
14`);
```

--------------------------------

### __root Modifier Usage

Source: https://data-star.dev/reference/rocket

Documentation for the __root modifier used to escape component-local signal scoping.

```APIDOC
## __root Modifier

### Description
The `__root` modifier is used when a Rocket component needs to leave a signal-name attribute in the outer page scope instead of rewriting it into the component’s private path. It acts as an escape hatch for wrapper-style components where host children should remain connected to outer-page Datastar signals.

### Usage
Apply the modifier to the key segment of the signal-name attribute.

### Supported Attributes
- `data-bind` and `data-bind:*`
- `data-computed:*`
- `data-indicator` and `data-indicator:*`
- `data-ref` and `data-ref:*`

### Example
```html
<demo-fieldset>
  <demo-input data-bind:name__root></demo-input>
</demo-fieldset>
```

### Notes
- Use sparingly.
- Do not use for normal component internals or when signals should be instance-local.
- Does not affect `data-attr:*`, `data-text`, or internal host/ref bookkeeping.
```

--------------------------------

### Stream SSE Events with Ruby Datastar

Source: https://data-star.dev/guide/backend_requests

Use the Datastar stream in Ruby to send patch elements and signals. Signals can be passed as a hash.

```ruby
datastar.stream do |sse|
  sse.patch_elements('<div id="question">...</div>')
  sse.patch_elements('<div id="instructions">...</div>')
  sse.patch_signals(answer: '...', prize: '...')
end
```

--------------------------------

### Handling Asynchronous Functions with Custom Events

Source: https://data-star.dev/guide/datastar_expressions

For asynchronous functions, dispatch a custom event with the result in its detail. Datastar will not await async operations directly within expressions. Listen for the custom event to update signals.

```html
1<div data-signals:result>
2    <input data-bind:foo
3           data-on:input="myfunction(el, $foo)"
4           data-on:mycustomevent__window="$result = evt.detail.value"
5    >
6    <span data-text="$result"></span>
7</div>
```

--------------------------------

### data-effect for Side Effects

Source: https://data-star.dev/reference

Execute an expression on page load and whenever its signal dependencies change. Useful for performing side effects like updating other signals or making backend requests.

```html
<div data-effect="$foo = $bar + $baz"></div>
```

--------------------------------

### data-on-signal-patch

Source: https://data-star.dev/reference/attributes

Runs an expression whenever any signals are patched. Useful for tracking changes, updating computed values, or triggering side effects.

```APIDOC
## data-on-signal-patch

### Description
Runs an expression whenever any signals are patched. This is useful for tracking changes, updating computed values, or triggering side effects when data updates.

### Method
N/A (Attribute-based)

### Endpoint
N/A

### Parameters
#### Attributes
- **data-on-signal-patch** (expression) - Required - The expression to execute when a signal is patched.
- **data-on-signal-patch-filter** (object) - Optional - Filters which signals to watch. Accepts an object with `include` and/or `exclude` properties that are regular expressions.

### Modifiers
Modifiers allow you to modify the timing of the event listener.
- **__delay** - Delay the event listener.
  - `.500ms` - Delay for 500 milliseconds.
  - `.1s` - Delay for 1 second.
- **__debounce** - Debounce the event listener.
  - `.500ms` - Debounce for 500 milliseconds.
  - `.1s` - Debounce for 1 second.
  - `.leading` - Debounce with leading edge.
  - `.notrailing` - Debounce without trailing edge.
- **__throttle** - Throttle the event listener.
  - `.500ms` - Throttle for 500 milliseconds.
  - `.1s` - Throttle for 1 second.
  - `.noleading` - Throttle without leading edge.
  - `.trailing` - Throttle with trailing edge.

### Request Example
```html
<div data-on-signal-patch="console.log('A signal changed!')"></div>
<div data-on-signal-patch="console.log('Signal patch:', patch)"></div>
<div data-on-signal-patch__debounce.500ms="doSomething()"></div>
```

### Response
N/A (Attribute-based behavior)
```

--------------------------------

### Attach Event Listener with data-on

Source: https://data-star.dev/guide/getting_started

Use the `data-on` attribute to attach an event listener to an HTML element. The attribute's value is a Datastar expression that executes when the event is triggered.

```html
<button data-on:click="alert('I’m sorry, Dave. I’m afraid I can’t do that.')">
    Open the pod bay doors, HAL.
</button>
```

--------------------------------

### Run Expression on Element Resize

Source: https://data-star.dev/reference/attributes

Executes an expression whenever an element's dimensions change. This is useful for responsive designs or layout adjustments.

```html
<div data-on-resize="$count++"></div>
```

--------------------------------

### Render Edges

Source: https://data-star.dev/examples/rocket_flow

Schedules an animation frame to update edge paths and labels based on source and target node positions.

```javascript
const scheduleEdgeRender = () => {
  if (!edges.size || edgeFramePending) return
  edgeFramePending = true
  edgeFrameId = requestAnimationFrame(() => {
    edgeFramePending = false
    edgeFrameId = 0
    for (const entry of edges.values()) {
      const source = entry.sourceId ? nodesById.get(entry.sourceId) : null
      const target = entry.targetId ? nodesById.get(entry.targetId) : null
      if (!source || !target) {
        entry.group?.setAttribute('display', 'none')
        continue
      }
      entry.group?.removeAttribute('display')
      const { c1x, c1y, c2x, c2y } = bezierPathPoints(
        source.x,
        source.y,
        target.x,
        target.y,
      )
      entry.path?.setAttribute(
        'd',
        `M ${source.x} ${source.y} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${target.x} ${target.y}`,
      )
      entry.path?.classList.toggle('is-animated', !!entry.animated)
      if (!entry.labelEl) continue
      if (!entry.label) {
        entry.labelEl.textContent = ''
        entry.labelEl.setAttribute('display', 'none')
        continue
      }
      entry.labelEl.textContent = entry.label
      entry.labelEl.removeAttribute('display')
      entry.labelEl.setAttribute('x', String((source.x + target.x) / 2))
      entry.labelEl.setAttribute('y', String((source.y + target.y) / 2))
    }
  })
}
```

--------------------------------

### Handle element resize events with data-on-resize

Source: https://data-star.dev/docs.md

Triggers an expression when element dimensions change, supporting debounce and throttle modifiers.

```html
<div data-on-resize="$count++"></div>
```

```html
<div data-on-resize__debounce.10ms="$count++"></div>
```

--------------------------------

### File Upload Binding

Source: https://data-star.dev/reference

Input fields of type `file` with `data-bind` will automatically encode file contents in base64. The resulting signal is an array of objects containing name, contents, and mime type.

```html
<input type="file" data-bind:files multiple />
```

--------------------------------

### Create Element Reference Signal (Value)

Source: https://data-star.dev/reference/attributes

Alternatively, use `data-ref="signalName"` to specify the signal name in the attribute value. This can be useful with certain templating languages.

```html
<div data-ref="foo"></div>
```

--------------------------------

### Data Binding with Kebab Case Modifier

Source: https://data-star.dev/reference/attributes

Use the `__case.kebab` modifier with `data-bind` to convert the signal name to kebab case.

```html
1<input data-bind:my-signal__case.kebab />
```

--------------------------------

### Bridge Property to DOM Ref

Source: https://data-star.dev/reference/rocket

Uses onFirstRender to link a property accessor to a rendered DOM element reference.

```javascript
 1rocket('demo-input-bridge', {
  props: ({ string }) => ({
    value: string.default(''),
  }),
  render: ({ html, props: { value } }) => html`
    <input data-ref:input value="${value}">
  `,
  onFirstRender({ overrideProp, refs }) {
    overrideProp(
      'value',
      (getDefault) => refs.input?.value ?? getDefault(),
      (value, setDefault) => {
        const next = String(value ?? '')
        if (refs.input && refs.input.value !== next) refs.input.value = next
        setDefault(next)
      },
    )
  },
})
```

--------------------------------

### Conditional Rendering with data-if

Source: https://data-star.dev/reference/rocket

Uses template tags to conditionally mount DOM branches based on component state. Inactive branches are removed from the live DOM.

```javascript
 1rocket('demo-status', {
 2  mode: 'light',
 3  setup({ $$ }) {
 4    $$.step = 0
 5  },
 6  render: ({ html }) => html`
 7    <div class="stack gap-2">
 8      <button type="button" data-on:click="$$step = ($$step + 1) % 3">Next</button>
 9
10      <template data-if="$$step === 0">
11        <p>Idle</p>
12      </template>
13      <template data-else-if="$$step === 1">
14        <p>Loading</p>
15      </template>
16      <template data-else>
17        <p>Ready</p>
18      </template>
19    </div>
20  `,
21})
```

--------------------------------

### Patch Elements with DataStar

Source: https://data-star.dev/how_tos/load_more_list_items

Patches elements on the page by appending new content to a specified selector. It also conditionally patches signals or removes a load more button based on the offset.

```Kotlin
val newOffset = offset + limit

generator.patchElements(
    elements = "<div>Item $newOffset</div>",
    options =
        PatchElementsOptions(
            selector = "#list",
            mode = ElementPatchMode.Append,
        ),
)

if (newOffset < max) {
    generator.patchSignals(
        signals = "{\"offset\": $newOffset}",
    )
} else {
    generator.patchElements(
        options =
            PatchElementsOptions(
                selector = "#load-more",
                mode = ElementPatchMode.Remove,
            ),
    )
}
```

--------------------------------

### Patch DOM and Signals

Source: https://data-star.dev/guide/backend_requests

Updates the DOM with new HTML content and synchronizes frontend signals from the backend.

```javascript
    // Patches elements into the DOM.
    stream.patchElements(`<div id="question">What do you put in a toaster?</div>`);

    // Patches signals.
    stream.patchSignals({'response':  '', 'answer': 'bread'});
});
```

--------------------------------

### Conditional and fallback styles with data-style

Source: https://data-star.dev/reference/attributes

Apply conditional styles using the logical AND operator (`&&`) or restore original inline styles when expressions evaluate to falsy values.

```html
<!-- When $x is false, color remains red from inline style -->
<div style="color: red;" data-style:color="$x && 'green'"></div>

<!-- When $hiding is true, display becomes none; when false, reverts to flex from inline style -->
<div style="display: flex;" data-style:display="$hiding && 'none'"></div>
```

--------------------------------

### Set JSON Response Headers with DataStar

Source: https://data-star.dev/reference/actions

For JSON responses, set `Content-Type` to `application/json` and optionally use the `datastar-only-if-missing` header to conditionally patch signals.

```javascript
response.headers.set('Content-Type', 'application/json')
response.headers.set('datastar-only-if-missing', 'true')
response.body = JSON.stringify({ foo: 'bar' })
```

--------------------------------

### PATCH Request

Source: https://data-star.dev/docs.md

Sends a PATCH request to the backend. Signals are sent as a JSON body by default. Supports options like `openWhenHidden` and `contentType`.

```APIDOC
## PATCH /endpoint

### Description
Sends a `PATCH` request to the backend. Works similarly to `@get()` but uses the PATCH HTTP method. Signals are sent as a JSON body by default.

### Method
PATCH

### Endpoint
`/endpoint`

### Parameters
#### Query Parameters
- **openWhenHidden** (boolean) - Optional - If true, the SSE connection remains open when the page is hidden.
- **contentType** (string) - Optional - Sets the `Content-Type` header. Can be 'form' for `application/x-www-form-urlencoded`.

### Request Example
```html
<button data-on:click="@patch('/endpoint')"></button>
```

### Response
#### Success Response (200)
- **Datastar SSE events** (array) - Zero or more SSE events from the backend.
```

--------------------------------

### SSE Event for Patching Elements

Source: https://data-star.dev/docs.md

Server-Sent Events (SSE) can be used to send zero or more `datastar-patch-elements` events. Each event contains HTML data to be morphed into the DOM. Note the required double newline after each event.

```text
event: datastar-patch-elements
data: elements <div id="hal">
data: elements     I’m sorry, Dave. I’m afraid I can’t do that.
data: elements </div>


```

--------------------------------

### Rocket Component Definition

Source: https://data-star.dev/examples/rocket_counter

Define the my-counter component using the rocket function, including prop validation and state observation.

```javascript
import { rocket } from 'datastar'

rocket('my-counter', {
  mode: 'light',
  props: ({ number }) => ({
    count: number.step(1).min(0),
  }),
  setup({ $$, observeProps, props }) {
    $$.counter = props.count
    observeProps(() => {
      $$.counter = props.count
    }, 'count')
  },
  render: ({ html }) => html`
    <button
      data-on:click="$$counter++"
      data-text="'Count: ' + $$counter"
    ></button>
  `,
})
```

--------------------------------

### Bind HTML attributes with data-attr

Source: https://data-star.dev/guide/reactive_signals

Use data-attr to bind HTML attribute values to expressions. Attribute names are converted to kebab case.

```html
1<input data-bind:foo />
2<button data-attr:disabled="$foo == ''">
3    Save
4</button>
```

```html
1<button data-attr:aria-hidden="$foo">Save</button>
```

```html
1<button data-attr="{disabled: $foo == '', 'aria-hidden': $foo}">Save</button>
```

--------------------------------

### Set View Transition Name

Source: https://data-star.dev/reference/attributes

Explicitly sets the view-transition-name style attribute on an element.

```html
<div data-view-transition="$foo"></div>
```

--------------------------------

### Define Rocket Password Strength Component

Source: https://data-star.dev/examples/rocket_password_strength

Register the component using the rocket function, defining props and a render function that binds input state to validation criteria.

```javascript
 1import { rocket } from 'datastar'
 2
 3rocket('password-strength', {
 4  mode: 'light',
 5  props: ({ string }) => ({ password: string }),
 6  setup({ $$, observeProps, props }) {
 7    $$.password = props.password ?? ''
 8    observeProps(() => {
 9      $$.password = props.password ?? ''
10    }, 'password')
11  },
12  render: ({ html }) => html`
13    <div class="password-strength-card">
14      <input
15        class="password-strength-input"
16        type="password"
17        placeholder="Test password strength"
18        data-bind:password
19      />
20      <ul class="password-strength-list">
21        ${
22          { label: '8+ characters', ok: '$$password.length >= 8' },
23          { label: '12+ characters', ok: '$$password.length >= 12' },
24          { label: 'Lowercase letter', ok: '/[a-z]/.test($$password)' },
25          { label: 'Uppercase letter', ok: '/[A-Z]/.test($$password)' },
26          { label: 'Number', ok: '/[0-9]/.test($$password)' },
27          {
28            label: 'Special character',
29            ok: '/[^a-zA-Z0-9]/.test($$password)',
30          },
31        ].map(({ label, ok }) => html`
32          <li class="password-strength-row">
33            <div
34              class="password-strength-status"
35              data-class:is-valid="${ok}"
36              data-text="${ok} ? '✓' : ''"
37            ></div>
38            <span class="password-strength-label" data-class:is-valid="${ok}"
39              >${label}</span
40            >
41          </li>
42        `)}
43      </ul>
44    </div>
45  `,
46})
```

--------------------------------

### PATCH /endpoint

Source: https://data-star.dev/reference/actions

Sends a PATCH request to the specified URI.

```APIDOC
## PATCH /endpoint

### Description
Sends a PATCH request to the backend.

### Method
PATCH

### Endpoint
/endpoint

### Request Example
<button data-on:click="@patch('/endpoint')"></button>
```

--------------------------------

### data-replace-url

Source: https://data-star.dev/reference

Replaces the browser URL without a page reload.

```APIDOC
## data-replace-url

### Description
Replaces the URL in the browser without reloading the page. The value is an evaluated expression.
```

--------------------------------

### Debug Signals with data-json-signals

Source: https://data-star.dev/reference

Renders reactive signals as JSON strings for debugging. Supports regex filtering and compact output via modifiers.

```html
<!-- Display all signals -->
<pre data-json-signals></pre>
```

```html
<!-- Only show signals that include "user" in their path -->
<pre data-json-signals="{include: /user/}"></pre>

<!-- Show all signals except those ending in "temp" -->
<pre data-json-signals="{exclude: /temp$/}"></pre>

<!-- Combine include and exclude filters -->
<pre data-json-signals="{include: /^app/, exclude: /password/}"></pre>
```

```html
<!-- Display filtered signals in a compact format -->
<pre data-json-signals__terse="{include: /counter/}"></pre>
```

--------------------------------

### Define Nested Object Structure with DataStar

Source: https://data-star.dev/reference/rocket

Use the `object` codec to create a typed nested object. Each field can have its own codec, allowing for mixed types. Missing fields will use their respective codec defaults.

```javascript
props: ({ object, string, number, bool, array }) => ({
  profile: object({
    id: string.trim,
    name: string.trim.default('Anonymous'),
    age: number.min(0),
    admin: bool,
    tags: array(string.trim.lower),
  }).default(() => ({
    id: '',
    name: 'Anonymous',
    age: 0,
    admin: false,
    tags: [],
  })),
})
```

--------------------------------

### Set HTML attributes with data-attr

Source: https://data-star.dev/reference/attributes

Use data-attr to bind a single attribute or multiple attributes via a key-value object.

```html
<div data-attr:aria-label="$foo"></div>
```

```html
<div data-attr="{'aria-label': $foo, disabled: $bar}"></div>
```

--------------------------------

### Component Rendering Mode

Source: https://data-star.dev/docs.md

The `mode` field in the Rocket definition specifies where the component renders, with options for 'open' shadow DOM, 'closed' shadow DOM, or 'light' DOM.

```typescript
mode?: 'open' | 'closed' | 'light'
```

--------------------------------

### Define Component Manifest Metadata

Source: https://data-star.dev/reference/rocket

Use the `manifest` property to document slots and events that Rocket cannot infer from the DOM. This metadata is used by tooling to describe the full public surface of the component.

```typescript
manifest?: {
  slots?: Array<{
    name: string
    description?: string
  }>
  events?: Array<{
    name: string
    kind?: 'event' | 'custom-event'
    bubbles?: boolean
    composed?: boolean
    description?: string
  }>
}
```

--------------------------------

### Using modifiers with data-signals

Source: https://data-star.dev/reference/attributes

Utilize modifiers like `__case` and `__ifmissing` with `data-signals` to control signal patching behavior, such as casing and conditional updates.

```html
<div data-signals:my-signal__case.kebab="1"
     data-signals:foo__ifmissing="1"
></div>
```

--------------------------------

### Schedule Graph Rendering

Source: https://data-star.dev/examples/rocket_flow

Schedules the main graph rendering using requestAnimationFrame. Ensures that rendering only occurs if the frame is not already scheduled and necessary SVG elements are available.

```javascript
    const schedule = () => {
      if (frame || !svg || !background || !gridPattern || !gridPath) return
      frame = requestAnimationFrame(() => {

```

--------------------------------

### Set JavaScript Response Headers with DataStar

Source: https://data-star.dev/reference/actions

When returning JavaScript, set `Content-Type` to `text/javascript` and use `datastar-script-attributes` to define attributes for the script element.

```javascript
response.headers.set('Content-Type', 'text/javascript')
response.headers.set('datastar-script-attributes', JSON.stringify({ type: 'module' }))
response.body = 'console.log("Hello from server!");'
```

--------------------------------

### String Codec Transformations

Source: https://data-star.dev/reference/rocket

The string codec provides a fluent API for normalizing and transforming string values.

```APIDOC
## String Codec Transformations

### Description
Use the string codec to perform normalization pipelines such as trimming, casing, and suffixing. These can be chained together.

### Available Members
- **.trim** - Removes surrounding whitespace.
- **.upper / .lower** - Changes string casing.
- **.kebab / .camel / .snake / .pascal** - Changes string naming convention.
- **.prefix(value) / .suffix(value)** - Adds prefix or suffix if missing.
- **.maxLength(n)** - Truncates string to n characters.
- **.default(value)** - Supplies a fallback string.

### Example
```javascript
props: ({ string }) => ({
  slug: string.trim.lower.kebab.maxLength(48),
  cssSize: string.trim.suffix('px').default('16px'),
  title: string.trim.title.default('Untitled'),
})
```
```

--------------------------------

### data-json-signals

Source: https://data-star.dev/reference/attributes

Displays reactive signals as a JSON string for debugging purposes.

```APIDOC
## data-json-signals

### Description
Sets the text content of an element to a reactive JSON stringified version of signals. Supports filtering via include/exclude regex objects.

### Modifiers
- `__terse`: Outputs a compact JSON format without extra whitespace.
```

--------------------------------

### Backend: Append Element Event

Source: https://data-star.dev/how_tos/load_more_list_items

A Datastar event to append new elements into a specified container. Use this to add new content to a list dynamically.

```text
1event: datastar-patch-elements
2data: selector #list
3data: mode append
4data: elements <div>Item 2</div>
5

```

--------------------------------

### Filter signal patches with data-on-signal-patch-filter

Source: https://data-star.dev/docs.md

Restricts which signals trigger the patch listener using include and exclude regular expression filters.

```html
<!-- Only react to counter signal changes -->
<div data-on-signal-patch-filter="{include: /^counter$/}"></div>

<!-- React to all changes except those ending with "changes" -->
<div data-on-signal-patch-filter="{exclude: /changes$/}"></div>

<!-- Combine include and exclude filters -->
<div data-on-signal-patch-filter="{include: /user/, exclude: /password/}"></div>
```

--------------------------------

### Patch Signals with Datastar

Source: https://data-star.dev/docs.md

Use the `datastar-patch-signals` event to patch signals. The `onlyIfMissing` option controls whether to update existing signals. Signals can be removed by setting their values to `null`.

```html
event: datastar-patch-signals
data: signals {foo: 1, bar: 2}


```

```html
event: datastar-patch-signals
data: signals {foo: null, bar: null}


```

```html
event: datastar-patch-signals
data: onlyIfMissing true
data: signals {foo: 1, bar: 2}


```

--------------------------------

### Checking if Blocks Have Loaded New Content

Source: https://data-star.dev/examples/rocket_virtual_scroll

Monitors the content of blocks to detect changes, indicating that new data has been loaded. If changes are detected, it triggers a repositioning of blocks and clears any pending timeouts.

```javascript
const checkBlocksLoaded = () => {
      if (
        !['A', 'B', 'C'].some((name) => {
          const html = blocks[name]?.innerHTML ?? ''
          const changed = html !== lastBlockContent[name]
          lastBlockContent[name] = html
          return changed
        })
      ) {
        return
      }

      positionBlocks()
      if (jumpTimeout) {
        clearJumpTimeout()
        isLoading = false
      }
    }
```

--------------------------------

### Trigger Interval Request Immediately

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Add the `.leading` modifier to the `data-on-interval__duration` attribute to execute the expression immediately upon page load, in addition to the regular interval.

```html
<div id="time"
     data-on-interval__duration.5s.leading="@get('/endpoint')"
></div>
```

--------------------------------

### Ensure Edge Graphics Creation

Source: https://data-star.dev/examples/rocket_flow

Creates and appends SVG elements (group, path, text) for an edge if they don't already exist. It registers the edge entry after creating the graphics.

```javascript
const ensureEdgeGraphics = (entry) => {
      if (entry.group) return
      const group = document.createElementNS(SVG_NS, 'g')
      const path = document.createElementNS(SVG_NS, 'path')
      const label = document.createElementNS(SVG_NS, 'text')
      group.classList.add('flow-edge')
      group.style.pointerEvents = 'auto'
      group.style.cursor = 'pointer'
      path.setAttribute('pointer-events', 'stroke')
      group.append(path, label)
      edgesLayer?.append(group)
      entry.group = group
      entry.path = path
      entry.labelEl = label
      registerEdgeEntry(entry)
    }
```

--------------------------------

### Date Prop API

Source: https://data-star.dev/reference/rocket

The date codec decodes a prop into a Date object.

```APIDOC
## date

### Description
Decodes a prop into a Date. Invalid input falls back to a valid date object.

### Members
- **default(value)**: Supplies the fallback date.
```

--------------------------------

### DataStar Fetch Events

Source: https://data-star.dev/reference/actions

DataStar triggers various events during the fetch request lifecycle, allowing for custom handling of different stages.

```APIDOC
## DataStar Fetch Events

### Description
All DataStar actions that trigger fetch requests emit `datastar-fetch` events during the request lifecycle. These events allow you to hook into different stages of the fetch process.

### Event Types
- **`started`**: Triggered when the fetch request begins.
- **`finished`**: Triggered when the fetch request completes successfully.
- **`error`**: Triggered when the fetch request encounters an error.
- **`retrying`**: Triggered when the fetch request is being retried.
- **`retries-failed`**: Triggered when all retry attempts for the fetch request have failed.

### Usage Example
```html
<div data-on:datastar-fetch="
    evt.detail.type === 'error' && console.log('Fetch error encountered')
"></div>
```
```

--------------------------------

### Keyed Signal-Name Attributes with __root

Source: https://data-star.dev/docs.md

For keyed signal-name attributes, append the __root modifier to the key segment. This allows Datastar to parse the base attribute shape before Rocket rewrites it, which is the recommended approach for authored host children.

```html
data-bind:name__root
```

```html
data-computed:total__root
```

```html
data-indicator:loading__root
```

```html
data-ref:input__root
```

--------------------------------

### Computed Signal Name Casing with Modifier

Source: https://data-star.dev/reference/attributes

Use the `__case.kebab` modifier with `data-computed` to format the computed signal name to kebab case.

```html
1<div data-computed:my-signal__case.kebab="$bar + $baz"></div>
```

--------------------------------

### Rocket Component Implementation

Source: https://data-star.dev/examples/rocket_starfield

Defines the star-field component using the datastar rocket API, including property validation, animation logic, and canvas rendering.

```javascript
  1import { rocket } from 'datastar'
  2
  3rocket('star-field', {
  4  mode: 'light',
  5  props: ({ number }) => ({
  6    starCount: number.min(1).default(500),
  7    speed: number.clamp(1, 100).default(50),
  8    centerX: number.clamp(0, 100).default(50),
  9    centerY: number.clamp(0, 100).default(50),
 10  }),
 11  onFirstRender({ refs, cleanup, host, observeProps, props }) {
 12    let aid = 0
 13    let ro
 14    let stars = []
 15    let last = 0
 16    let count = props.starCount
 17    let canvas
 18    let ctx
 19    let bg = '#000'
 20    let strokeStyles = []
 21
 22    const reset = () => {
 23      if (!canvas) return
 24      const {
 25        clientWidth: width = innerWidth,
 26        clientHeight: height = innerHeight,
 27      } = canvas.parentElement ?? {}
 28      canvas.width = width
 29      canvas.height = height
 30      stars = Array.from({ length: props.starCount }, () => {
 31        const x = Math.random() * width,
 32          y = Math.random() * height
 33        return { fx: x, fy: y, tx: x, ty: y, b: (Math.random() * 100) | 0 }
 34      })
 35    }
 36
 37    const animate = (now = 0) => {
 38      if (!canvas || !ctx) return
 39      const { width, height } = canvas
 40      const centerX = (width * props.centerX) / 100
 41      const centerY = (height * props.centerY) / 100
 42      const dt = last ? (now - last) / 1000 : 0
 43      const velocity = (1 + (8 * (props.speed - 1)) / 99) * dt * 0.5
 44      const max = Math.min(width, height) * 0.1
 45      const buckets = {}
 46
 47      last = now
 48      ctx.clearRect(0, 0, width, height)
 49      ctx.fillStyle = bg
 50      ctx.fillRect(0, 0, width, height)
 51
 52      for (const star of stars) {
 53        star.fx = star.tx
 54        star.fy = star.ty
 55        star.tx += Math.max(-max, Math.min(max, (star.tx - centerX) * velocity))
 56        star.ty += Math.max(-max, Math.min(max, (star.ty - centerY) * velocity))
 57        star.b = Math.min(100, star.b + 1)
 58
 59        if (star.fx < 0 || star.fx > width || star.fy < 0 || star.fy > height) {
 60          star.tx = star.fx = Math.random() * width
 61          star.ty = star.fy = Math.random() * height
 62          star.b = (Math.random() * 100) | 0
 63          continue
 64        }
 65
 66        const bucket = (star.b / 10) | 0
 67        ;(buckets[bucket] ??= new Path2D()).moveTo(star.fx, star.fy)
 68        buckets[bucket].lineTo(star.tx, star.ty)
 69      }
 70
 71      ctx.lineWidth = 1
 72      for (const bucket in buckets) {
 73        ctx.strokeStyle = strokeStyles[bucket]
 74        ctx.stroke(buckets[bucket])
 75      }
 76
 77      aid = requestAnimationFrame(animate)
 78    }
 79
 80    canvas = refs.canvas
 81    ctx = canvas?.getContext('2d', {
 82      alpha: true,
 83      antialias: true,
 84      optimizeSpeed: true,
 85      willReadFrequently: false,
 86    })
 87    if (!canvas || !ctx) return
 88
 89    canvas.removeAttribute('width')
 90    canvas.removeAttribute('height')
 91
 92    const style = getComputedStyle(host)
 93    bg = style.backgroundColor
 94    strokeStyles = Array.from(
 95      { length: 10 },
 96      (_, i) => `color-mix(in srgb, ${style.color}, ${bg} ${i * 10}%)`,
 97    )
 98
 99    reset()
100    animate()
101    ro = new ResizeObserver(reset)
102    ro.observe(canvas.parentElement || canvas)
103
104    observeProps(() => {
105      if (props.starCount === count) return
106      count = props.starCount
107      reset()
108    }, 'starCount')
109
110    cleanup(() => {
111      cancelAnimationFrame(aid)
112      ro?.disconnect()
113    })
114  },
115  render: ({ html }) => html`
116    <style>
117      .rocket-starfield {
118        display: block;
119        width: 100%;
120        height: 100%;
121      }
122
123      canvas {
124        display: block;
125        width: 100%;
126        height: 100%;
127      }
128    </style>
129
130    <div class="rocket-starfield">
131      <canvas data-ref:canvas data-ignore-morph></canvas>
132    </div>
133  `,
134})
```

--------------------------------

### Handle Mouse Wheel for Zooming

Source: https://data-star.dev/examples/rocket_flow

Adjusts the viewport zoom level based on mouse wheel events. It calculates the next zoom level, ensuring it stays within defined bounds, and adjusts the viewport center to keep the mouse pointer focused. The 'schedule()' function is called to trigger a re-render after zoom.

```javascript
const handleWheel = (evt) => {
      evt.preventDefault()
      if (!svg) return
      const rect = svg.getBoundingClientRect()
      const zoom = metrics.zoom
      const nextZoom = clampZoom(zoom * 1.2 ** (-evt.deltaY / 120))
      if (nextZoom === zoom) return
      const px = evt.clientX - rect.left
      const py = evt.clientY - rect.top
      const focusX = metrics.minX + (px / rect.width) * metrics.worldWidth
      const focusY = metrics.minY + (py / rect.height) * metrics.worldHeight
      const nextWorldWidth = metrics.screenWidth / nextZoom
      const nextWorldHeight = metrics.screenHeight / nextZoom
      const minX = focusX - (px / rect.width) * nextWorldWidth
      const minY = focusY - (py / rect.height) * nextWorldHeight
      viewport = [
        minX + nextWorldWidth / 2,
        minY + nextWorldHeight / 2,
        nextZoom,
      ]
      schedule()
    }
```

--------------------------------

### Patch DOM elements with Node.js

Source: https://data-star.dev/guide/getting_started

Uses the ServerSentEventGenerator to stream updates via a response object.

```javascript
// Creates a new `ServerSentEventGenerator` instance (this also sends required headers)
ServerSentEventGenerator.stream(req, res, (stream) => {
    // Patches elements into the DOM.
    stream.patchElements(`<div id="hal">I’m sorry, Dave. I’m afraid I can’t do that.</div>`);

    setTimeout(() => {
        stream.patchElements(`<div id="hal">Waiting for an order...</div>`);
    }, 1000);
});
```

--------------------------------

### Define Rocket QR Code Component

Source: https://data-star.dev/examples/rocket_qr_code

Register the qr-code component using the rocket function, defining props for validation and an onFirstRender hook to manage the canvas lifecycle.

```javascript
import { rocket } from 'datastar'

const qrCreator = (
  await import('https://cdn.jsdelivr.net/npm/qr-creator@1.0.0/+esm')
).default

const isHex = (value) => /^#[\da-f]{6}$/i.test(String(value ?? ''))
const getErrorText = ({ text, size, colorDark, colorLight }) =>
  [
    !text && 'Text is required',
    (size < 50 || size > 1000) && 'Size must be 50-1000px',
    (!isHex(colorDark) || !isHex(colorLight)) &&
      'Colors must be valid hex codes',
  ]
    .filter(Boolean)
    .join(', ')

rocket('qr-code', {
  props: ({ string, number, oneOf }) => ({
    text: string.trim.default('Hello World'),
    size: number.clamp(50, 1000).default(200),
    errorLevel: oneOf('L', 'M', 'Q', 'H').default('L'),
    colorDark: string.trim.upper.prefix('#').maxLength(7).default('#000000'),
    colorLight: string.trim.upper.prefix('#').maxLength(7).default('#FFFFFF'),
  }),
  onFirstRender({ refs, observeProps, props }) {
    const renderQR = () => {
      if (!(refs.canvas instanceof HTMLCanvasElement) || getErrorText(props))
        return
      qrCreator.render(
        {
          text: props.text,
          radius: 0,
          ecLevel: props.errorLevel,
          fill: props.colorDark,
          background: props.colorLight,
          size: props.size,
        },
        refs.canvas,
      )
    }

    renderQR()
    observeProps(renderQR)
  },
  render: ({ html, props: { text, size, colorDark, colorLight } }) => html`
    <style>
      :host {
        display: inline-flex;
        width: ${size}px;
        height: ${size}px;
        align-items: center;
        justify-content: center;
        position: relative;
      }

      canvas {
        display: block;
      }

      .qr-error {
        font-weight: bold;
        text-align: center;
      }
    </style>

    ${
      getErrorText({ text, size, colorDark, colorLight })
        ? html`<div class="qr-error">${getErrorText({ text, size, colorDark, colorLight })}</div>`
        : html`<canvas data-ref:canvas data-ignore-morph></canvas>`

}
  `,
})
```

--------------------------------

### data-show

Source: https://data-star.dev/reference/attributes

Shows or hides an element based on whether an expression evaluates to true or false.

```APIDOC
## data-show

### Description
Shows or hides an element based on whether an expression evaluates to `true` or `false`. For anything with custom requirements, use `data-class` instead.

### Method
N/A (Attribute-based)

### Endpoint
N/A

### Parameters
#### Attributes
- **data-show** (expression) - Required - The expression to evaluate for showing or hiding the element.

### Request Example
```html
<div data-show="$foo"></div>
<div data-show="$foo" style="display: none"></div>
```

### Response
N/A (Attribute-based behavior)
```

--------------------------------

### Send Multiple SSE Events

Source: https://data-star.dev/guide/backend_requests

Send multiple Server-Sent Events, including patch elements and patch signals, in a single response using Datastar's SSE syntax.

```datastar
(d*/patch-elements! sse "<div id=\"question\">...</div>")
(d*/patch-elements! sse "<div id=\"instructions\">...</div>")
(d*/patch-signals! sse "{answer: '...', prize: '...'}")
```

--------------------------------

### createCodec

Source: https://data-star.dev/reference/rocket

Defines a custom codec by providing decode and encode functions to normalize input and reflect values back to attribute text.

```APIDOC
## createCodec

### Description
Creates a new codec that Rocket uses to turn a plain decode/encode pair into a prop codec. If decode throws, Rocket logs a warning and falls back to the codec's default value.

### Request Body
- **decode** (function) - Required - Normalizes input from unknown types to the target type T.
- **encode** (function) - Required - Reflects the value T back to attribute text.

### Request Example
```javascript
let myCodec = createCodec({
  decode(value) {
    // normalize input
  },
  encode(value) {
    // reflect back to attribute text
  },
})
```
```

--------------------------------

### Setting multiple CSS styles with data-style

Source: https://data-star.dev/reference/attributes

Set multiple CSS properties simultaneously using a JavaScript object notation or JSON within the `data-style` attribute.

```html
<div data-style="{
   display: $hiding ? 'none' : 'flex',
   'background-color': $red ? 'red' : 'green'
}"></div>
```

--------------------------------

### Use Intersection Observer

Source: https://data-star.dev/reference/attributes

Triggers an expression when an element enters the viewport.

```html
<div data-on-intersect="$intersected = true"></div>
```

--------------------------------

### Patching Elements with Clojure SDK

Source: https://data-star.dev/guide/getting_started

Utilize the patch-elements! function within a Ring handler to stream updates to the client.

```clojure
 1;; Import the SDK's api and your adapter
 2(require
 3 '[starfederation.datastar.clojure.api :as d*]
 4 '[starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]])
 5
 6;; in a ring handler
 7(defn handler [request]
 8  ;; Create an SSE response
 9  (->sse-response request
10                  {on-open
11                   (fn [sse]
12                     ;; Patches elements into the DOM
13                     (d*/patch-elements! sse
14                                         "<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>")
15                     (Thread/sleep 1000)
16                     (d*/patch-elements! sse
17                                         "<div id=\"hal\">Waiting for an order...</div>"))}))
```

--------------------------------

### Lazy Loaded Content

Source: https://data-star.dev/examples/lazy_load

The target element that replaces the initial loading state once the request completes.

```html
<div id="graph">
    <img src="/images/examples/tokyo.png" />
</div>
```

--------------------------------

### Send SSE Events with PHP Datastar SSE

Source: https://data-star.dev/guide/backend_requests

Utilize the SSE object in PHP to patch elements and signals. Signals can be passed as an associative array.

```php
$sse->patchElements('<div id="question">...</div>');
$sse->patchElements('<div id="instructions">...</div>');
$sse->patchSignals(['answer' => '...', 'prize' => '...']);
```

--------------------------------

### Define a Custom Element with Rocket

Source: https://data-star.dev/docs.md

Use the `rocket` function to define a custom element. The first argument is the unique tag name, and the second is the definition object.

```typescript
rocket('demo-user-card', {
  props: ({ string }) => ({
    name: string.default('Anonymous'),
  }),
  render({ html, props: { name } }) {
    return html`<p>${name}</p>`
  },
})
```

--------------------------------

### Class Name Casing with Modifier

Source: https://data-star.dev/reference/attributes

Use the `__case.camel` modifier with `data-class` to convert the class name to camel case based on the signal's value.

```html
1<div data-class:my-class__case.camel="$foo"></div>
```

--------------------------------

### Run Expression on RequestAnimationFrame

Source: https://data-star.dev/reference/attributes

Executes an expression on every requestAnimationFrame event. Useful for animations or continuously updating values.

```html
<div data-on-raf="$count++"></div>
```

--------------------------------

### Java SSE Patch Signals

Source: https://data-star.dev/docs.md

Uses the ServerSentEventGenerator to send patch signals in Java, including a thread sleep for a delay between updates.

```java
import starfederation.datastar.utils.ServerSentEventGenerator;

// Creates a new `ServerSentEventGenerator` instance.
AbstractResponseAdapter responseAdapter = new HttpServletResponseAdapter(response);
ServerSentEventGenerator generator = new ServerSentEventGenerator(responseAdapter);

// Patches signals.
generator.send(PatchSignals.builder()
    .data("{\"hal\": \"Affirmative, Dave. I read you.\"}")
    .build()
);

Thread.sleep(1000);

generator.send(PatchSignals.builder()
    .data("{\"hal\": \"...\"}")
    .build()
);
```

--------------------------------

### Toggle Boolean Signals with @toggleAll()

Source: https://data-star.dev/reference/actions

The @toggleAll() action inverts the boolean value of signals that match a provided filter. It supports include and exclude regular expressions for precise targeting.

```html
<!-- Toggles the `foo` signal only -->
<div data-signals:foo="false">
    <button data-on:click="@toggleAll({include: /^foo$/})"></button>
</div>
```

```html
<!-- Toggles all signals starting with `is` -->
<div data-signals="{isOpen: false, isActive: true, isEnabled: false}">
    <button data-on:click="@toggleAll({include: /^is/})"></button>
</div>
```

```html
<!-- Toggles signals starting with `settings.` -->
<div data-signals="{settings: {darkMode: false, autoSave: true}}">
    <button data-on:click="@toggleAll({include: /^settings\./})"></button>
</div>
```

--------------------------------

### Observe Prop Changes for Imperative Actions

Source: https://data-star.dev/docs.md

The `observeProps` function allows you to react to changes in specific props or all props. The callback receives the current props and an object detailing which props have changed, enabling targeted imperative updates.

```typescript
rocket('demo-video-frame', {
  props: ({ string, number }) => ({
    src: string.trim,
    currentTime: number.min(0),
  }),
  mode: 'light',
  renderOnPropChange: false,
  onFirstRender({ refs, observeProps }) {
    observeProps((props, changes) => {
      if (!(refs.video instanceof HTMLVideoElement)) {
        return
      }
      if ('src' in changes) {
        refs.video.src = props.src
      }
      if ('currentTime' in changes) {
        refs.video.currentTime = props.currentTime
      }
    })
  },
  render({ html, props: { src } }) {
    return html`<video data-ref:video controls src="${src}"></video>`
  },
})
```

--------------------------------

### Conditional Branch Rendering

Source: https://data-star.dev/examples/rocket_conditional

Use ternary operators with the `html` tag to conditionally render different DOM branches based on a step variable. Each branch is a distinct DOM subtree.

```javascript
step === 1
            ? html`
                <div data-branch="loading">
                  <strong>Loading</strong>
                  <p>
                    The component can stay prop-driven while still swapping whole
                    branches in and out of the DOM.
                  </p>
                </div>
              `
            : html`
                <div data-branch="ready">
                  <strong>Ready</strong>
                  <p>
                    The fallback branch mounts fresh after earlier branches unmount.
                  </p>
                </div>
              `
```

--------------------------------

### Execute JavaScript Response

Source: https://data-star.dev/guide/datastar_expressions

Executes JavaScript directly when the response content-type is text/javascript.

```javascript
alert('This mission is too important for me to allow you to jeopardize it.')
```

--------------------------------

### Kotlin: Data Class for Offset Signals

Source: https://data-star.dev/how_tos/load_more_list_items

Defines a data class to represent offset signals, used for managing pagination state. This is typically used on the server-side to deserialize incoming signal data.

```kotlin
1@Serializable
2data class OffsetSignals(
3    val offset: Int,
4)
5
6val signals =
7    readSignals(
8        request,
9        { json: String -> Json.decodeFromString<OffsetSignals>(json) },
10    )
11
12val max = 5
13val limit = 1
14val offset = signals.offset
15
16val generator = ServerSentEventGenerator(response)
17
18if (offset < max) {

```

--------------------------------

### Patch DOM Elements with Server-Sent Events (Scala)

Source: https://data-star.dev/docs.md

Use ServerSentEventGenerator to patch elements into the DOM. Includes a delay between patches.

```scala
val generator = ServerSentEventGenerator(response)

generator.patchElements(
    elements = """<div id=\"hal\">I’m sorry, Dave. I’m afraid I can’t do that.</div>""",
)

Thread.sleep(ONE_SECOND)

generator.patchElements(
    elements = """<div id=\"hal\">Waiting for an order...</div>""",
)
```

--------------------------------

### Defining Nested Signals

Source: https://data-star.dev/docs.md

Signals can be structured using dot-notation or object syntax to manage complex state.

```html
<div data-signals:foo.bar="1"></div>
```

```html
<div data-signals="{foo: {bar: 1}}"></div>
```

--------------------------------

### Dynamic Polling Frequency in Kotlin

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses ServerSentEventGenerator to patch elements with a dynamic interval.

```kotlin
 1val now: LocalDateTime = currentTime()
 2val currentSeconds = now.second
 3val duration = if (currentSeconds < 50) 5 else 1
 4
 5val generator = ServerSentEventGenerator(response)
 6
 7generator.patchElements(
 8    elements =
 9        """
10        <div id="time" data-on-interval__duration.${duration}s="@get('/endpoint')">
11            $now
12        </div>
13        """.trimIndent(),
14)
```

--------------------------------

### Event Bubbling with Dynamic IDs

Source: https://data-star.dev/how_tos/keep_datastar_code_dry

Enhances event bubbling by capturing a data attribute (e.g., 'data-id') from the clicked button and including it in the backend action. This allows for context-specific actions.

```html
<div data-on:click="evt.target.tagName == 'BUTTON'
    && ($id = evt.target.dataset.id)
    && @get('/endpoint')">
    <button data-id="1">Click me</button>
    <button data-id="2">No, click me!</button>
    <button data-id="3">Click us all!</button>
</div>
```

--------------------------------

### Multi-line Datastar Expression

Source: https://data-star.dev/docs.md

Executes multiple statements within a Datastar expression that spans multiple lines. Statements must be separated by semicolons, as line breaks alone are not sufficient.

```html
<div data-signals:foo="1">
    <button data-on:click="
        $landingGearRetracted = true;
        @post('/launch')
    ">
        Force launch
    </button>
</div>
```

--------------------------------

### Binary Prop Decoders

Source: https://data-star.dev/reference/rocket

Decode base64 strings into Uint8Array for binary data handling.

```javascript
props: ({ bin }) => ({
  payload: bin,
})
```

--------------------------------

### Custom Element Binding with Property and Event Modifiers

Source: https://data-star.dev/reference/attributes

Bind to a custom element's specific property (`__prop.checked`) and sync back on a specific event (`__event.change`).

```html
1<my-toggle data-bind:is-checked__prop.checked__event.change></my-toggle>
```

--------------------------------

### JSON Codec

Source: https://data-star.dev/docs.md

Details on the `json` codec for parsing JSON text and cloning structured values.

```APIDOC
## `json`

`json` parses JSON text and clones structured values so instances do not share mutable default objects by accident.

Without an explicit `.default(...)`, the zero value is an empty object .

| Member | Effect | Typical use |
|---|---|---|
| `.default(value)` | Supplies a fallback object or array. | Payloads, chart series, settings blobs, filter state. |

```javascript
props: ({ json }) => ({
  series: json.default(() => []),
  options: json.default(() => ({ stacked: false, legend: true })),
})
```
```

--------------------------------

### Edge Selection Logic

Source: https://data-star.dev/examples/rocket_flow

Applies CSS classes to edges based on selection state and clears the current selection.

```javascript
const applyEdgeSelectionClasses = () => {
  edgesLayer?.querySelectorAll('.flow-edge').forEach((group) => {
    const selected = group.dataset.edgeKey === selectedEdgeKey
    group.classList.toggle('is-selected', selected)
    if (
      !selected &&
      group.dataset.edgeKey !== host.getAttribute('pending-edge')
    ) {
      group.classList.remove('is-pending')
    }
  })
}

const clearSelectedEdge = () => {
  if (!selectedEdgeKey) return
  selectedEdgeKey = null
```

--------------------------------

### Multi-line Datastar Expressions

Source: https://data-star.dev/guide/datastar_expressions

Datastar expressions can span multiple lines, but semicolons are required to separate statements. Line breaks alone are not sufficient.

```html
1<div data-signals:foo="1">
2    <button data-on:click="
3        $landingGearRetracted = true;
4        @post('/launch')
5    ">
6        Force launch
7    </button>
8</div>
```

--------------------------------

### JavaScript Response Headers

Source: https://data-star.dev/reference/actions

When returning JavaScript (text/javascript), DataStar allows setting script attributes via a response header.

```APIDOC
## JavaScript Response Headers

### Description
When returning JavaScript (`text/javascript`), the server can optionally include a response header to set attributes on the injected script element.

### Response Headers
- **`datastar-script-attributes`** (string) - Sets the script element’s attributes using a JSON encoded string.

### Request Example
```javascript
response.headers.set('Content-Type', 'text/javascript')
response.headers.set('datastar-script-attributes', JSON.stringify({ type: 'module' }))
response.body = 'console.log("Hello from server!");'
```
```

--------------------------------

### Dynamic Polling Frequency in Node.js

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

Uses ServerSentEventGenerator to stream patched elements.

```javascript
 1import { createServer } from "node:http";
 2import { ServerSentEventGenerator } from "../npm/esm/node/serverSentEventGenerator.js";
 3
 4const server = createServer(async (req, res) => {
 5  const currentTime = new Date();
 6  const duration = currentTime.getSeconds > 50 ? 5 : 1;
 7
 8  ServerSentEventGenerator.stream(req, res, (sse) => {
 9    sse.patchElements(`
```

--------------------------------

### Default Request Cancellation

Source: https://data-star.dev/reference/actions

Shows the default behavior where rapid clicks on a button cancel previous pending requests.

```html
1<!-- Clicking this button multiple times will cancel previous requests (default behavior) -->
2<button data-on:click="@get('/slow-endpoint')">Load Data</button>
```

--------------------------------

### Multiple Conditional Class Binding

Source: https://data-star.dev/reference/attributes

Apply multiple classes to an element based on different expressions using a key-value pair object with `data-class`.

```html
1<div data-class="{success: $foo != '', 'font-bold': $foo == 'strong'}"></div>
```

--------------------------------

### data-on-signal-patch-filter

Source: https://data-star.dev/reference/attributes

Filters which signals to watch when using the data-on-signal-patch attribute.

```APIDOC
## data-on-signal-patch-filter

### Description
Filters which signals to watch when using the `data-on-signal-patch` attribute. The attribute accepts an object with `include` and/or `exclude` properties that are regular expressions.

### Method
N/A (Attribute-based)

### Endpoint
N/A

### Parameters
#### Attributes
- **data-on-signal-patch-filter** (object) - Required - An object with `include` and/or `exclude` properties that are regular expressions.

### Request Example
```html
<!-- Only react to counter signal changes -->
<div data-on-signal-patch-filter="{include: /^counter$/}"></div>

<!-- React to all changes except those ending with "changes" -->
<div data-on-signal-patch-filter="{exclude: /changes$/}"></div>

<!-- Combine include and exclude filters -->
<div data-on-signal-patch-filter="{include: /user/, exclude: /password/}"></div>
```

### Response
N/A (Attribute-based behavior)
```

--------------------------------

### Persist Signal in Local Storage

Source: https://data-star.dev/reference/attributes

Persists signal values in the browser's local storage, allowing them to be retained between page loads. By default, signals are stored under the 'datastar' key.

```html
<div data-persist></div>
```

--------------------------------

### Datastar Text Plugin: Invalid Attribute Key

Source: https://data-star.dev/errors/key_not_allowed?metadata=%7B%22plugin%22%3A%7B%22name%22%3A%22text%22%2C%22type%22%3A%22attribute%22%7D%2C%22element%22%3A%7B%22id%22%3A%22%22%2C%22tag%22%3A%22DIV%22%7D%2C%22expression%22%3A%7B%22rawKey%22%3A%22textFoo%22%2C%22key%22%3A%22foo%22%2C%22value%22%3A%22%22%2C%22fnContent%22%3A%22%22%7D%7D

Attribute keys are not permitted for the text plugin. This error arises when attempting to use an attribute key within the text attribute.

```html
1<div data-text-foo=""></div>
```

--------------------------------

### Define Rocket Flow Container Component

Source: https://data-star.dev/examples/rocket_flow

Defines the 'flow-container' component using the 'rocket' function, specifying its properties and initial render logic.

```javascript
rocket('flow-container', {
  props: ({ array, number, date }) => ({
    viewport: array(number, number, number).default([0, 0, 1]),
    grid: number.min(1).default(32),
    serverUpdateTime: date.default(() => new Date()),
  }),
  onFirstRender({ cleanup, host, observeProps, props, refs }) {
    host.style.display = 'block'
    host.style.position = 'relative'
    if (!host.hasAttribute('tabindex')) host.setAttribute('tabindex', '0')

    let svg
    let background
    let gridPattern
  }
})
```

--------------------------------

### Provide Selector for Form ContentType

Source: https://data-star.dev/errors/fetch_form_not_found

When using `contentType: 'form'` and the element is not within a form, provide a `selector` option to specify the form's ID or class. This ensures Datastar can find the correct form for submission.

```html
1<button data-on:click="@post('/endpoint', {contentType: 'form', selector: '#myform'})></button>
```

--------------------------------

### Stream SSE events in TypeScript/Node

Source: https://data-star.dev/guide/backend_requests

Uses the ServerSentEventGenerator to stream events to the client.

```typescript
1// Creates a new `ServerSentEventGenerator` instance (this also sends required headers)
2ServerSentEventGenerator.stream(req, res, (stream) => {
```

--------------------------------

### datastar-patch-elements SSE Event

Source: https://data-star.dev/reference/sse_events

Handles patching of DOM elements using Server-Sent Events. Supports various morphing modes and namespaces.

```APIDOC
## SSE Event: datastar-patch-elements

### Description
Patches one or more elements in the DOM. By default, Datastar morphs elements by matching top-level elements based on their ID.

### Method
Server-Sent Event

### Endpoint
N/A (Server-Sent Event)

### Parameters
#### SSE Data Lines
- **`selector`** (string) - Optional - Selects the target element of the patch using a CSS selector. Not required when using the `outer` or `replace` modes.
- **`mode`** (string) - Optional - Specifies the morphing mode. Defaults to `outer`.
  - `outer`: Morphs the outer HTML of the elements.
  - `inner`: Morphs the inner HTML of the elements.
  - `replace`: Replaces the outer HTML of the elements.
  - `prepend`: Prepends the elements to the target’s children.
  - `append`: Appends the elements to the target’s children.
  - `before`: Inserts the elements before the target as siblings.
  - `after`: Inserts the elements after the target as siblings.
  - `remove`: Removes the target elements from DOM.
- **`namespace`** (string) - Optional - Specifies the XML namespace for patching elements (e.g., `svg`, `mathml`).
- **`useViewTransition`** (boolean) - Optional - Whether to use view transitions when patching elements. Defaults to `false`.
- **`elements`** (string) - Required - The HTML elements to patch. Can span multiple lines.

### Request Example
```
event: datastar-patch-elements
data: elements <div id="foo">Hello world!</div>

```

### Response
#### Success Response
N/A (Server-Sent Event stream)

#### Response Example
```
event: datastar-patch-elements
data: elements <div id="foo">Hello world!</div>

```

### Additional Examples

**Removing an element:**
```
event: datastar-patch-elements
data: selector #foo
data: mode remove

```

**Patching with non-default options:**
```
event: datastar-patch-elements
data: selector #foo
data: mode inner
data: useViewTransition true
data: elements <div>
data: elements        Hello world!
data: elements </div>

```

**Patching SVG elements:**
```
event: datastar-patch-elements
data: namespace svg
data: elements <circle id="circle" cx="100" r="50" cy="75"></circle>

```
```

--------------------------------

### Add 3D Buildings Layer

Source: https://data-star.dev/examples/rocket_openfreemap

Adds a fill-extrusion layer for 3D buildings to the map. Ensure the map style is loaded before calling this function. It uses a source layer named 'building' and defines extrusion height based on zoom level.

```javascript
map.addLayer(
        {
          id: 'rocket-openfreemap-3d-buildings',
          type: 'fill-extrusion',
          source: buildingLayer.source,
          'source-layer': 'building',
          minzoom: 14,
          paint: {
            'fill-extrusion-color': '#b9b5ad',
            'fill-extrusion-base': 0,
            'fill-extrusion-height': [
              'interpolate',
              ['linear'],
              ['zoom'],
              14,
              0,
              16,
              40,
              18,
              90,
            ],
            'fill-extrusion-opacity': 0.8,
            'fill-extrusion-vertical-gradient': true,
          },
        },
        layers.find((layer) => layer.type === 'symbol')?.id
      )
```

--------------------------------

### PatchElements Event with Selector Target

Source: https://data-star.dev/errors/patch_elements_no_targets_found

Use this format when targeting an element using a CSS selector for a datastar-patch-elements event. Ensure the selector correctly identifies an existing element.

```yaml
1event: datastar-patch-elements
2data: selector #foo
3data: elements <div></div>
```

--------------------------------

### Handle Pointer Down for Viewport Dragging

Source: https://data-star.dev/examples/rocket_flow

Initiates dragging behavior when the left mouse button is pressed on the SVG or background. Captures pointer events to allow continuous dragging and updates the viewport accordingly. Ensures pointer capture is released and event listeners are removed on pointer up or cancel.

```javascript
const pointerDown = (evt) => {
      if (evt.button !== 0 || (evt.target !== svg && evt.target !== background))
        return
      console.log('[rocket/flow] viewport:pointerdown', {
        pointerId: evt.pointerId,
        target: evt.target instanceof Element ? evt.target.tagName : null,
      })
      clearSelectedEdge()
      evt.preventDefault()
      const origin = [...viewport]
      svg.classList.add('is-dragging')
      try {
        svg.setPointerCapture(evt.pointerId)
      } catch {}
      const move = (event) => {
        if (event.pointerId !== evt.pointerId) return
        const scale = 1 / origin[2]
        viewport = [
          origin[0] - (event.clientX - evt.clientX) * scale,
          origin[1] - (event.clientY - evt.clientY) * scale,
          origin[2],
        ]
        schedule()
      }
      const end = (event) => {
        if (event.pointerId !== evt.pointerId) return
        svg.classList.remove('is-dragging')
        try {
          svg.releasePointerCapture(evt.pointerId)
        } catch {}
        svg.removeEventListener('pointermove', move, true)
        svg.removeEventListener('pointerup', end, true)
        svg.removeEventListener('pointercancel', end, true)
      }
      svg.addEventListener('pointermove', move, true)
      svg.addEventListener('pointerup', end, true)
      svg.addEventListener('pointercancel', end, true)
    }
```

--------------------------------

### Filter Signal Patch Events

Source: https://data-star.dev/reference/attributes

Use `data-on-signal-patch-filter` with `include` or `exclude` regular expressions to specify which signal changes should trigger the `data-on-signal-patch` listener.

```html
<!-- Only react to counter signal changes -->
<div data-on-signal-patch-filter="{include: /^counter$/}"></div>
```

```html
<!-- React to all changes except those ending with "changes" -->
<div data-on-signal-patch-filter="{exclude: /changes$/}"></div>
```

```html
<!-- Combine include and exclude filters -->
<div data-on-signal-patch-filter="{include: /user/, exclude: /password/}"></div>
```

--------------------------------

### Define component props signature

Source: https://data-star.dev/reference/rocket

The type signature for the props definition function.

```typescript
props?: (codecs: CodecRegistry) => Defs
```

--------------------------------

### @intl() Helper Function

Source: https://data-star.dev/reference/actions

The @intl() function formats values based on type, options, and locale. It supports datetime, number, pluralRules, relativeTime, list, and displayNames formatting.

```APIDOC
## @intl() Helper Function

### Description
Provides internationalized, locale-aware formatting for dates, numbers, and other values using the Intl namespace object.

### Method
N/A (Helper function, not an API endpoint)

### Endpoint
N/A

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A

### Parameters
- **type** (string) - Required - Specifies the type of value to format. Possible values: `datetime`, `number`, `pluralRules`, `relativeTime`, `list`, `displayNames`.
- **value** (any) - Required - The value to be formatted.
- **options** (Record<string, any>) - Optional - Formatting options, specific to the `type` parameter (e.g., `Intl.DateTimeFormatOptions`, `Intl.NumberFormatOptions`).
- **locale** (string | string[]) - Optional - The locale or locales to use for formatting.

### Request Example
```html
<!-- Converts a number to a formatted USD currency string in the user’s locale -->
<div data-text="@intl('number', 1000000, {style: 'currency', currency: 'USD'})"></div>

<!-- Converts a date to a formatted string in the specified locale -->
<div data-text="@intl('datetime', new Date(), {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'}, 'de-AT')"></div>
```

### Response
#### Success Response (Formatted Value)
- **formattedValue** (string) - The locale-aware formatted string.

#### Response Example
```json
{
  "formattedValue": "$1,000,000.00"
}
```

#### Error Handling
- If invalid `type` or `options` are provided, an error may be thrown or an empty string returned depending on the browser's Intl implementation.
```

--------------------------------

### data-bind Attribute

Source: https://data-star.dev/reference

The `data-bind` attribute creates a two-way data binding between a signal and an element's bound state. It syncs signal changes to the element and element changes back to the signal.

```APIDOC
## `data-bind` Attribute

### Description
Creates a signal (if one doesn’t already exist) and sets up two-way data binding between it and an element’s current bound state. When the signal changes, Datastar writes that value to the element. When one of the bind events fires, Datastar reads the element’s current bound property/value and writes that back to the signal.

The `data-bind` attribute can be placed on any HTML element on which data can be input or choices selected (`input`, `select`, `textarea` elements, and web components). Native elements use their built-in bind semantics automatically. Generic custom elements default to binding through `value` and listening on `change`.

`data-bind` does **not** inspect the event payload. It only uses the configured event as a signal to re-read the element’s current bound property/value. If you need to pull data from `event` itself, use `data-on:*` instead.

### Method
N/A (Attribute)

### Endpoint
N/A

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A

### Request Example
```html
1<input data-bind:foo />
```

```html
1<input data-bind="foo" />
```

Attribute casing rules apply to the signal name.

```html
1<!-- Both of these create the signal `$fooBar` -->
2<input data-bind:foo-bar />
3<input data-bind="fooBar" />
```

The initial value of the signal is set to the value of the element, unless a signal has already been defined. So in the example below, `$fooBar` is set to `baz`.

```html
1<input data-bind:foo-bar value="baz" />
```

Whereas in the example below, `$fooBar` inherits the value `fizz` of the predefined signal.

```html
1<div data-signals:foo-bar="'fizz'">
2    <input data-bind:foo-bar value="baz" />
3</div>
```

#### Predefined Signal Types
When you predefine a signal, its **type** is preserved during binding. Whenever the element’s value changes, the signal value is automatically converted to match the original type.
For example, in the code below, `$fooBar` is set to the **number** `10` (not the string "10") when the option is selected.

```html
1<div data-signals:foo-bar="0">
2    <select data-bind:foo-bar>
3        <option value="10">10</option>
4    </select>
5</div>
```

In the same way, you can assign multiple input values to a single signal by predefining it as an **array**. In the example below, `$fooBar` becomes `["fizz", "baz"]` when both checkboxes are checked, and `["", ""]` when neither is checked.

```html
1<div data-signals:foo-bar="[]">
2    <input data-bind:foo-bar type="checkbox" value="fizz" />
3    <input data-bind:foo-bar type="checkbox" value="baz" />
4</div>
```

#### File Uploads
Input fields of type `file` will automatically encode file contents in base64. This means that a form is not required.

```html
1<input type="file" data-bind:files multiple />
```

The resulting signal is in the format `{ name: string, contents: string, mime: string }[]`. See the file upload example.
> If you want files to be uploaded to the server, rather than be converted to signals, use a form and with `multipart/form-data` in the `enctype` attribute. See the backend actions reference.

### Response
#### Success Response (200)
N/A

#### Response Example
N/A
```

--------------------------------

### Access Signal Properties with Datastar Expression

Source: https://data-star.dev/docs.md

Retrieves the length property of the 'foo' signal using a Datastar expression. This demonstrates accessing properties of signals within expressions.

```html
<div data-text="$foo.length"></div>
```

--------------------------------

### data-class

Source: https://data-star.dev/reference/attributes

Adds or removes a class to or from an element based on an expression.

```APIDOC
### `data-class`

Adds or removes a class to or from an element based on an expression.

#### Example Usage
```html
<div data-class:font-bold="$foo == 'strong'"></div>
```

If the expression evaluates to `true`, the `hidden` class is added to the element; otherwise, it is removed.

The `data-class` attribute can also be used to add or remove multiple classes from an element using a set of key-value pairs, where the keys represent class names and the values represent expressions.

#### Example Usage
```html
<div data-class="{success: $foo != '', 'font-bold': $foo == 'strong'}"></div>
```

#### Modifiers
Modifiers allow you to modify behavior when defining a class name using a key.

* `__case` – Converts the casing of the class.
  * `.camel` – Camel case: `myClass`
  * `.kebab` – Kebab case: `my-class` (default)
  * `.snake` – Snake case: `my_class`
  * `.pascal` – Pascal case: `MyClass`

#### Example Usage
```html
<div data-class:my-class__case.camel="$foo"></div>
```
```

--------------------------------

### Enable Node Dragging

Source: https://data-star.dev/examples/rocket_flow

Adds event listeners to a node's group element to enable dragging functionality. It captures pointer events and updates the node's position during drag.

```javascript
const enableNodeDrag = (entry) => {
      if (!entry.group || dragEnabledGroups.has(entry.group) || !svg) return
      dragEnabledGroups.add(entry.group)
      const root = svg.ownerDocument?.defaultView ?? window
      entry.group.addEventListener('pointerdown', (evt) => {
        if (evt.button !== 0) return
        console.log('[rocket/flow] node:pointerdown', {
          pointerId: evt.pointerId,
          id: entry.id,
          target: evt.target instanceof Element ? evt.target.tagName : null,
        })
        evt.preventDefault()
        evt.stopPropagation()
        const pointerId = evt.pointerId
        const drag = {
          pointerId,
          startX: entry.x,
          startY: entry.y,
          startClientX: evt.clientX,
          startClientY: evt.clientY,
        }
        activeNodeDrags.set(pointerId, drag)
        try {
          entry.group.setPointerCapture(pointerId)
        } catch {}
        entry.group.classList.add('is-dragging')
        entry.group.style.cursor = 'grabbing'
        emitNodeEvent(entry, 'flow-node-drag-start', {
          pointerId,
          origin: { x: drag.startX, y: drag.startY },
        })

        const move = (event) => {

```

--------------------------------

### Access Signals Without Subscription with @peek()

Source: https://data-star.dev/reference/actions

Use @peek() within expressions to access signal values without causing re-evaluation when the accessed signal changes. This is useful for optimizing expression updates.

```html
<div data-text="$foo + @peek(() => $bar)"></div>
```

--------------------------------

### Edge Update and Removal Event Handlers

Source: https://data-star.dev/examples/rocket_flow

Logic for processing edge updates from custom events and cleaning up edge references upon removal.

```javascript
      const entry = edges.get(target)
      if (!entry) return
      const detail =
        /** @type {CustomEvent<Record<string, any>>} */ (evt).detail ?? {}
      entry.sourceId = (
        detail.source ??
        detail.sourceId ??
        target.getAttribute('source') ??
        ''
      ).trim()
      entry.targetId = (
        detail.target ??
        detail.targetId ??
        target.getAttribute('target') ??
        ''
      ).trim()
      entry.label = detail.label ?? target.getAttribute('label') ?? ''
      entry.animated = Boolean(
        detail.animated ?? target.hasAttribute('animated'),
      )
      entry.id = (detail.id ?? target.getAttribute('id') ?? '').trim()
      registerEdgeEntry(entry)
      scheduleEdgeRender()
    }

    const onEdgeRemove = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
      const entry = edges.get(target)
      if (entry?.key && edgesByKey.get(entry.key) === entry)
        edgesByKey.delete(entry.key)
      entry?.group?.remove()
      edges.delete(target)
      if (entry?.key === selectedEdgeKey) clearSelectedEdge()
      scheduleEdgeRender()
    }
```

--------------------------------

### Update Viewport Metrics and Render

Source: https://data-star.dev/examples/rocket_flow

Calculates and updates screen and world metrics based on the current viewport and SVG dimensions. Dispatches a 'viewport-change' event if the viewport signature has changed. This function should be called whenever the viewport needs to be recalculated and potentially re-rendered.

```javascript
frame = 0
        const [cx, cy, zoom] = viewport
        const rect = svg.getBoundingClientRect()
        metrics.screenWidth = Math.max(1, rect.width)
        metrics.screenHeight = Math.max(1, rect.height)
        metrics.zoom = zoom
        metrics.worldWidth = metrics.screenWidth / zoom
        metrics.worldHeight = metrics.screenHeight / zoom
        metrics.minX = cx - metrics.worldWidth / 2
        metrics.minY = cy - metrics.worldHeight / 2
        svg.setAttribute(
          'viewBox',
          `${metrics.minX} ${metrics.minY} ${metrics.worldWidth} ${metrics.worldHeight}`,
        )
        background.setAttribute('x', String(metrics.minX))
        background.setAttribute('y', String(metrics.minY))
        background.setAttribute('width', String(metrics.worldWidth))
        background.setAttribute('height', String(metrics.worldHeight))
        const spacing = Math.max(4, grid)
        gridPattern.setAttribute('width', String(spacing))
        gridPattern.setAttribute('height', String(spacing))
        gridPath.setAttribute('d', `M ${spacing} 0 L 0 0 0 ${spacing}`)
        gridPattern.removeAttribute('patternTransform')
        const signature = `${metrics.minX}|${metrics.minY}|${metrics.zoom}|${metrics.screenWidth}|${metrics.screenHeight}`
        if (signature !== lastSignature) {
          lastSignature = signature
          console.log('[rocket/flow] viewport:change', {
            viewport: [...viewport],
          })
          host.dispatchEvent(
            new CustomEvent('viewport-change', {
              detail: {
                viewport: [...viewport],
                screen: {
                  width: metrics.screenWidth,
                  height: metrics.screenHeight,
                },
                world: {
                  minX: metrics.minX,
                  minY: metrics.minY,
                  width: metrics.worldWidth,
                  height: metrics.worldHeight,
                },
              },
              bubbles: true,
              composed: true,
            }),
          )
        }
        renderNodes()
```

--------------------------------

### DELETE /endpoint

Source: https://data-star.dev/reference/actions

Sends a DELETE request to the specified URI.

```APIDOC
## DELETE /endpoint

### Description
Sends a DELETE request to the backend.

### Method
DELETE

### Endpoint
/endpoint

### Request Example
<button data-on:click="@delete('/endpoint')"></button>
```

--------------------------------

### Signal Inherits Predefined Value

Source: https://data-star.dev/reference

When a signal is predefined using `data-signals`, `data-bind` will inherit its value. Here, `$fooBar` inherits `fizz` from the predefined signal.

```html
<div data-signals:foo-bar="'fizz'">
    <input data-bind:foo-bar value="baz" />
</div>
```

--------------------------------

### Set Pending Edge State

Source: https://data-star.dev/examples/rocket_flow

Highlights a specific edge by adding the 'is-pending' class to it. Removes the highlight if no edgeKey is provided. Sets the 'pending-edge' attribute on the host.

```javascript
    const setPendingEdge = (edgeKey) => {
      if (!edgeKey) {
        clearPendingEdge()
        return
      }
      host.setAttribute('pending-edge', edgeKey)
      edgesLayer?.querySelectorAll('.flow-edge').forEach((group) => {
        group.classList.toggle('is-pending', group.dataset.edgeKey === edgeKey)
      })
    }
```

--------------------------------

### Forcing a Component Render with ctx.render

Source: https://data-star.dev/docs.md

Call `ctx.render` with an empty overrides object to force a component re-render. This is useful for coarse structural patches after async operations, not for high-frequency state updates.

```typescript
ctx.render({}, user, null)
```

--------------------------------

### Define SVG Namespace Constants

Source: https://data-star.dev/examples/rocket_flow

Constants for SVG namespaces used in DOM manipulation.

```javascript
const SVG_NS = 'http://www.w3.org/2000/svg'
const XLINK_NS = 'http://www.w3.org/1999/xlink'
const XML_NS = 'http://www.w3.org/XML/1998/namespace'
```

--------------------------------

### Apply signal modifiers

Source: https://data-star.dev/docs.md

Use modifiers to control signal casing, property binding, or event synchronization.

```html
<input data-bind:my-signal__case.kebab />
```

```html
<my-toggle data-bind:is-checked__prop.checked__event.change></my-toggle>
```

--------------------------------

### Intersection Observer (data-on-intersect)

Source: https://data-star.dev/docs.md

Runs an expression when the element intersects with the viewport, with modifiers to control trigger conditions and timing.

```APIDOC
## data-on-intersect

### Description
Runs an expression when the element enters or exits the viewport.

### Modifiers
- __once: Trigger only once.
- __exit: Trigger on exit.
- __half: Trigger when half visible.
- __full: Trigger when fully visible.
- __threshold: Trigger at specific percentage (.25, .75).
- __delay: Delay execution.
- __debounce: Debounce execution.
- __throttle: Throttle execution.
- __viewtransition: Wrap in document.startViewTransition().

### Request Example
<div data-on-intersect__once__full="$fullyIntersected = true"></div>
```

--------------------------------

### JSON Response Headers

Source: https://data-star.dev/reference/actions

For JSON responses (application/json), DataStar provides a header to conditionally patch signals.

```APIDOC
## JSON Response Headers

### Description
When returning JSON (`application/json`), the server can optionally include a response header to control conditional patching of signals.

### Response Headers
- **`datastar-only-if-missing`** (boolean) - If set to `true`, only patch signals that don’t already exist.

### Request Example
```javascript
response.headers.set('Content-Type', 'application/json')
response.headers.set('datastar-only-if-missing', 'true')
response.body = JSON.stringify({ foo: 'bar' })
```
```

--------------------------------

### Handling Scroll Events for Block Recycling

Source: https://data-star.dev/examples/rocket_virtual_scroll

Manages scroll events to recycle blocks of content as the user scrolls. It determines which blocks to load next based on the scroll direction and updates block positions accordingly.

```javascript
const handleScroll = (direction) => {
      if (isLoading) return
      const [above, visible, below] = blockPositions
      const recycleBlock = direction === 'down' ? above : below
      const referenceBlock = direction === 'down' ? below : above
      const newStartIndex =
        startIndexOf(referenceBlock) +
        (direction === 'down' ? props.bufferSize : -props.bufferSize)

      if (
        (direction === 'down' && newStartIndex >= props.totalItems) ||
        (direction === 'up' && newStartIndex < 0)
      ) {
        return
      }

      isLoading = true
      setStartIndex(recycleBlock, newStartIndex)
      blockPositions =
        direction === 'down' ? [visible, below, above] : [below, above, visible]
      loadBlock(newStartIndex, recycleBlock.toLowerCase())
      setTimeout(positionBlocks, 100)
      isLoading = false
    }
```

--------------------------------

### data-computed

Source: https://data-star.dev/reference/attributes

Creates a signal that is computed based on an expression.

```APIDOC
### `data-computed`

Creates a signal that is computed based on an expression. The computed signal is read-only, and its value is automatically updated when any signals in the expression are updated.

#### Example Usage
```html
<div data-computed:foo="$bar + $baz"></div>
```

Computed signals are useful for memoizing expressions containing other signals. Their values can be used in other expressions.

#### Example Usage
```html
<div data-computed:foo="$bar + $baz"></div>
<div data-text="$foo"></div>
```

> Computed signal expressions must not be used for performing actions (changing other signals, actions, JavaScript functions, etc.). If you need to perform an action in response to a signal change, use the `data-effect` attribute.

The `data-computed` attribute can also be used to create computed signals using a set of key-value pairs, where the keys represent signal names and the values are callables (usually arrow functions) that return a reactive value.

#### Example Usage
```html
<div data-computed="{foo: () => $bar + $baz}"></div>
```

#### Modifiers
Modifiers allow you to modify behavior when defining computed signals using a key.

* `__case` – Converts the casing of the signal name.
  * `.camel` – Camel case: `mySignal` (default)
  * `.kebab` – Kebab case: `my-signal`
  * `.snake` – Snake case: `my_signal`
  * `.pascal` – Pascal case: `MySignal`

#### Example Usage
```html
<div data-computed:my-signal__case.kebab="$bar + $baz"></div>
```
```

--------------------------------

### Show Element Based on Signal

Source: https://data-star.dev/reference

The `data-show` attribute conditionally displays an element based on the truthiness of a signal expression. For custom styling, `data-class` is recommended.

```html
<div data-show="$foo"></div>
```

--------------------------------

### SSE Event for Patching Signals

Source: https://data-star.dev/docs.md

This Server-Sent Event (SSE) format is used to patch frontend signals. The 'datastar-patch-signals' event type carries the signal data.

```sse
event: datastar-patch-signals
data: signals {hal: 'Affirmative, Dave. I read you.'}


```

--------------------------------

### Specify SVG Namespace for Patching

Source: https://data-star.dev/examples/svg_morphing

Use this data line to specify the SVG namespace when patching SVG elements. This is required because SVG is an XML dialect with its own namespace.

```text
1event: datastar-patch-elements
2data: namespace svg
3data: elements <circle id="circle" cx="100" r="50" cy="75"></circle>
4

```

--------------------------------

### Conditional Class Binding

Source: https://data-star.dev/reference/attributes

Use `data-class` to conditionally add or remove a class based on an expression. If the expression is true, `font-bold` is added.

```html
1<div data-class:font-bold="$foo == 'strong'"></div>
```

--------------------------------

### Create derived signals with data-computed

Source: https://data-star.dev/guide/reactive_signals

Defines a read-only signal derived from other reactive expressions.

```html
<input data-bind:foo-bar />
<div data-computed:repeated="$fooBar.repeat(2)" data-text="$repeated"></div>
```

--------------------------------

### Table Row Before Editing

Source: https://data-star.dev/examples/edit_row

Displays the read-only version of a table row with contact information and an 'Edit' button. This structure is present before the user initiates editing.

```html
1<tr>
2    <td>Joe Smith</td>
3    <td>joe@smith.org</td>
4    <td>
5        <button data-on:click="@get('/examples/edit_row/0')">
6            Edit
7        </button>
8    </td>
9</tr>
```

--------------------------------

### Use Datastar Expressions

Source: https://data-star.dev/reference/attributes

Accesses signal values and the current element reference within a data attribute expression.

```html
<div id="bar" data-text="$foo + el.id"></div>
```

--------------------------------

### Apply Node Content

Source: https://data-star.dev/examples/rocket_flow

Replaces the children of a node's group element with provided content. If no content is provided, it clears the group's children.

```javascript
const applyNodeContent = (entry, content) => {
      if (!entry.group) return
      if (!content) {
        entry.group.replaceChildren()
        return
      }
      const clone = content.cloneNode(true)
      if (clone.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
        entry.group.replaceChildren(...Array.from(clone.childNodes))
      } else {
        entry.group.replaceChildren(clone)
      }
    }
```

--------------------------------

### Implement Delete Row Button in HTML Table

Source: https://data-star.dev/examples/delete_row

Uses a button with a confirmation dialog and a delete request. The button is disabled while the request is in progress.

```html
 1<table>
 2    <thead>
 3        <tr>
 4            <th>Name</th>
 5            <th>Email</th>
 6            <th>Actions</th>
 7        </tr>
 8    </thead>
 9    <tbody>
10        <tr>
11            <td>Joe Smith</td>
12            <td>joe@smith.org</td>
13            <td>
14                <button
15                    class="error"
16                    data-on:click="confirm('Are you sure?') && @delete('/examples/delete_row/0')"
17                    data-indicator:_fetching
18                    data-attr:disabled="$_fetching"
19                >
20                    Delete
21                </button>
22            </td>
23        </tr>
24    </tbody>
25</table>
```

--------------------------------

### Implement Infinite Scroll Trigger

Source: https://data-star.dev/examples/infinite_scroll

Use the data-on-intersect attribute on the final element of a list to trigger a request when it scrolls into view.

```html
<div data-on-intersect="@get('/examples/infinite_scroll/more')">
    Loading...
</div>
```

--------------------------------

### Scroll Element Into View

Source: https://data-star.dev/reference/attributes

Automatically scrolls the element into the viewport when it becomes visible or is updated. Useful for new content loaded dynamically.

```html
<div data-scroll-into-view></div>
```

--------------------------------

### data-signals Attribute

Source: https://data-star.dev/guide/reactive_signals

The data-signals attribute patches global signals into the application state.

```APIDOC
## data-signals

### Description
Adds, updates, or removes global signals. Hyphenated names are converted to camelCase. Supports dot-notation for nested signals.

### Usage
- `data-signals:signal-name="value"`
- `data-signals="{signalName: value, nested: {key: value}}"`
```

--------------------------------

### Boolean Codec

Source: https://data-star.dev/docs.md

Details on the `bool` codec for decoding truthy attribute forms into booleans.

```APIDOC
## `bool`

`bool` decodes common truthy attribute forms into a boolean. Empty-string attributes such as `<demo-dialog open>` decode to `true`.

Without an explicit `.default(...)`, the zero value is `false`.

| Member | Effect | Notes |
|---|---|---|
| `.default(value)` | Supplies the fallback boolean. | `true`, `false`, or a factory function. |

```javascript
props: ({ bool }) => ({
  open: bool,
  disabled: bool,
  elevated: bool.default(true),
})
```
```

--------------------------------

### Conditionally setting CSS styles with data-style

Source: https://data-star.dev/docs.md

Use `data-style` to dynamically set CSS properties based on expressions. Falsy values restore the original inline style or remove the property.

```html
<div style="color: red;" data-style:color="$x && 'green'"></div>
```

```html
<div style="display: flex;" data-style:display="$hiding && 'none'"></div>
```

--------------------------------

### data-on

Source: https://data-star.dev/docs.md

The `data-on` attribute attaches an event listener to an element, executing an expression when the event is triggered. An `evt` variable representing the event object is available in the expression.

```APIDOC
## `data-on`

### Description
Attaches an event listener to an element and executes an expression when the event fires.

### Usage
```html
<button data-on:click="$foo = ''">Reset</button>
```

### Accessing Event Object
The `evt` variable is available in the expression, representing the event object.

```html
<div data-on:my-event="$foo = evt.detail"></div>
```

### Supported Events
Works with standard browser events and custom events. The `data-on:submit` listener prevents default form submission behavior.
```

--------------------------------

### Observe Flow Children

Source: https://data-star.dev/examples/rocket_flow

MutationObserver that hides flow children nodes when they are added to the DOM.

```javascript
const childObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) hideFlowChild(node)
      }
    })
```

--------------------------------

### Ensure Cluster Layers and Data

Source: https://data-star.dev/examples/rocket_openfreemap

Manages the addition and updating of cluster layers and data for markers. It checks if the map style is loaded and adds or updates the GeoJSON source for clustering. This function is crucial for displaying aggregated markers efficiently.

```javascript
const ensureClusterLayersAndData = (config) => {
      if (!map?.isStyleLoaded()) return
      let source = map.getSource(clusterSourceID)
      if (!source) {
        map.addSource(clusterSourceID, {
          type: 'geojson',
          data: markerEntriesToGeoJSON(markerEntries),
          cluster: true,
          clusterMaxZoom: config.maxZoom,
          clusterRadius: config.radius,
        })
        source = map.getSource(clusterSourceID)
      } else {
        source.setData(markerEntriesToGeoJSON(markerEntries))
      }

      if (!map.getLayer(clusterLayerID)) {
        map.addLayer({
          id: clusterLayerID,
          type: 'circle',
          source: clusterSourceID,
          filter: ['has', 'point_count'],
          paint: {
            'circle-color': [
              'step',
              ['get', 'point_count'],
              '#3b82f6',
              6,
              '#2563eb',
              12,
              '#1d4ed8',
            ],
            'circle-radius': [
              'step',
              ['get', 'point_count'],
              32,
              6,
              40,
              12,
              48,
            ],
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 3,
            'circle-opacity': 0.88,
          },
        })
      }

      if (!map.getLayer(clusterCountLayerID)) {
        map.addLayer({
          id: clusterCountLayerID,
          type: 'symbol',
          source: clusterSourceID,
          filter: ['has', 'point_count'],
          layout: {
            'text-field': '{point_count_abbreviated}',
            'text-size': 24,
          },
          paint: {
            'text-color': '#ffffff',
          },
        })
      }

      if (!map.getLayer(unclusteredLayerID)) {
        map.addLayer({
          id: unclusteredLayerID,
          type: 'circle',
          source: clusterSourceID,
          filter: ['!', ['has', 'point_count']],
          paint: {
            'circle-color': '#ad1529',
            'circle-radius': 12,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 3,
          },
        })
      }
    }
```

--------------------------------

### Displaying a Signal Value

Source: https://data-star.dev/guide/datastar_expressions

Use '$signalName' within a data attribute to display the current value of a Datastar signal. Ensure the signal is defined using 'data-signals'.

```html
1<div data-signals:foo="1">
2    <div data-text="$foo"></div>
3</div>
```

--------------------------------

### Generate Edge Key

Source: https://data-star.dev/examples/rocket_flow

Creates a unique key for an edge, prioritizing an explicit ID or falling back to source and target IDs.

```javascript
const makeEdgeKey = (sourceId, targetId, id) =>
  id ? `id:${id}` : `${sourceId ?? ''}->${targetId ?? ''}`
```

--------------------------------

### Update Document Title via Datastar

Source: https://data-star.dev/examples/title_update

Uses the datastar-patch-elements event to target the title tag and update its content dynamically.

```text
event: datastar-patch-elements
data: selector title
data: elements <title>08:30:36</title>
```

--------------------------------

### data-computed for Memoizing Expressions

Source: https://data-star.dev/reference

Memoize expressions containing other signals using `data-computed`. The computed signal's value can be used in other expressions.

```html
<div data-computed:foo="$bar + $baz">
</div>
<div data-text="$foo"></div>
```

--------------------------------

### Apply ARIA attributes with data-attr

Source: https://data-star.dev/guide/the_tao_of_datastar

Use the data-attr directive to dynamically update ARIA attributes based on component state.

```html
<button data-on:click="$_menuOpen = !$_menuOpen"
        data-attr:aria-expanded="$_menuOpen ? 'true' : 'false'"
>
    Open/Close Menu
</button>
<div data-attr:aria-hidden="$_menuOpen ? 'false' : 'true'"></div>
```

--------------------------------

### Date Prop Decoders

Source: https://data-star.dev/reference/rocket

Decode props into Date objects, ensuring invalid inputs result in valid date instances.

```javascript
props: ({ date }) => ({
  startAt: date.default(() => new Date()),
  endAt: date.default(() => new Date(Date.now() + 60_000)),
})
```

--------------------------------

### Using __root for Page-Level Signal Binding

Source: https://data-star.dev/reference/rocket

Apply the __root modifier to signal-name attributes to ensure they remain bound to the outer page scope rather than the component's private scope.

```html
<demo-fieldset>
  <demo-input data-bind:name__root></demo-input>
</demo-fieldset>
```

--------------------------------

### Setting single CSS styles with data-style

Source: https://data-star.dev/reference/attributes

Use `data-style` to set individual inline CSS properties based on expressions. The styles are kept in sync with signal changes.

```html
<div data-style:display="$hiding && 'none'"></div>
<div data-style:background-color="$red ? 'red' : 'blue'"></div>
```

--------------------------------

### Define Host Accessor Overrides

Source: https://data-star.dev/reference/rocket

Type definitions for overriding existing props or defining new host properties.

```typescript
1overrideProp<Name extends keyof Props & string>(
  name: Name,
  getter?: (getDefault: () => Props[Name]) => any,
  setter?: (value: any, setDefault: (value: Props[Name]) => void) => void,
): void

defineHostProp(name: string, descriptor: PropertyDescriptor): void
```

--------------------------------

### Define flow-node Component Properties

Source: https://data-star.dev/examples/rocket_flow

Defines the properties for the 'flow-node' component, specifying their types and default values. Use this for configuring node dimensions and labels.

```javascript
rocket('flow-node', {
  props: ({ number, string }) => ({
    x: number,
    y: number,
    label: string,
    width: number.min(1).default(DEFAULT_NODE_WIDTH),
    height: number.min(1).default(DEFAULT_NODE_HEIGHT),
  }),
  setup({ cleanup, effect, host, props }) {
    host.style.display = 'none'

    const collectCustomContent = () => {
      const fragment = document.createDocumentFragment()
      host.childNodes.forEach((child) => {
        if (
          child.nodeType === Node.ELEMENT_NODE &&
          child.nodeName.toUpperCase() === 'TEMPLATE'
        )
          return
        const clone = cloneNodeIntoSvg(child)
        if (!clone) return
        if (clone.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
          fragment.append(...Array.from(clone.childNodes))
        } else {
          fragment.append(clone)
        }
      })
      return fragment.childNodes.length ? fragment : null
    }

    const createDefaultContent = () => {
      const fragment = document.createDocumentFragment()
      const svg = document.createElementNS(SVG_NS, 'svg')
      const rect = document.createElementNS(SVG_NS, 'rect')
      const text = document.createElementNS(SVG_NS, 'text')
      svg.setAttribute('width', String(props.width))
      svg.setAttribute('height', String(props.height))
      svg.setAttribute('viewBox', `0 0 ${props.width} ${props.height}`)
      svg.setAttribute('data-default-node', '')
      rect.setAttribute('rx', '12')
      rect.setAttribute('ry', '12')
      rect.setAttribute('width', String(props.width))
      rect.setAttribute('height', String(props.height))
      rect.setAttribute('fill', '#ffffff')
      rect.setAttribute('stroke', '#94a3b8')
      rect.setAttribute('stroke-width', '1.5')
      text.setAttribute('x', String(props.width / 2))
      text.setAttribute('y', String(props.height / 2))
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('dominant-baseline', 'middle')
      text.setAttribute(
        'font-family',
        'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont',
      )
      text.setAttribute('font-weight', '600')
      text.setAttribute('font-size', '13')
      text.setAttribute('fill', '#0f172a')
      text.textContent = props.label
      svg.append(rect, text)
      fragment.append(svg)
      return fragment
    }

    const snapshot = () => ({
      id: host.getAttribute('id') ?? '',
      x: props.x,
      y: props.y,
      label: props.label,
      width: props.width,
      height: props.height,
      content: collectCustomContent() ?? createDefaultContent(),
    })

    const emit = (name) => {
      host.dispatchEvent(
        new CustomEvent(name, {
          detail: snapshot(),
          bubbles: true,
          composed: true,
        }),
      )
    }

    const observer = new MutationObserver(() =>
      queueMicrotask(() => emit('flow-node-update')),
    )
    observer.observe(host, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
    })

    queueMicrotask(() => emit('flow-node-register'))
    cleanup(() => {
      observer.disconnect()
      emit('flow-node-remove')
    })
    effect(() => {
      props.x
      props.y
      props.label
      props.width
      props.height
      emit('flow-node-update')
    })
  },
})
```

--------------------------------

### HTML Response for DOM Patching

Source: https://data-star.dev/docs.md

When a response has a `text/html` content type, Datastar morphs the top-level HTML elements into the DOM based on element IDs. Ensure a target element with a matching ID exists.

```html
<div id="hal">
    I’m sorry, Dave. I’m afraid I can’t do that.
</div>
```

--------------------------------

### Multiple Statements in Datastar Expressions

Source: https://data-star.dev/guide/datastar_expressions

Separate multiple statements within a single Datastar expression using a semicolon (;). This allows for sequential operations within a data attribute.

```html
1<div data-signals:foo="1">
2    <button data-on:click="$landingGearRetracted = true; @post('/launch')">
3        Force launch
4    </button>
5</div>
```

--------------------------------

### Prevent Flicker with Initial Hidden State

Source: https://data-star.dev/reference

To avoid element flickering before Datastar processes the DOM, apply `display: none` to elements using `data-show`.

```html
<div data-show="$foo" style="display: none"></div>
```

--------------------------------

### Number Codec

Source: https://data-star.dev/docs.md

Details on the `number` codec, its capabilities for numeric API enforcement, and available members.

```APIDOC
## `number`

`number` turns a prop into a numeric API and lets you enforce range, rounding, snapping, and remapping rules right in the prop definition.

Without an explicit `.default(...)`, the zero value is `0`.

| Member | Effect | Example |
|---|---|---|
| `.min(value)` | Enforces a lower bound. | `-4` with `min(0)` becomes `0`. |
| `.max(value)` | Enforces an upper bound. | `120` with `max(100)` becomes `100`. |
| `.clamp(min, max)` | Applies both bounds. | `120` with `clamp(0, 100)` becomes `100`. |
| `.step(step, base?)` | Snaps to the nearest increment. | `13` with `step(5)` becomes `15`. |
| `.round` | Rounds to the nearest integer. | `3.6` becomes `4`. |
| `.ceil(decimals?)` | Rounds up with optional decimal precision. | `1.231` with `ceil(2)` becomes `1.24`. |
| `.floor(decimals?)` | Rounds down with optional decimal precision. | `1.239` with `floor(2)` becomes `1.23`. |
| `.fit(inMin, inMax, outMin, outMax, clamped?, rounded?)` | Maps one numeric range into another. | `50` from `0-100` into `0-1` becomes `0.5`. |
| `.default(value)` | Supplies a fallback number. | Missing values can become `0` or `1`. |

```javascript
props: ({ number }) => ({
  width: number.min(0).default(320),
  opacity: number.clamp(0, 1).ceil(2).default(1),
  progress: number.clamp(0, 100).step(5),
  normalizedX: number.fit(0, 1920, 0, 1, true, false),
})
```
```

--------------------------------

### DELETE Request

Source: https://data-star.dev/docs.md

Sends a DELETE request to the backend. Signals are sent as a JSON body by default. Supports options like `openWhenHidden` and `contentType`.

```APIDOC
## DELETE /endpoint

### Description
Sends a `DELETE` request to the backend. Works similarly to `@get()` but uses the DELETE HTTP method. Signals are sent as a JSON body by default.

### Method
DELETE

### Endpoint
`/endpoint`

### Parameters
#### Query Parameters
- **openWhenHidden** (boolean) - Optional - If true, the SSE connection remains open when the page is hidden.
- **contentType** (string) - Optional - Sets the `Content-Type` header. Can be 'form' for `application/x-www-form-urlencoded`.

### Request Example
```html
<button data-on:click="@delete('/endpoint')"></button>
```

### Response
#### Success Response (200)
- **Datastar SSE events** (array) - Zero or more SSE events from the backend.
```

--------------------------------

### Component Cleanup

Source: https://data-star.dev/examples/rocket_openfreemap

Removes markers, layers, and the map instance when the component is destroyed.

```javascript
cleanup(() => {
      removeDomMarkers()
      removeClusterLayersAndSource()
      map?.remove()
    })
```

--------------------------------

### Virtual Scroll Component Render Template

Source: https://data-star.dev/examples/rocket_virtual_scroll

HTML structure and CSS styles for the virtual scroll viewport, spacer, and blocks.

```html
render: ({ html, host }) => html`
    <style>
      :host {
        display: block;
      }

      .virtual-scroll-viewport {
        height: inherit;
        overflow-y: auto;
        position: relative;
      }

      .virtual-scroll-spacer {
        position: relative;
      }

      .virtual-scroll-block {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
      }
    </style>

    <div class="virtual-scroll-viewport" data-ref:viewport data-viewport>
      <div class="virtual-scroll-spacer" data-ref:spacer data-spacer>
        <div
          id="${host.id}-a"
          class="virtual-scroll-block"
          data-ref:block-a
          data-block="A"
        ></div>
        <div
          id="${host.id}-b"
          class="virtual-scroll-block"
          data-ref:block-b
          data-block="B"
        ></div>
        <div
          id="${host.id}-c"
          class="virtual-scroll-block"
          data-ref:block-c
          data-block="C"
        ></div>
      </div>
    </div>
  `
```

--------------------------------

### Binding element text content with data-text

Source: https://data-star.dev/reference/attributes

Bind the text content of an element to an expression using the `data-text` attribute.

```html
<div data-text="$foo"></div>
```

--------------------------------

### Attach Event Listeners with data-on

Source: https://data-star.dev/reference/attributes

The `data-on` attribute attaches an event listener to an element, executing an expression when the specified event is triggered. The event object is available as `evt`.

```html
<button data-on:click="$foo = ''">Reset</button>
```

```html
<div data-on:my-event="$foo = evt.detail"></div>
```

```html
<!-- The data-on:submit event listener prevents the default submission behavior of forms. -->
```

--------------------------------

### Numeric Prop API

Source: https://data-star.dev/reference/rocket

The number codec allows for numeric prop enforcement, including range, rounding, snapping, and remapping.

```APIDOC
## number

### Description
Turns a prop into a numeric API and lets you enforce range, rounding, snapping, and remapping rules.

### Members
- **min(value)**: Enforces a lower bound.
- **max(value)**: Enforces an upper bound.
- **clamp(min, max)**: Applies both bounds.
- **step(step, base?)**: Snaps to the nearest increment.
- **round**: Rounds to the nearest integer.
- **ceil(decimals?)**: Rounds up with optional decimal precision.
- **floor(decimals?)**: Rounds down with optional decimal precision.
- **fit(inMin, inMax, outMin, outMax, clamped?, rounded?)**: Maps one numeric range into another.
- **default(value)**: Supplies a fallback number.
```

--------------------------------

### Constrain Prop to Allowed Values with DataStar

Source: https://data-star.dev/reference/rocket

The `oneOf` codec restricts a prop to a predefined set of literal values or codecs. Without an explicit default, the first allowed entry is used.

```javascript
props: ({ oneOf, string, number }) => ({
  tone: oneOf('neutral', 'info', 'success', 'warning', 'danger').default('neutral'),
  alignment: oneOf('start', 'center', 'end').default('start'),
  flexibleValue: oneOf(string.trim, number.round),
})
```

--------------------------------

### Observe Reactive Properties

Source: https://data-star.dev/examples/rocket_openfreemap

Updates map state when component properties change, such as style URL, view coordinates, or clustering settings.

```javascript
observeProps(() => {
      if (!map || props.styleUrl === prevStyleURL) return
      prevStyleURL = props.styleUrl
      map.setStyle(props.styleUrl)
    }, 'styleUrl')
    observeProps(
      () => {
        if (!map) return
        const next = JSON.stringify({
          center: props.center,
          zoom: props.zoom,
          bearing: props.bearing,
          pitch: props.pitch,
        })
        if (next === prevView) return
        prevView = next
        map.easeTo({
          center: props.center,
          zoom: props.zoom,
          bearing: props.bearing,
          pitch: props.pitch,
          duration: 500,
        })
      },
      'center',
      'zoom',
      'bearing',
      'pitch',
    )
    observeProps(() => {
      if (!map || props.dragRotate === prevDragRotate) return
      prevDragRotate = props.dragRotate
      if (props.dragRotate) {
        map.dragRotate.enable()
        ensure3DBuildings()
      } else {
        map.dragRotate.disable()
      }
    }, 'dragRotate')
    observeProps(
      () => {
        const next = JSON.stringify([
          props.cluster,
          Math.round(props.clusterMaxZoom),
          Math.round(props.clusterRadius),
        ])
        if (next === prevClusterSignal) return
        prevClusterSignal = next
        syncMarkers()
      },
      'cluster',
      'clusterMaxZoom',
      'clusterRadius',
    )
    observeProps(() => {
      const nextMarkers = readMarkerEntries()
      const next = JSON.stringify(nextMarkers)
      if (next === prevMarkers) return
      prevMarkers = next
      markerEntries = nextMarkers
      syncMarkers()
    }, 'markers')
```

--------------------------------

### Rocket Render Type Definitions

Source: https://data-star.dev/reference/rocket

Defines the types for render values, including primitives, nodes, iterables, and document fragments. The `RocketRender` type specifies the signature for the render function.

```typescript
1type RocketPrimitiveRenderValue =
2  | string
3  | number
4  | boolean
5  | bigint
6  | Date
7  | null
8  | undefined
9
10type RocketComposedRenderValue =
11  | RocketPrimitiveRenderValue
12  | Node
13  | Iterable<RocketComposedRenderValue>
14
15type RocketRenderValue =
16  | DocumentFragment
17  | RocketPrimitiveRenderValue
18  | Iterable<RocketComposedRenderValue>
19
20type RocketRender<Props extends Record<string, any>> = {
21  (context: RenderContext<Props>): RocketRenderValue
22  <A1>(context: RenderContext<Props>, a1: A1): RocketRenderValue
23  <A1, A2, A3, A4, A5, A6, A7, A8>(
24    context: RenderContext<Props>,
25    a1: A1,
26    a2: A2,
27    a3: A3,
28    a4: A4,
29    a5: A5,
30    a6: A6,
31    a7: A7,
32    a8: A8,
33  ): RocketRenderValue
34}
35
36render?: RocketRender<InferProps<Defs>>
```

--------------------------------

### Set Pending Node State

Source: https://data-star.dev/examples/rocket_flow

Sets the pending state for a specific node, highlighting it and related edges. Clears pending state if no nodeId is provided. Requires 'pending' and 'data-pending-node' attributes on the host.

```javascript
    const setPendingState = (nodeId) => {
      if (!nodeId) {
        clearPendingState()
        return
      }
      host.setAttribute('pending', 'true')
      host.setAttribute('data-pending-node', nodeId)
      nodesLayer?.querySelectorAll('.flow-node').forEach((group) => {
        group.classList.toggle('is-pending', group.dataset.nodeId === nodeId)
      })
      edgesLayer?.querySelectorAll('.flow-edge').forEach((group) => {
        const connected =
          group.dataset.sourceId === nodeId || group.dataset.targetId === nodeId
        group.classList.toggle('is-pending', connected)
      })
    }
```

--------------------------------

### data-ignore

Source: https://data-star.dev/reference/attributes

Tells Datastar to ignore an element and its descendants.

```APIDOC
### `data-ignore`

Datastar walks the entire DOM and applies plugins to each element it encounters. It’s possible to tell Datastar to ignore an element and its descendants by placing a `data-ignore` attribute on it. This can be useful for preventing naming conflicts with third-party libraries, or when you are unable to escape user input.

#### Example Usage
```html
<div data-ignore data-show-thirdpartylib="">
    <div>
        Datastar will not process this element.
    </div>
</div>
```

#### Modifiers
* `__self` – Only ignore the element itself, not its descendants.
```

--------------------------------

### data-bind Attribute

Source: https://data-star.dev/reference/attributes

The `data-bind` attribute establishes two-way data binding between an element's state and a Datastar signal. It automatically updates the signal when the element's value changes and vice-versa. It supports various input types, including file uploads.

```APIDOC
## data-bind

### Description
Creates a signal (if one doesn’t already exist) and sets up two-way data binding between it and an element’s current bound state. When the signal changes, Datastar writes that value to the element. When one of the bind events fires, Datastar reads the element’s current bound property/value and writes that back to the signal.

### Method
N/A (Attribute)

### Endpoint
N/A (Attribute)

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A

### Request Example
```html
1<input data-bind:foo />
```

```html
1<input data-bind="foo" />
```

```html
1<!-- Both of these create the signal `$fooBar` -->
2<input data-bind:foo-bar />
3<input data-bind="fooBar" />
```

```html
1<!-- The initial value of the signal is set to the value of the element, unless a signal has already been defined. So in the example below, `$fooBar` is set to `baz`. -->
2<input data-bind:foo-bar value="baz" />
```

```html
1<!-- Whereas in the example below, `$fooBar` inherits the value `fizz` of the predefined signal. -->
2<div data-signals:foo-bar="'fizz'">
3    <input data-bind:foo-bar value="baz" />
4</div>
```

#### Predefined Signal Types
When you predefine a signal, its **type** is preserved during binding. Whenever the element’s value changes, the signal value is automatically converted to match the original type.

For example, in the code below, `$fooBar` is set to the **number** `10` (not the string `
```

--------------------------------

### Synchronize Globe Arcs Data

Source: https://data-star.dev/examples/rocket_globe

Use the "stringify and compare" pattern to prevent unnecessary updates when working with complex reactive objects or arrays that update frequently. This ensures the effect only runs when the actual data changes.

```javascript
1onFirstRender({ refs, observeProps, props }) {
 2    let prevArcs = ''
 3
 4    const syncArcs = () => {
 5        const next = JSON.stringify(props.arcs || [])
 6        if (next === prevArcs) return
 7        prevArcs = next
 8        globe.arcsData(JSON.parse(next))
 9    }
10
11    syncArcs()
12    observeProps(syncArcs, 'arcs')
13}
```

--------------------------------

### Positioning Blocks for Virtual Scrolling

Source: https://data-star.dev/examples/rocket_virtual_scroll

Calculates and sets the vertical positions of blocks based on their content height and average item height. This function is crucial for determining where each block should be rendered within the viewport.

```javascript
const positionBlocks = () => {
      const positions = ['A', 'B', 'C']
        .map((name) => ({
          block: name,
          startIdx: startIndexOf(name),
          el: blocks[name],
          height: blocks[name]?.getBoundingClientRect().height ?? 0,
        }))
        .sort((a, b) => a.startIdx - b.startIdx)
      const totalHeight = positions.reduce((sum, pos) => sum + pos.height, 0)
      const blockCount = props.bufferSize * 3
      totalMeasuredHeight =
        measuredItems > 0 ? totalMeasuredHeight + totalHeight : totalHeight
      measuredItems =
        measuredItems > 0 ? measuredItems + blockCount : blockCount
      avgItemHeight = totalMeasuredHeight / measuredItems || avgItemHeight

      let currentY = (positions[0]?.startIdx ?? 0) * avgItemHeight
      for (const pos of positions) {
        setY(pos.block, currentY)
        currentY += pos.height
      }
      setHeights()
    }
```

--------------------------------

### SSE Patch Signals Event

Source: https://data-star.dev/guide/reactive_signals

Server-Sent Event format for patching signals using the datastar-patch-signals event type.

```text
1event: datastar-patch-signals
2data: signals {hal: 'Affirmative, Dave. I read you.'}
3
```

```text
1event: datastar-patch-signals
2data: signals {hal: 'Affirmative, Dave. I read you.'}
3
4// Wait 1 second
5
6event: datastar-patch-signals
7data: signals {hal: '...'}
8
```

--------------------------------

### Patch Elements with Datastar

Source: https://data-star.dev/docs.md

Use the `datastar-patch-elements` event to morph elements in the DOM. Ensure top-level elements have IDs for default morphing. Supports various modes like `outer`, `inner`, `replace`, `prepend`, `append`, `before`, `after`, and `remove`.

```html
event: datastar-patch-elements
data: elements <div id="foo">Hello world!</div>


```

```html
event: datastar-patch-elements
data: selector #foo
data: mode remove


```

```html
event: datastar-patch-elements
data: selector #foo
data: mode inner
data: useViewTransition true
data: elements <div>
data: elements        Hello world!
data: elements </div>


```

```html
event: datastar-patch-elements
data: namespace svg
data: elements <circle id="circle" cx="100" r="50" cy="75"></circle>


```

--------------------------------

### Streaming Patch Elements via SSE

Source: https://data-star.dev/guide/getting_started

Use the datastar-patch-elements event type in an SSE stream to update the DOM. Ensure events are terminated with two newline characters.

```text
1event: datastar-patch-elements
2data: elements <div id="hal">
3data: elements     I’m sorry, Dave. I’m afraid I can’t do that.
4data: elements </div>
5
```

```text
 1event: datastar-patch-elements
 2data: elements <div id="hal">
 3data: elements     I’m sorry, Dave. I’m afraid I can’t do that.
 4data: elements </div>
 5
 6event: datastar-patch-elements
 7data: elements <div id="hal">
 8data: elements     Waiting for an order...
 9data: elements </div>
10
```

--------------------------------

### Codec Contract Definition

Source: https://data-star.dev/reference/rocket

Defines the interface for a codec, requiring `decode` and `encode` methods. Use this to understand the requirements for custom codecs.

```typescript
export type Codec<T> = {
  decode(value: unknown): T
  encode(value: T): string
}
```

--------------------------------

### data-class with Boolean Expression

Source: https://data-star.dev/reference

Conditionally add or remove a class based on a boolean expression. If the expression is true, the class is added; otherwise, it's removed.

```html
<div data-class:font-bold="$foo == 'strong'"></div>
```

--------------------------------

### HTML Lazy Tabs Structure

Source: https://data-star.dev/examples/lazy_tabs

Uses data-on:click attributes to trigger server-side requests for tab content updates.

```html
 1<div id="demo">
 2    <div role="tablist">
 3        <button
 4            role="tab"
 5            aria-selected="true"
 6            data-on:click="@get('/examples/lazy_tabs/0')"
 7        >
 8            Tab 0
 9        </button>
10        <button
11            role="tab"
12            aria-selected="false"
13            data-on:click="@get('/examples/lazy_tabs/1')"
14        >
15            Tab 1
16        </button>
17        <button
18            role="tab"
19            aria-selected="false"
20            data-on:click="@get('/examples/lazy_tabs/2')"
21        >
22            Tab 2
23        </button>
24        <!-- More tabs... -->
25    </div>
26    <div role="tabpanel">
27        <p>Lorem ipsum dolor sit amet...</p>
28        <p>Consectetur adipiscing elit...</p>
29        <!-- Tab content -->
30    </div>
31</div>
```

--------------------------------

### Read signals in Kotlin

Source: https://data-star.dev/docs.md

Uses a custom JsonUnmarshaller to decode signals from a request body.

```kotlin
@Serializable
data class Signals(
    val foo: String,
)

val jsonUnmarshaller: JsonUnmarshaller<Signals> = { json -> Json.decodeFromString(json) }

val request: Request =
    postRequest(
        body =
            """
            {
                "foo": "bar"
            }
            """.trimIndent(),
    )

val signals = readSignals(request, jsonUnmarshaller)
```

--------------------------------

### Prevent Default Enter Key Behavior and Show Alert

Source: https://data-star.dev/how_tos/bind_keydown_events_to_specific_keys

Prevent the default action (e.g., form submission) when 'Enter' is pressed and then show an alert. This uses a comma within the expression to sequence actions.

```html
<div data-on:keydown__window="evt.key === 'Enter' && (evt.preventDefault(), alert('Key pressed'))"></div>
```

--------------------------------

### Implementing custom validity with data-custom-validity

Source: https://data-star.dev/reference

Set custom validation messages for form inputs. An empty string indicates the input is valid.

```html
<form>
    <input data-bind:foo name="foo" />
    <input data-bind:bar name="bar"
           data-custom-validity="$foo === $bar ? '' : 'Values must be the same.'"
    />
    <button>Submit form</button>
</form>
```

--------------------------------

### Handle Node Removal

Source: https://data-star.dev/examples/rocket_flow

Cleans up node references and associated groups when a node is removed.

```javascript
const onNodeRemove = (evt) => {
      const target = evt.target
      if (!(target instanceof HTMLElement)) return
      const entry = nodes.get(target)
      entry?.group?.remove()
      nodes.delete(target)
      if (entry?.id && nodesById.get(entry.id) === entry)
        nodesById.delete(entry.id)
      scheduleEdgeRender()
    }
```

--------------------------------

### Boolean Prop API

Source: https://data-star.dev/reference/rocket

The bool codec decodes common truthy attribute forms into a boolean.

```APIDOC
## bool

### Description
Decodes common truthy attribute forms into a boolean. Empty-string attributes decode to true.

### Members
- **default(value)**: Supplies the fallback boolean.
```

--------------------------------

### data-on Attribute

Source: https://data-star.dev/guide/reactive_signals

The data-on attribute attaches event listeners to elements to execute expressions.

```APIDOC
## data-on

### Description
Attaches an event listener to an element. Executes the provided expression when the event is triggered. Event names are converted to kebab-case.

### Usage
- `data-on:event-name="expression"`
- Example: `data-on:click="$signal = 'value'"`
```

--------------------------------

### Compact JSON Output with data-json-signals__terse

Source: https://data-star.dev/reference/attributes

The `__terse` modifier for `data-json-signals` outputs JSON in a compact format without extra whitespace, suitable for inline display.

```html
<!-- Display filtered signals in a compact format -->
<pre data-json-signals__terse="{include: /counter/}"></pre>
```

--------------------------------

### PatchElements Event with ID Target

Source: https://data-star.dev/errors/patch_elements_no_targets_found

Use this format when targeting an element directly by its ID for a datastar-patch-elements event. Ensure the ID exists in the DOM.

```yaml
1event: datastar-patch-elements
2data: elements <div id="foo"></div>
```

--------------------------------

### Normalize Viewport

Source: https://data-star.dev/examples/rocket_flow

Normalizes viewport values, ensuring x, y, and zoom are valid numbers within expected ranges.

```javascript
const normalizeViewport = (value) => [
  value?.[0] ?? 0,
  value?.[1] ?? 0,
  clampZoom(value?.[2] ?? 1),
]
```

--------------------------------

### OneOf Codec

Source: https://data-star.dev/reference/rocket

The `oneOf` codec constrains a property to a predefined set of allowed values. These values can be literals or other codecs. A default value can be explicitly set, otherwise, the first option serves as the default.

```APIDOC
## `oneOf` codec

### Description
`oneOf` constrains a prop to a known set of allowed values. You can pass literal values, codecs, or both. Without an explicit `.default(...)`, the zero value is the first allowed entry.

### Form
- `oneOf('a', 'b', 'c')`: Enums and variant names. Returns the matching literal or the first/default entry.
- `oneOf(codecA, codecB)`: Union-like decoding. Tries each codec in order until one succeeds.
- `.default(value)`: Explicit fallback. Overrides the implicit “first option wins” fallback.

### Example
```javascript
props: ({ oneOf, string, number }) => ({
  tone: oneOf('neutral', 'info', 'success', 'warning', 'danger').default('neutral'),
  alignment: oneOf('start', 'center', 'end').default('start'),
  flexibleValue: oneOf(string.trim, number.round),
})
```
```

--------------------------------

### Toggling Element Visibility with data-show

Source: https://data-star.dev/examples/rocket_conditional

Use the `data-show` attribute to toggle the visibility of an element. This attribute keeps the DOM node mounted, preserving its state, bindings, and event handlers.

```html
<aside data-show="${showDetails}">
            <strong>Still mounted</strong>
            <p>
              <code>data-show</code> only changes visibility. The DOM node stays
              in place, so its state, bindings, and event handlers remain intact.
            </p>
          </aside>
```

--------------------------------

### data-bind Modifiers

Source: https://data-star.dev/reference

The `data-bind` attribute allows for modifying behavior when binding signals using a key. Modifiers like `__case`, `__prop`, and `__event` provide fine-grained control over the binding process.

```APIDOC
## data-bind Modifiers

Modifiers allow you to modify behavior when binding signals using a key.

### Modifiers

*   `__case` – Converts the casing of the signal name.
    *   `.camel` – Camel case: `mySignal` (default)
    *   `.kebab` – Kebab case: `my-signal`
    *   `.snake` – Snake case: `my_signal`
    *   `.pascal` – Pascal case: `MySignal`
*   `__prop` – Binds through a specific property instead of the inferred native/default binding.
    *   Example: `data-bind:is-checked__prop.checked`
*   `__event` – Defines which events sync the element back to the signal.
    *   Example: `data-bind:query__event.input.change`

### Examples

```html
<input data-bind:my-signal__case.kebab />
```

Native form controls still use their built-in binding semantics automatically. Generic custom elements now default to `value` plus `change`. Use `__prop` and `__event` when a custom element’s live state is stored somewhere else.

```html
<my-toggle data-bind:is-checked__prop.checked__event.change></my-toggle>
```
```

--------------------------------

### data-attr Attribute

Source: https://data-star.dev/reference/attributes

The `data-attr` attribute allows you to set and synchronize HTML attributes with Datastar expressions. It supports setting individual attributes or multiple attributes using a key-value object.

```APIDOC
## data-attr

### Description
Sets the value of any HTML attribute to an expression, and keeps it in sync.

### Method
N/A (Attribute)

### Endpoint
N/A (Attribute)

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A

### Request Example
```html
1<div data-attr:aria-label="$foo"></div>
```

```html
1<div data-attr="{'aria-label': $foo, disabled: $bar}"></div>
```

### Response
#### Success Response (200)
N/A (Attribute)

#### Response Example
N/A (Attribute)
```

--------------------------------

### Removing a signal with data-signals

Source: https://data-star.dev/reference/attributes

Set a signal's value to `null` or `undefined` in the `data-signals` attribute to remove it.

```html
<div data-signals="{foo: null}"></div>
```

--------------------------------

### Accessing Element Properties

Source: https://data-star.dev/guide/datastar_expressions

The 'el' variable is automatically available in Datastar expressions, representing the element the attribute is attached to. Use it to access element properties like 'offsetHeight'.

```html
1<div data-text="el.offsetHeight"></div>
```

--------------------------------

### Conditionally Show Element

Source: https://data-star.dev/reference/attributes

The `data-show` attribute toggles an element's visibility based on a signal's truthiness. Use `style="display: none"` initially to prevent flickering.

```html
<div data-show="$foo"></div>
```

```html
<div data-show="$foo" style="display: none"></div>
```

--------------------------------

### Ensure Node Group Creation

Source: https://data-star.dev/examples/rocket_flow

Creates a new SVG group element for a node if it doesn't exist. Sets cursor style and appends it to the nodes layer. Also enables node dragging.

```javascript
    const ensureNodeGroup = (entry) => {
      if (entry.group) return
      entry.group = document.createElementNS(SVG_NS, 'g')
      entry.group.classList.add('flow-node')
      entry.group.setAttribute('tabindex', '-1')
      entry.group.style.cursor = 'grab'
      nodesLayer?.append(entry.group)
      syncNodeDataset(entry)
      enableNodeDrag(entry)
    }
```

--------------------------------

### Display signal values with data-text

Source: https://data-star.dev/guide/reactive_signals

Updates an element's text content based on a signal value or a JavaScript expression.

```html
<input data-bind:foo-bar />
<div data-text="$fooBar"></div>
```

```html
<input data-bind:foo-bar />
<div data-text="$fooBar.toUpperCase()"></div>
```

--------------------------------

### Patch Signals Event

Source: https://data-star.dev/reference/sse_events

Updates client-side signals using the datastar-patch-signals event type. The signals data should be a valid JSON object.

```text
event: datastar-patch-signals
data: signals {foo: 1, bar: 2}

```

```text
event: datastar-patch-signals
data: signals {foo: null, bar: null}

```

```text
event: datastar-patch-signals
data: onlyIfMissing true
data: signals {foo: 1, bar: 2}

```

--------------------------------

### Wrap SVG Elements in <svg> Tag

Source: https://data-star.dev/examples/svg_morphing

Alternatively, ensure the target SVG element is wrapped in an outer `<svg>` tag to correctly handle the namespace.

```html
1<svg id="circle">
2    <circle cx="50" cy="100" r="50" fill="red" />
3</svg>

```

--------------------------------

### Processing Scroll Events and Triggering Updates

Source: https://data-star.dev/examples/rocket_virtual_scroll

Continuously checks the scroll position to determine if new content needs to be loaded or if blocks need to be repositioned. It handles both normal scrolling and jump-to-index scenarios.

```javascript
const checkScroll = () => {
      if (!viewport) return
      const now = Date.now()
      if (now - lastProcessedScroll < 20) return
      lastProcessedScroll = now

      const { scrollTop, clientHeight } = viewport
      const scrollBottom = scrollTop + clientHeight
      const y = { A: blockAY, B: blockBY, C: blockCY }
      const [above, , below] = blockPositions
      const nextBlocks = Object.fromEntries(
        ['A', 'B', 'C'].map((name) => (
          [
            name,
            {
              y: y[name],
              height: blocks[name]?.offsetHeight ?? 0,
              startIdx: startIndexOf(name),
            },
          ]
        )))
      )

      if (
        !['A', 'B', 'C'].some((name) =>
          isBlockInView(nextBlocks[name], scrollTop, scrollBottom),
        )
      ) {
        if (isLoading && jumpTimeout) {
          clearJumpTimeout()
          isLoading = false
        }

        if (!isLoading) {
          clearJumpTimeout()
          const baseIndex =
            Math.floor(
              Math.floor(scrollTop / avgItemHeight) / props.bufferSize,
            ) * props.bufferSize

          blockAStartIndex = Math.max(0, baseIndex - props.bufferSize)
          blockBStartIndex = baseIndex
          blockCStartIndex = Math.min(
            props.totalItems - props.bufferSize,
            baseIndex + props.bufferSize,
          )
          blockPositions = ['A', 'B', 'C']
          isLoading = true
          loadBlock(blockAStartIndex, 'all')
          jumpTimeout = setTimeout(() => {
            positionBlocks()
            isLoading = false
            jumpTimeout = 0
          }, 250)
          return
        }
      }

      if (
        nextBlocks[below] &&
        (scrollBottom > nextBlocks[below].y + nextBlocks[below].height - 100 ||
          scrollTop > nextBlocks[below].y + nextBlocks[below].height) &&
        !isLoading
      ) {
        handleScroll('down')
      }

      if (
        nextBlocks[above] &&
        (scrollTop < nextBlocks[above].y + 100 ||
          scrollBottom < nextBlocks[above].y) &&
        !isLoading
      ) {
        handleScroll('up')
      }
    }
```

--------------------------------

### Manage Graph Layers

Source: https://data-star.dev/examples/rocket_flow

Ensures a specific SVG group layer exists within the graph container.

```javascript
const ensureLayer = (name) => {
  let layer = graph?.querySelector(`g[data-layer="${name}"]`)
  if (layer instanceof SVGGElement) return layer
  layer = document.createElementNS(SVG_NS, 'g')
  layer.dataset.layer = name
  graph?.append(layer)
  return layer
}
```

--------------------------------

### External Synchronous Function

Source: https://data-star.dev/guide/datastar_expressions

Define a simple JavaScript function that takes data as an argument and returns a processed result. This function can be called directly from Datastar expressions.

```javascript
1function myfunction(data) {
2    return `You entered: ${data}`;
3}
```

--------------------------------

### Access Element Properties in Datastar Expression

Source: https://data-star.dev/docs.md

Displays the offset height of the current element using the 'el' variable within a Datastar expression. 'el' refers to the element the attribute is attached to.

```html
<div data-text="el.offsetHeight"></div>
```

--------------------------------

### data-effect

Source: https://data-star.dev/reference

The `data-effect` attribute executes an expression on page load and whenever any signals in the expression change, enabling side effects like updating other signals or making backend requests.

```APIDOC
## data-effect

Executes an expression on page load and whenever any signals in the expression change. This is useful for performing side effects, such as updating other signals, making requests to the backend, or manipulating the DOM.

### Example

```html
<div data-effect="$foo = $bar + $baz"></div>
```
```

--------------------------------

### HTML with Data Attribute for Polling

Source: https://data-star.dev/how_tos/poll_the_backend_at_regular_intervals

This HTML snippet demonstrates how to use a custom data attribute to configure polling intervals. The `data-on-interval__duration` attribute specifies the polling duration in seconds and the endpoint to fetch data from. The content within the div will be updated with the current time.

```html
<div id="time"
     data-on-interval__duration.${duration}s="@get('/endpoint')"
  >
    ${currentTime.toISOString()}
  </div>
```

--------------------------------

### Backend: Remove Button Event

Source: https://data-star.dev/how_tos/load_more_list_items

A Datastar event to remove an element from the DOM. Use this to hide or remove UI elements, such as a "load more" button, when no more data is available.

```text
1event: datastar-patch-elements
2data: selector #load-more
3data: mode remove
4

```

--------------------------------

### data-class with Camel Case Modifier

Source: https://data-star.dev/reference

Use the `__case.camel` modifier with `data-class` to convert the class name to camel case.

```html
<div data-class:my-class__case.camel="$foo"></div>
```

--------------------------------

### data-json-signals

Source: https://data-star.dev/docs.md

The `data-json-signals` attribute sets the text content of an element to a reactive, JSON stringified version of signals, which is helpful for debugging.

```APIDOC
## `data-json-signals`

### Description
Displays a reactive JSON stringified version of signals as the element's text content.

### Usage
```html
<!-- Display all signals -->
<pre data-json-signals></pre>
```

### Filtering Signals
Optionally provide a filter object to include or exclude signals using regular expressions.

```html
<!-- Only show signals that include "user" in their path -->
<pre data-json-signals="{include: /user/}"></pre>

<!-- Show all signals except those ending in "temp" -->
<pre data-json-signals="{exclude: /temp$/}"></pre>

<!-- Combine include and exclude filters -->
<pre data-json-signals="{include: /^app/, exclude: /password/}"></pre>
```

### Modifiers
#### `__terse`
Outputs JSON in a compact format without extra whitespace.
```

--------------------------------

### Numeric Prop Decoders

Source: https://data-star.dev/reference/rocket

Enforce numeric constraints like range, rounding, and mapping on component props.

```javascript
props: ({ number }) => ({
  width: number.min(0).default(320),
  opacity: number.clamp(0, 1).ceil(2).default(1),
  progress: number.clamp(0, 100).step(5),
  normalizedX: number.fit(0, 1920, 0, 1, true, false),
})
```

--------------------------------

### Clamp Zoom Value

Source: https://data-star.dev/examples/rocket_flow

Ensures a zoom value is within the acceptable range of 0.05 to 16.

```javascript
const clampZoom = (value) => {
  const next = Number(value)
  if (!Number.isFinite(next) || next <= 0) return 1
  return Math.min(16, Math.max(0.05, next))
}
```

--------------------------------

### Apply Interval Duration Modifier

Source: https://data-star.dev/reference/attributes

Customizes the interval duration using the duration modifier.

```html
<div data-on-interval__duration.500ms="$count++"></div>
```

--------------------------------

### JSON Payload for Patching Signals

Source: https://data-star.dev/docs.md

A JSON object used to patch frontend signals. This format is expected when the response content-type is application/json.

```json
{"hal": "Affirmative, Dave. I read you."}
```

--------------------------------

### Change SVG Circle Color

Source: https://data-star.dev/examples/svg_morphing

This Go snippet demonstrates how to change the fill color of an SVG circle using `sse.PatchElements`. The target SVG element must have a corresponding ID.

```go
1svgMorphingRouter.Get("/circle_color", func(w http.ResponseWriter, r *http.Request) {
2    sse := datastar.NewSSE(w, r)
3    color := svgColors[rand.N(len(svgColors))]
4    sse.PatchElements(fmt.Sprintf(`<svg id="circle-demo"><circle cx="50" cy="50" r="40" fill="%s" /></svg>`, color))
5})

```

--------------------------------

### Change SVG Circle Radius

Source: https://data-star.dev/examples/svg_morphing

This Go snippet shows how to morph the radius of an SVG circle. Ensure the target SVG element has the correct ID for the patch to apply.

```go
1svgMorphingRouter.Get("/circle_size", func(w http.ResponseWriter, r *http.Request) {
2    sse := datastar.NewSSE(w, r)
3    radius := 15 + rand.N(45) // Random radius between 15-60
4    sse.PatchElements(fmt.Sprintf(`<svg id="size-demo"><circle cx="50" cy="50" r="%d" fill="green" /></svg>`, radius))
5})

```

--------------------------------

### Rocket renderOnPropChange Type

Source: https://data-star.dev/reference/rocket

Defines the `renderOnPropChange` property, which can be a boolean to enable/disable or a function to conditionally control re-rendering based on prop changes.

```typescript
1renderOnPropChange?:
2  | boolean
3  | ((context: {
4      host: HTMLElement
5      props: Props
6      changes: Partial<Props>
7    }) => boolean)
```
