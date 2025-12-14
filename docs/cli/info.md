# `taupy info`

Display a concise summary of your **local environment** – handy for bug reports and when you need to figure out why a project fails to run.

The command inspects the current working directory, your system and the installed `taupy` package, then prints the detected versions.

---

## Usage

```bash
taupy info
```

Example output:

```text
TauPy v0.4.0
Python 3.11.7
OS: Windows 11
WebView: WebView2 120.0.2210.91
Frontend: React (external)
Launcher: rust/release
```

---

## What gets reported?

| Field | Meaning |
|-------|---------|
| **TauPy** | Installed version of `taupy-framework` (PyPI) |
| **Python** | Exact Python interpreter version used by the CLI |
| **OS** | Operating-system family & release as detected by `platform` |
| **WebView** | Microsoft Edge WebView2 runtime build (Windows only) |
| **Frontend** | `Python`, `React`, or `React (external)` depending on project files and `taupy.toml` |
| **Launcher** | Whether the Rust launcher binary is present in `launcher/` (built in *dev*/ *build*) |

The command does **not** phone home – all checks are performed locally.

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Ran successfully |
| `1`  | Unexpected error occurred |