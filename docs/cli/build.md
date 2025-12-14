# `taupy build`

Produce a **production-ready** build of your TauPy application inside the `./target` folder.

The command performs four main steps:

1. **Rust launcher** – copies a prebuilt `taupy.exe` and `WebView2Loader.dll` (or uses your own).
2. **Frontend** – runs `npm run build` if a React project is detected (skipped otherwise).
3. **Backend** – bundles `main.py` into `app.exe` via **Nuitka** (onefile by default).
4. **Packaging** – copies all artefacts into `./target`, ready to ship or code-sign.

---

## Usage

```bash
taupy build
```

```
Usage: taupy build [OPTIONS]

  Build TauPy app into ./target
```

There are no extra flags today – the behaviour is driven by **`taupy.toml`**. For example:

```toml
[build]
onefile = true      # disable if you prefer directory mode

[build.modules]
pandas = true   # include extra Python modules
```

---

## What ends up in `target/`
| Path | Description |
|------|-------------|
| `app.exe` | Bundled backend (Python → C → EXE) |
| `dist/`   | Static frontend assets (if any) |
| `launcher/taupy.exe` | Rust/WebView2 launcher |
| `launcher/WebView2Loader.dll` | Loader DLL for Windows runtime |

You can now zip the folder or wrap it with an installer (MSI, Inno Setup, etc.).

---

## Adding extra Python modules
If your backend imports C-extensions or pure-Python libs not auto-detected by Nuitka, list them under `[build.modules]` in `taupy.toml`:

```toml
[build.modules]
matplotlib = true
lxml = true
```

TauPy passes them to Nuitka via `--include-module=...` flags.

---

## Exit codes
* `0` – build succeeded
* `1` – missing dependency or build tool failed

---

## Troubleshooting
* "nuitka not found" – install with `pip install nuitka` (Python ≥3.11)
* "npm build failed" – fix errors in your React project; ensure `npm run build` passes standalone
* Antivirus deleting `app.exe` – some AVs falsely flag one-file executables; whitelist or use directory mode
