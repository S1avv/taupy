# Routing

TauPy ships with a minimal router for Python-first UIs.

## Defining routes
Use `@app.route(path)` on callables that return a component:

```python
from taupy import App, VStack, Text

app = App("Demo", 800, 600)

@app.route("/")
def home():
    return VStack(Text("Hello"))
```

Routes can return synchronous or async components. Async handlers are awaited automatically.

## Navigation from code
Call `await app.navigate("/settings")` to render another route. The existing root component is replaced and the new HTML is broadcast to clients.

## Router API
- `router.register(path, handler)`: Register a handler manually.
- `router.get(path)`: Retrieve a handler (used internally).

See `tests/test_router.py` for usage examples.
