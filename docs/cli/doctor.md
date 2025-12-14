# `taupy doctor`

Run a series of environment checks to ensure your system is ready to **develop** and **build** TauPy applications.

The command validates the presence and versions of required toolchains and runtimes:

| Check | Requirement |
|-------|-------------|
| Python | 3.9 or newer |
| Rust   | `rustc` + `cargo` available in `PATH` |
| Node.js | `node` + `npm` available (needed for React template) |
| WebView2 | Microsoft Edge WebView2 Runtime installed (Windows only) |
| Nuitka | Python compiler used for producing single-exe builds |

---

## Usage

```bash
taupy doctor
```

Example output:

```
TauPy Doctor

[OK] Python >=3.11 - 3.11.7
[OK] Rust toolchain (rustc/cargo) - rustc 1.76.0 (a2a35644c 2025-02-01); cargo 1.76.0
[OK] Node.js + npm - v20.10.0; 10.2.0
[OK] WebView2 runtime (Windows) - WebView2 runtime registry found (HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients)
[OK] Nuitka - Nuitka 2.1.1 Commercial: None (with Python 3.11.7 on win32)
```

Any missing dependency is reported with `[ERR]` and a helpful message.

---

## Exit codes
* `0` – all checks passed.
* `1` – at least one required dependency is missing or outdated.

Use this in CI pipelines to fail early:

```yaml
- name: Verify build environment
  run: taupy doctor
```