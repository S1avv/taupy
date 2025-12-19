import os
import shutil
import subprocess
import sys
import click

OK = "[OK]"
WARN = "[WARN]"
ERR = "[ERR]"


def _check_cmd(name: str, args: list[str] | None = None):
    args = args or [name, "--version"]
    try:
        completed = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
        )
        return completed.returncode == 0, (completed.stdout or "").strip()
    except Exception as exc:
        return False, str(exc)


def _check_python():
    ver = sys.version_info
    ok = ver.major == 3 and ver.minor >= 11
    return ok, f"{ver.major}.{ver.minor}.{ver.micro}"


def _check_rust():
    rustc = shutil.which("rustc") or shutil.which("rustc.exe")
    cargo = shutil.which("cargo") or shutil.which("cargo.exe")
    ok = rustc is not None and cargo is not None
    detail = []
    if rustc:
        _, out = _check_cmd(rustc.split(os.sep)[-1])
        detail.append(out.splitlines()[0] if out else "rustc found")
    if cargo:
        _, out = _check_cmd(cargo.split(os.sep)[-1])
        detail.append(out.splitlines()[0] if out else "cargo found")
    return ok, "; ".join(detail) if detail else "not found"


def _check_node():
    node = shutil.which("node") or shutil.which("node.exe")
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    ok = node is not None and npm is not None
    detail = []
    if node:
        _, out = _check_cmd(node.split(os.sep)[-1])
        detail.append(out.splitlines()[0] if out else "node found")
    if npm:
        _, out = _check_cmd(npm.split(os.sep)[-1])
        detail.append(out.splitlines()[0] if out else "npm found")
    return ok, "; ".join(detail) if detail else "not found"


def _check_webview2():
    reg_exe = shutil.which("reg") or shutil.which("reg.exe")
    if not reg_exe:
        return False, "reg.exe not available; cannot verify (non-Windows?)"

    reg_paths = [
        r"HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients",
        r"HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients",
    ]
    for rp in reg_paths:
        try:
            subprocess.check_output(
                [reg_exe, "query", rp],
                stderr=subprocess.STDOUT,
                text=True,
            )
            return True, f"WebView2 runtime registry found ({rp})"
        except subprocess.CalledProcessError:
            continue

    candidates = [
        os.path.join(
            os.environ.get("ProgramFiles(x86)", ""),
            "Microsoft",
            "EdgeWebView",
            "Application",
        ),
        os.path.join(
            os.environ.get("ProgramFiles", ""),
            "Microsoft",
            "EdgeWebView",
            "Application",
        ),
    ]
    for path in candidates:
        if path.strip() and os.path.exists(path):
            return True, f"WebView2 runtime found at {path}"

    return (
        False,
        "WebView2 runtime not detected. Install: https://go.microsoft.com/fwlink/p/?LinkId=2124703",
    )


def _check_nuitka():
    nuitka = shutil.which("nuitka") or shutil.which("nuitka3")
    if not nuitka:
        return False, "nuitka not found in PATH"
    ok, out = _check_cmd(nuitka.split(os.sep)[-1])
    return ok, out.splitlines()[0] if out else "nuitka found"


def _status(ok: bool) -> str:
    return click.style(OK, fg="green") if ok else click.style(ERR, fg="red")


def _maybe_warn(cond: bool, msg: str):
    if cond:
        click.secho(f"{WARN} {msg}", fg="yellow")


@click.command()
def doctor():
    """Run environment checks for TauPy dev/build."""
    checks = [
        ("Python >=3.11",) + _check_python(),
        ("Rust toolchain (rustc/cargo)",) + _check_rust(),
        ("Node.js + npm",) + _check_node(),
        ("WebView2 runtime (Windows)",) + _check_webview2(),
        ("Nuitka",) + _check_nuitka(),
    ]

    click.secho("TauPy Doctor\n", fg="cyan", bold=True)
    for name, ok, detail in checks:
        click.echo(f"{_status(ok)} {name} - {detail}")

    _maybe_warn(
        not os.access(os.getcwd(), os.W_OK),
        "Current directory is not writable; builds may fail.",
    )
