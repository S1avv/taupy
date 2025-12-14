# `taupy dev`

Launch the **development environment** for your TauPy project. It can spin up:

1. The Python backend with automatic code reload (via `watchdog`).
2. The Vite/React dev server (if a `package.json` is detected) **or** connect to an external frontend you specify.
3. A TauPy desktop window that loads the frontend - opening dev-tools if you ask so.

---

## Usage

```bash
taupy dev [OPTIONS]
```

```
Usage: taupy dev [OPTIONS]

  Start TauPy backend alongside the Vite dev server (if present).

Options:
  --backend-only        Run only TauPy backend (skip frontend dev server).
  --frontend-only       Run only frontend dev server (skip backend).
  --port INTEGER        HTTP port for TauPy app or external frontend.
  --ws-port INTEGER     WebSocket port for TauPy backend (0 = auto).
  --external-http TEXT  External frontend URL (e.g. http://localhost:5173).
  --open-devtools       Open browser devtools in TauPy window.
  --help                Show this message and exit.
```

If neither `--backend-only` nor `--frontend-only` is given (the default), **both** parts start in parallel and talk to each other automatically.

### Typical workflow

```bash
# 1. Make sure you are in project root
taupy dev            # spins up backend + Vite (if present) + window

# 2. Edit Python files → backend reloads instantly
# 3. Edit React/Vite files → Vite hot-reloads, window refreshes
# 4. Press Ctrl+C to stop everything
```

### Environment variables respected
| Variable | Purpose |
|----------|---------|
| `TAUPY_HTTP_PORT` | Override HTTP port without `--port` flag |
| `TAUPY_WS_PORT`   | Override WebSocket port |
| `TAUPY_EXTERNAL_HTTP` | Force-use external dev server |

---

## Exit codes
* `0` – servers shut down gracefully (Ctrl+C)
* `>0` – backend or frontend process exited with error

---

## Tips
* Combine with **`--open-devtools`** while debugging front-end code.
* Use **`--backend-only`** when integrating TauPy backend with an existing local web app.
* If the chosen port is busy, TauPy will try the next free one unless you forced it via `--port`.
