# TauPy CLI Overview

TauPy ships with a single **`taupy`** executable that streamlines the whole lifecycle of your app – from scaffolding a fresh project to shipping a signed, single-file binary.  If you know `npm`, `cargo`, or `flutter`, you will feel right at home.

```bash
$ taupy --help
Usage: taupy [OPTIONS] COMMAND [ARGS]...

  TauPy command-line interface

Options:
  -V, --version  Show the current TauPy version and exit
  -v, --verbose  Enable debug logging
  -q, --quiet    Only show warnings & errors
  --help         Show this message and exit

Commands:
  new       Scaffold a new TauPy project
  dev       Start the app in hot-reload development mode
  build     Build a production binary (Nuitka + launcher)
  config    Inspect or generate taupy.toml
  doctor    Verify your toolchain & environment
  info      Print versions and environment summary
```

Most real-world workflows boil down to three commands:

| Phase | Command | What it does |
|-------|---------|--------------|
| **Bootstrap** | `taupy new my_app` | Generates project with Python widgets or React template |
| **Develop** | `cd my_app`<br>`taupy dev` | Watches your code, reloads the window instantly |
| **Ship** | `taupy build` | Produces `dist/my_app.exe` ready for distribution |

---

## Global flags

| Flag | Description |
|------|-------------|
| `--verbose` | Print extra logs from the backend and launcher |
| `--quiet` | Suppress non-error output (useful in CI) |
| `--version` | Show CLI + framework version |

You can combine them: `taupy --verbose dev`.

---

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `TAUPY_HTTP_PORT` | Force a specific port for the internal HTTP server | random free port |
| `TAUPY_EXTERNAL_HTTP` | URL of an external front-end dev server (e.g. Vite) to load instead of bundled HTML | - |
| `TAUPY_LAUNCHER_PATH` | Absolute path to a custom-built launcher executable | built-in launcher |
| `TAUPY_NO_COLOR` | Disable ANSI colors in CLI output | off |

These can be useful in CI pipelines or advanced setups.

---

## Command reference

The table below links to detailed pages for each sub-command:

| Command | Docs |
|---------|------|
| `new`   | [taupy new](./new.md) |
| `dev`   | [taupy dev](./dev.md) |
| `build` | [taupy build](./build.md) |
| `config`| [taupy config](./config.md) |
| `doctor`| [taupy doctor](./doctor.md) |
| `info`  | [taupy info](./info.md) |

---

## Power user tips

* **Multiple Python versions** – create a virtualenv with Python 3.11+ and install `taupy-framework` there; the launcher will embed that interpreter into the final EXE.
* **Continuous integration** – run `taupy doctor` in CI to verify Rust, Node and Nuitka are present before building.
* **Updating** – simply `pip install -U taupy-framework`; the CLI auto-detects a newer version and suggests to upgrade.

---