import os
import shutil
import subprocess
import sys
import click
from typing import Optional

ICON_INFO = "ℹ"
ICON_OK = "✔"
ICON_WARN = "⚠"
ICON_ERR = "✖"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(BASE_DIR, "utils")
WINDOW_DIR = os.path.join(BASE_DIR, "window")
WINDOW_TARGET_DIR = os.path.join(WINDOW_DIR, "target", "release")
DLL_FILE = os.path.join(UTILS_DIR, "WebView2Loader.dll")
TAUPY_EXE = os.path.join(UTILS_DIR, "taupy.exe")


def _copy_if_exists(src: str, dst_dir: str) -> None:
    if not os.path.exists(src):
        click.secho(f"Missing artifact: {src}", fg="red")
        return
    shutil.copy(src, os.path.join(dst_dir, os.path.basename(src)))


def _detect_frontend_dir(cwd: str) -> Optional[str]:
    candidates = [
        os.path.join(cwd, "package.json"),
        os.path.join(cwd, "vite-project", "package.json"),
        os.path.join(cwd, "fr", "package.json"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return os.path.dirname(candidate)
    return None


@click.command()
def build():
    """
    Build TauPy app into ./target:
    - bundles Python backend via Nuitka (onefile)
    - builds React frontend (if present) into dist/
    - copies WebView2 loader and taupy.exe runtime
    - builds Rust launcher automatically (cargo build --release)
    """
    cwd = os.getcwd()
    target_dir = os.path.join(cwd, "target")
    launcher_dir = os.path.join(target_dir, "launcher")
    onefile_build_dir = os.path.join(target_dir, "main.onefile-build")
    frontend_dir = _detect_frontend_dir(cwd)
    main_py = os.path.join(cwd, "main.py")

    if not os.path.exists(main_py):
        click.secho(f"{ICON_ERR} main.py not found in {cwd}. Run from your project root.", fg="red")
        sys.exit(1)

    click.secho(f"{ICON_INFO} Preparing build output...", fg="cyan")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(launcher_dir, exist_ok=True)
    if os.path.exists(onefile_build_dir):
        shutil.rmtree(onefile_build_dir, ignore_errors=True)

    click.secho(f"{ICON_INFO} Using prebuilt Rust launcher (no cargo build)...", fg="cyan")
    click.secho(f"{ICON_INFO} Copying WebView2 loader and runtime into launcher/...", fg="cyan")
    dll_candidates = [
        os.path.join(cwd, "launcher", "WebView2Loader.dll"),
        DLL_FILE,
    ]
    exe_candidates = [
        os.path.join(cwd, "launcher", "taupy.exe"),
        TAUPY_EXE,
    ]
    for cand in dll_candidates:
        if os.path.exists(cand):
            _copy_if_exists(cand, launcher_dir)
            break
    for cand in exe_candidates:
        if os.path.exists(cand):
            _copy_if_exists(cand, launcher_dir)
            break

    if frontend_dir:
        npm_bin = shutil.which("npm") or shutil.which("npm.cmd")
        if npm_bin:
            click.secho(f"{ICON_INFO} Building React frontend...", fg="cyan")
            try:
                subprocess.check_call([npm_bin, "run", "build"], cwd=frontend_dir)
                dist_src = os.path.join(frontend_dir, "dist")
                dist_dst = os.path.join(target_dir, "dist")
                if os.path.exists(dist_src):
                    shutil.copytree(dist_src, dist_dst, dirs_exist_ok=True)
            except subprocess.CalledProcessError as exc:
                click.secho(f"{ICON_ERR} npm build failed ({exc.returncode}).", fg="red")
        else:
            click.secho(f"{ICON_WARN} npm not found; skipping frontend build.", fg="yellow")
    else:
        click.secho(f"{ICON_WARN} No frontend detected; skipping React build.", fg="yellow")

    try:
        import websockets  # noqa: F401
    except ImportError:
        click.secho(f"{ICON_ERR} Missing dependency 'websockets'. Install it before building (pip install websockets).", fg="red")
        sys.exit(1)

    nuitka_bin = shutil.which("nuitka") or shutil.which("nuitka3")
    if not nuitka_bin:
        click.secho(f"{ICON_ERR} Nuitka not found. Install with `pip install nuitka` to bundle backend.", fg="red")
        sys.exit(1)

    click.secho(f"{ICON_INFO} Bundling Python backend with Nuitka...", fg="cyan")
    jobs = max(1, min(os.cpu_count() or 1, 8))
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        f"--output-dir={target_dir}",
        "--output-filename=app.exe",
        "--include-package=websockets",
        "--include-package=websockets.legacy",
        "--include-module=websockets.legacy",
        "--include-module=websockets.legacy.client",
        "--include-module=websockets.legacy.server",
        "--include-package=TauPy",
        f"--jobs={jobs}",
        main_py,
    ]
    if sys.platform == "win32":
        cmd.extend([
            "--windows-console-mode=disable",
        ])
    try:
        subprocess.check_call(cmd)

        if os.path.exists(onefile_build_dir):
            shutil.rmtree(onefile_build_dir, ignore_errors=True)
    except subprocess.CalledProcessError as exc:
        click.secho(f"{ICON_ERR} Nuitka build failed ({exc.returncode}).", fg="red")
        sys.exit(exc.returncode)

    for suffix in (".build", ".dist", ".onefile-build", ".onefile-dist"):
        maybe_dir = os.path.splitext(main_py)[0] + suffix
        if os.path.exists(maybe_dir):
            shutil.rmtree(maybe_dir, ignore_errors=True)

    click.secho(f"{ICON_OK} Done. Artifacts are in: {target_dir}", fg="green", bold=True)
