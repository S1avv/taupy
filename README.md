<p align="center">
  <img src="assets/lg.png" alt="TauPy" width="auto" height="240" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-alpha-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/platform-Windows%2064bit-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/runtime-WebView2-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/speed-unbelievably%20fast-9cf?style=for-the-badge" />
  <img src="https://img.shields.io/badge/framework-built%20for%20future-black?style=for-the-badge" />
</p>

# TauPy

Build desktop apps with **Python + Rust**, and drop in React/Vite when you want. Fast reloads, native window controls, and a tiny API surface.

## Why TauPy
- **Hybrid by design** - Python backend + Rust launcher; use Python widgets or a full React front-end.
- **Hot dev loop** - edit → window refreshes near-instantly, no page reload dance.
- **Native window API** - minimize/maximize/resize/drag, all routed through Python to the launcher.
- **Shipping ready** - `taupy build` bundles your front-end, rebuilds the launcher, and Nuitka-packages the backend.

## Code example (Python UI)
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

## Quick start (React front-end)
```bash
taupy new [app_name]
cd [app_name]
npm install
taupy dev
```

## Build
```bash
taupy build
```
Pipeline:
1) Build React/Vite (if present) → `target/dist`  
2) `cargo build --release` for the launcher → `target/launcher`  
3) Nuitka bundle backend → `target/app.exe`

## Performance snapshot (indicative)

| Scenario | TauPy (Python + Rust) | PyQt / PySide | Tkinter | Electron |
|--------|------------------------|---------------|----------|----------|
| Cold start (release build) | ~300–600 ms | ~900 ms – 1.8 s | ~500–900 ms | ~1.5 – 3 s |
| Hot reload (code → UI) | ~40–120 ms (WS diff) | Full widget refresh | Full redraw | ~200–500 ms |
| UI update (state → render) | ~10–40 ms | QWidget update | Full widget update | Virtual DOM diff |
| Bundle size | ~6–15 MB + dist | 40–80 MB | ~2–5 MB | 120+ MB |
| UI stack | HTML/CSS (WebView) | Native Qt | Native Tk | Chromium |

### Measurement conditions

> Measurements taken on Windows 11, Ryzen 7 5800X, NVMe SSD.  
> Release builds, minimal "hello world" applications.  
> Numbers are indicative and vary by project size and configuration.

## TauPy CLI
- `taupy dev` — run backend + external front-end (Vite) with hot reload.
- `taupy build` — build front-end, launcher, and Nuitka bundle into `target/`.
- `taupy new <name>` — scaffold a new TauPy project.

## Dev vs Prod (auto)
- Dev (`--dev`): external HTTP (Vite 5173), hot reload.
- Prod: serves bundled `dist/` on 8000. Override with `TAUPY_EXTERNAL_HTTP` / `TAUPY_HTTP_PORT`.

## Roadmap
- Cross-platform launcher (Linux/macOS)
- Native dialogs & notifications
- Packaging presets (single-file)
- Built-in icon set & theme presets
- DevTools/inspector mode
- Playground in browser

## Requirements
- Windows 64-bit, Python 3.11+
- Rust toolchain (launcher rebuild)
- Node.js (for React/Vite, optional)

📜 License  
TauPy is released under the MIT License. Free for commercial and personal use.

💬 Contributing  
Contributions are welcome!

⭐ Support the Project  
If TauPy inspires you - please star the repository. Every ⭐ makes development faster ❤️
