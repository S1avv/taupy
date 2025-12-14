# Quick Start

1. Install TauPy from PyPI.
2. Scaffold a new project with the CLI.
3. Run the development server with hot-reload.
4. Build a production-ready binary.

> **Estimated time:** 2 minutes

---

## 1 – Install TauPy

You only need Python 3.8 or newer and `pip`:

```bash
python -m pip install --upgrade taupy-framework
```

Verify the installation:

```bash
$ taupy --version
TauPy 0.4.0
```

---

## 2 – Create a new project

The `taupy new` command generates the boilerplate for you. Two templates are available: **python** (pure-Python UI) and **react** (Vite + React front-end).

```bash
taupy new my_app
```

---

## 3 – Run in development mode

Navigate into the project directory and launch the app in _dev_ mode. The CLI watches your source files and reloads the window on every save.

```bash
cd my_app

taupy dev
```

When the server is ready, a desktop window opens. Edit `app.py` (or your React components); changes appear instantly.

---

## 4 – Build a standalone executable

Ready to share your app? Run:

```bash
taupy build
```

This produces `dist/my_app.exe`. The binary bundles Python, your code and the TauPy launcher – users can run it **without installing Python or any dependencies**.

---

## What’s next?

* Dive deeper into [Python UI development](./python-ui/overview.md).
* Learn how to create rich React front-ends with [React integration](./react.md).
* Check the [Configuration](./configuration.md) reference for window size, icons and advanced options.
* Join the community on [GitHub](https://github.com/S1avv/taupy)
