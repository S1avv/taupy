# Vanilla Frontend

Use TauPy with plain HTML, CSS, and JavaScript-no React or Python widgets. The vanilla template serves `dist/` as-is while TauPy provides the window, WebSocket bridge, and backend events.

---

## 1. When to pick Vanilla
- You already have static HTML/CSS or a lightweight JS app and need a desktop wrapper.
- You want zero React/NPM dependencies (or will add your own bundler later).
- You prefer to keep backend logic in Python but author UI in raw markup.

---

## 2. Scaffold a project

```bash
taupy new my_app -f vanilla
cd my_app
taupy dev
```

Template contents:
- `main.py` - TauPy backend in `AppMode.RAW_HTML`.
- `dist/` - `index.html`, `style.css`, `main.js`, plus `client.js` (WebSocket bridge).
- `launcher/` - `taupy.exe` + `WebView2Loader.dll`.
- `taupy.toml` - ports and build flags.

Layout:

```
my_app/
  main.py
  dist/
    index.html
    style.css
    main.js
    client.js
  launcher/
    taupy.exe
    WebView2Loader.dll
  taupy.toml
```

> Tip: Replace `dist/` with assets from any bundler; keep `client.js` or reimplement its bridge.

---

## 3. Development workflow
- Run `taupy dev`. Vanilla mode watches `dist/` and triggers a live reload on save.
- Default ports: HTTP `8000`, WebSocket `8765`. Override with `TAUPY_HTTP_PORT` and `TAUPY_WS_PORT`.
- `TAUPY_EXTERNAL_HTTP` is not needed; assets are served locally.
- Add `--open-devtools` (or `TAUPY_OPEN_DEVTOOLS=1`) to debug in the TauPy window.

---

## 4. Wire events from HTML to Python

Attach `data-component-id` to elements. `client.js` sends clicks and inputs over WebSocket.

**HTML (`dist/index.html`):**
```html
<button data-component-id="save-btn">Save</button>
<input type="text" data-component-id="search-box" />
<script src="./client.js"></script>
<script type="module" src="./main.js"></script>
```

**Python (`main.py`):**
```python
import asyncio
from taupy import App, AppMode
from taupy.events import Click, Input

app = App("Vanilla TauPy", 900, 640, mode=AppMode.RAW_HTML)

@app.dispatcher.on_click("save-btn")
async def save(_: Click):
    print("Save requested")

@app.dispatcher.on_input("search-box")
async def on_search(evt: Input):
    print("Query:", evt.value)

async def main():
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
```

`client.js` already handles DOM updates (`update_text`, `update_html`, `replace`, `update_input`), theme changes, and `hot_reload` messages from Python.

---

## 5. Custom messages and window commands

You can send custom payloads over the same WebSocket:

```js
// dist/main.js
const socket = new WebSocket("ws://localhost:8765");
socket.addEventListener("open", () => {
  socket.send(JSON.stringify({ type: "window_cmd", command: { type: "toggle_fullscreen" } }));
});
```

Supported window commands include `toggle_fullscreen`, `minimize`, `maximize`, `restore`, `set_title`, `set_size`, and more (see `App.send_window_command`).

---

## 6. Build and distribute

```bash
taupy build
```

The build copies `dist/`, bundles the backend with Nuitka, and writes `target/` with `app.exe`, `dist/`, and `launcher/`. See [Build & Distribution](./build.md) for release details.

---

## 7. Tips
- Keep `data-component-id` unique to avoid handler conflicts.
- If antivirus flags onefile builds, set `onefile = false` in `taupy.toml` and rebuild.
- To debug WebSocket traffic, open DevTools and watch console logs; verify ports `8000/8765` are free. 
