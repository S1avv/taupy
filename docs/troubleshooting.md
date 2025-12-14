# Troubleshooting

Quick fixes for common problems when installing, developing, building, or running TauPy apps.

---

## 1. Installation & environment

- **WebView2 runtime not found**  
  Run `taupy doctor` to confirm. Install from Microsoft: <https://go.microsoft.com/fwlink/p/?LinkId=2124703>.

- **Python version mismatch**  
  Use Python 3.9+ (CPython recommended). Verify: `python -V`.

- **Node/npm missing (React projects)**  
  Install Node 18+ and npm 9+. Check with `node -v` and `npm -v`.

- **Long path errors on Windows**  
  Enable long paths once: `git config --system core.longpaths true`.

---

## 2. Dev mode (`taupy dev`)

- **Port already in use (5173/8765/8000)**  
  Pick another port: `TAUPY_HTTP_PORT=5174 TAUPY_WS_PORT=8766 taupy dev`. Close the conflicting app or free the port.

- **Blank window or 404 in dev**  
  Vite may not be running. Ensure `npm run dev` succeeded or rerun `taupy dev` so TauPy starts Vite for you. Confirm the Vite URL in logs (`http://localhost:<port>`).

- **WebSocket does not connect / HMR not working**  
  Firewalls can block localhost WS. Allow local connections on `8765`. If developing over a network share, move the project to a local disk so file watching works reliably.

- **`npm` not found message during `taupy dev`**  
  Install Node/npm or switch to the Python template (no NPM needed). On Windows, ensure `npm.cmd` is on PATH.

---

## 3. Build & packaging (`taupy build`)

- **`nuitka not found`**  
  Install in the active environment: `python -m pip install nuitka`.

- **`npm run build` fails**  
  Fix React/Vite errors first. Run `npm run build` manually to see the stack trace; check Node/npm versions against `package.json` engines.

- **Antivirus deletes `app.exe`**  
  Switch to directory mode: set `onefile = false` in `taupy.toml` and rebuild, or whitelist the file.

- **Packaged app shows blank window**  
  Ensure `dist/` exists next to `app.exe` and `launcher/`. In production keep `external_http = false` so assets load locally.

- **`taupy.exe` missing**  
  Check `launcher/` inside `target/`. If absent, rerun `taupy build`; if you customized the launcher, copy your built binary there.

---

## 4. Runtime issues

- **Window does not open**  
  Verify `launcher/taupy.exe` runs (double-click in `target/`). Check that WebView2 runtime is installed and not blocked by antivirus.

- **WebSocket drops in packaged app**  
  Firewall may block localhost. Allow `app.exe` and ports `8000/8765`. Avoid setting `TAUPY_EXTERNAL_HTTP` in production unless you really load an external server.

- **Slow startup**  
  Onefile EXEs decompress on first run. Use `onefile = false` for faster start, or keep the app warm during demos.

---

## 5. If nothing helps

- Run `taupy doctor` and share its output.
- Re-run with debug logging in React: construct `new TaupyClient({ debug: true })`.
- Open an issue on GitHub with OS version, Python/Node versions, the command you ran, and full logs.
