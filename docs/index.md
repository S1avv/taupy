# TauPy

> Build desktop apps with **Python + Rust**, and drop in React/Vite when you want. Fast reloads, native window controls, and a tiny API surface.

## Why TauPy
- **Hybrid by design** - Python backend + Rust launcher; use Python widgets or a full React front-end.
- **Hot dev loop** - edit → window refreshes near-instantly, no page reload dance.
- **Native window API** - minimize/maximize/resize/drag, all routed through Python to the launcher.
- **Shipping ready** - `taupy build` bundles your front-end, rebuilds the launcher, and Nuitka-packages the backend.


## Quick Start

```bash
# Install
pip install taupy-framework

# Scaffold a project
taupy new my_app
cd my_app

# Start dev mode
# For the React template install npm deps first
npm install
taupy dev
```

Your app opens simultaneously in the browser and the native window with instant reloads.

## Minimal Python UI Example

```python
from taupy import App, VStack, Text, Button, State
from taupy.events import Click

app = App("Hello TauPy", 800, 500)
msg = State("Hello, TauPy!")

@app.dispatcher.on_click("btn_hello")
async def hello(_: Click):
    msg.set("Button clicked!")

@app.route("/")
def home():
    return VStack(Text(msg), Button("Click me", id="btn_hello"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run(VStack(id="root")))
```

## Repository Layout

```
.
├─ taupy/            # Framework source code
├─ docs/             # This documentation (MkDocs + Material)
├─ examples/         # Ready-to-run demo projects
└─ tests/            # Unit & integration tests
```

## Community

- GitHub: <https://github.com/S1avv/taupy>
- Issues & PRs are welcome!

## License

Released under the **MIT** license - free for commercial and open-source projects alike.
