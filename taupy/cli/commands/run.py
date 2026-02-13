import click
import os
import runpy
import sys
import time
import shutil
import tomllib
from urllib.parse import urlparse

import subprocess


@click.command()
def run():
    """
    Start TauPy app in production mode.

    This command runs main.py directly without development mode flags.
    """
    cwd = os.getcwd()
    main_py = os.path.join(cwd, "main.py")

    if not os.path.exists(main_py):
        click.secho(
            f"main.py not found in {cwd}. Run from your project root.",
            fg="red",
        )
        sys.exit(1)

    no_window = False
    if sys.platform == "win32":
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        launcher_override = os.getenv("TAUPY_LAUNCHER_PATH")
        if launcher_override:
            launcher_path = launcher_override
        else:
            launcher_path = os.path.join(base_dir, "utils", "taupy.exe")
        if not os.path.exists(launcher_path):
            click.secho(
                "Lake Engine runtime missing, starting backend server without desktop window.",
                fg="yellow",
            )
            no_window = True

    frontend_dir = None
    root_pkg = os.path.join(cwd, "package.json")
    nested_pkg = os.path.join(cwd, "vite-project", "package.json")
    if os.path.exists(root_pkg):
        frontend_dir = cwd
    elif os.path.exists(nested_pkg):
        frontend_dir = os.path.join(cwd, "vite-project")

    npm_proc = None

    if frontend_dir:
        vite_port: str | None = None

        env_http_port = os.environ.get("TAUPY_HTTP_PORT")
        if env_http_port and env_http_port.isdigit():
            vite_port = env_http_port
        else:
            cfg_path = os.path.join(cwd, "taupy.toml")
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, "rb") as fh:
                        cfg = tomllib.load(fh)
                except Exception:
                    cfg = {}
                frontend_cfg = cfg.get("frontend", {}) if isinstance(cfg, dict) else {}
                external_http = (
                    frontend_cfg.get("external_http")
                    if isinstance(frontend_cfg, dict)
                    else None
                )
                if isinstance(external_http, str) and external_http:
                    parsed = urlparse(external_http)
                    if parsed.port:
                        vite_port = str(parsed.port)
                if not vite_port:
                    dev_cfg = cfg.get("dev", {}) if isinstance(cfg, dict) else {}
                    dev_port = dev_cfg.get("port") if isinstance(dev_cfg, dict) else None
                    if isinstance(dev_port, int):
                        vite_port = str(dev_port)

        if not vite_port:
            vite_port = "5173"

        npm_bin = shutil.which("npm") or shutil.which("npm.cmd")
        if not npm_bin:
            click.secho(
                "npm not found in PATH, skipping frontend dev server.", fg="yellow"
            )
        else:
            try:
                from taupy.reloader import free_port

                free_port(int(vite_port))
            except Exception:
                pass

            npm_cmd = [npm_bin, "run", "dev", "--", "--host", "--port", vite_port]
            npm_proc = subprocess.Popen(npm_cmd, cwd=frontend_dir)
            os.environ["TAUPY_EXTERNAL_HTTP"] = "1"
            os.environ["TAUPY_HTTP_PORT"] = vite_port
            time.sleep(2)

    click.secho(f"Running main.py in {cwd}", fg="green")
    argv_backup = sys.argv[:]
    new_argv = [main_py]
    if no_window:
        new_argv.append("--no-window")
    sys.argv = new_argv
    try:
        runpy.run_path(main_py, run_name="__main__")
    except SystemExit as exc:
        sys.exit(exc.code)
    finally:
        sys.argv = argv_backup
        if npm_proc and npm_proc.poll() is None:
            npm_proc.terminate()
