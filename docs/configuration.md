# Configuration

TauPy keeps configuration lightweight. Most settings are passed to the `App` constructor or CLI flags.

## Window settings
- `title`: Window title.
- `width` / `height`: Initial window size.
- `frameless`: Hide the native frame (`--frameless`).
- `transparent`: Transparent background (`--transparent`).
- `always_on_top`: Keep window above others (`--always-on-top`).
- `resizable`: Allow resizing (`--resizable=false` to disable).
- `min_width` / `min_height` / `max_width` / `max_height`: Size bounds.

## Server ports
- `http_port`: Port for static assets (default 8000 or 5173 in dev external mode).
- `ws_port`: WebSocket port (default 8765, can be overridden via `TAUPY_WS_PORT`).
- `TAUPY_EXTERNAL_HTTP`: Set to `1` to let an external dev server (e.g. Vite) serve assets.

## Dev flags
- `--dev`: Enables hot reload and dev UI output.
- `--no-window`: Run headless (useful for CI).
- `--open-devtools`: Opens WebView devtools where supported.