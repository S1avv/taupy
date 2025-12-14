# `taupy new`

Create a brand-new **TauPy** application in seconds.

The command copies a ready-to-run template, asks a few questions (or reads CLI flags), and leaves you with a fully-wired project that already contains:

* `main.py` – Python backend entry-point (widget or socket version depending on chosen template)
* `launcher/` – prebuilt `taupy.exe` launcher and `WebView2Loader.dll`
* `dist/` – minimal `client.js` required for Python-only UI
* `vite-react` (optional) – Vite + React template when the *react* frontend is selected
* `taupy.toml` – project configuration generated from your answers

---

## Usage

```bash
# Interactive mode (prompts for template, ports, etc.)
taupy new my-app
```

```
Usage: taupy new [OPTIONS] NAME

  Scaffold a new TauPy project with recommended structure.

Arguments:
  NAME  Target directory that will be created.

Options:
  -f, --frontend [react|python]  Choose UI template (react = Vite + React, python = TauPy widgets). If omitted you will be asked in interactive mode.
  --help                        Show this message and exit.
```

### What happens under the hood
1. Copies starter files from TauPy’s internal *utils* folder.
2. Generates *taupy.toml* using your answers (ports, hot-reload mode, etc.).
3. If you chose **react**, Vite template is copied and ready for `npm install`.
4. Prints quick *next steps* so you can `cd` into the directory and run `taupy dev`.

---

## Exit codes
* `0` – project created successfully
* `1` – target directory exists or user aborted