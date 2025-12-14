# React Integration

Use TauPy as the backend and native window host for React or TypeScript-based front-ends.

---

## 1. When to pick React
- You want full control over UI/UX with JSX, CSS, and the NPM ecosystem.
- You already have a Vite/React SPA and only need a desktop wrapper plus a Python backend.
- You prefer to keep business logic in Python but render a modern web UI.

---

## 2. Scaffold a React project

```bash
taupy new my_app -f react
cd my_app
npm install
taupy dev
```

What you get:
- `main.py` - TauPy backend configured for raw HTML mode.
- `src/` - Vite + React + TypeScript starter (see `src/taupyClient.ts`).
- `dist/` - Build output served in production.
- `launcher/` - `taupy.exe` + `WebView2Loader.dll` used to open the desktop window.
- `taupy.toml` - Ports, hot reload mode, and build flags.

---

## 3. Development workflow
- Run `taupy dev` in project root. It starts `python main.py --dev`, launches `npm run dev -- --host --port <TAUPY_HTTP_PORT>` if a `package.json` is present, and opens the TauPy window.
- Default ports: HTTP `5173` (Vite) and WebSocket `8765`. Override with `TAUPY_HTTP_PORT` and `TAUPY_WS_PORT`.
- TauPy sets `TAUPY_EXTERNAL_HTTP=1` in dev so the window loads the Vite server instead of local `dist/`.
- Use `npm run dev` separately if you want, then run `python main.py --dev` with `TAUPY_EXTERNAL_HTTP=1` to point the window at that server.
- To inspect the page, set `TAUPY_OPEN_DEVTOOLS=1` (or run `python main.py --open-devtools`) before starting dev mode.

---

## 4. WebSocket bridge with `TaupyClient`

`src/taupyClient.ts` is a tiny helper around `WebSocket`. It auto-reconnects, lets you subscribe to messages by `type`, and reports connection status changes.

```tsx
import { useEffect, useMemo, useState } from "react";
import { TaupyClient } from "./taupyClient";

export function useTaupy() {
  const client = useMemo(() => new TaupyClient({ debug: true }), []);
  const [status, setStatus] = useState<"connecting" | "open" | "closed">("connecting");

  useEffect(() => {
    client.connect();
    const offStatus = client.onStatus(setStatus);
    return () => {
      offStatus();
      client.close();
    };
  }, [client]);

  return { client, status };
}
```

### Send events from React to Python
Python listens for `click`, `input`, and `window_cmd` messages. Use matching IDs in React and in backend handlers.

```tsx
client.send({ type: "click", id: "save-btn" });
client.send({ type: "input", id: "search-box", value: query });
client.send({ type: "window_cmd", command: { type: "toggle_fullscreen" } });
```

```python
from taupy import App, AppMode
from taupy.events import Click, Input

app = App("React + TauPy", 900, 640, mode=AppMode.RAW_HTML)

@app.dispatcher.on_click("save-btn")
async def save(_: Click):
    print("Save requested from React UI")

@app.dispatcher.on_input("search-box")
async def search(evt: Input):
    print("Search:", evt.value)
```

Supported `window_cmd.command` payloads include `toggle_fullscreen`, `minimize`, `maximize`, `restore`, `set_title`, `set_size`, `set_position`, and more (see `App.send_window_command`).

### Send data from Python to React
Broadcast JSON messages and subscribe by `type` on the React side.

```python
import asyncio
from taupy import App, AppMode

app = App("React push", 800, 600, mode=AppMode.RAW_HTML)

@app.on_connect
async def hello():
    await app.server.broadcast({"type": "welcome", "payload": {"user": "Alice"}})
```

```tsx
useEffect(() => {
  const off = client.on("welcome", (msg) => {
    setUser(msg.payload.user);
  });
  return off;
}, [client]);
```

Built-in message types you may see: `hot_reload` (triggers a reload in dev) and `hmr_error` (syntax error details).

---

## 5. Building for production
- Run `npm run build` to emit static assets into `dist/`.
- Run `taupy build` to bundle everything: it runs the React build if `package.json` exists, packages the Python backend with Nuitka, and copies launcher binaries into `target/`.
- In production `AppMode.RAW_HTML` serves files from `dist/` through the launcher's tiny HTTP server. Keep `external_http` set to `false` (default) so assets are loaded locally.
- If you must load a remote or already-running frontend in production, set `TAUPY_EXTERNAL_HTTP=1` and point `TAUPY_HTTP_PORT` (or the full URL in `taupy.toml`) to it.

---

## 6. Tips
- Keep IDs stable between React components and backend handlers to avoid missed events.
- For structured data from React, serialize it into the `value` field of an `input` message (JSON string) and parse in Python.
- Use `client.onStatus` to show an offline banner if the WebSocket drops.
- Test `npm run build` alone before `taupy build` to catch front-end errors early.
