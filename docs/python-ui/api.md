# Python UI API

Key building blocks when writing Python-first interfaces.

## App
- `App(title, width, height, **opts)`: Main controller. Manages routing, server, and window.
- `app.route(path)`: Decorator to register routes.
- `await app.navigate(path)`: Switch to another route.

## Components
- `Component`: Base class with `props`, `children`, `render()`, and `id`.
- Layout helpers: `HStack`, `VStack`, `Center`, `Spacer`, `Scroll`, `Container`.
- Elements: `Div`, `Button`, `Text`, `Input`, `Table`, `Image`, `Modal`.

## State
- `State(initial)`: Reactive value. Call to get/set: `state()` / `state(new_value)`.
- `state.subscribe(callback)`: Subscribe to changes. The callback receives the new value.

## Events
- `Click`, `Input`, `Resize` events are dispatched via `Dispatcher`.
- Use `@app.dispatcher.on_click("btn_id")` or `on_input("field_id")` to register handlers.

## Server
- `TauServer.broadcast(message)`: Send a JSON message to connected clients.

For concrete examples, see `tests/test_components_basic.py` and `tests/test_events.py`.
