import click
import subprocess
import os
import time
import shutil
from taupy.reloader import free_port


@click.command()
def dev():
    """
    Start TauPy backend alongside the Vite dev server (if present).
    """
    cwd = os.getcwd()
    root_pkg = os.path.join(cwd, "package.json")
    nested_pkg = os.path.join(cwd, "vite-project", "package.json")

    if os.path.exists(root_pkg):
        frontend_dir = cwd
    elif os.path.exists(nested_pkg):
        frontend_dir = os.path.join(cwd, "vite-project")
    else:
        frontend_dir = None

    npm_proc = None

    dev_port = os.environ.get("TAUPY_HTTP_PORT", "5173")
    has_frontend = frontend_dir is not None

    try:
        env = os.environ.copy()

        if has_frontend:
            npm_bin = shutil.which("npm") or shutil.which("npm.cmd")
            if not npm_bin:
                click.secho(
                    "npm не найден в PATH, пропускаю запуск фронтенда", fg="yellow"
                )
            else:
                try:
                    free_port(int(dev_port))
                except Exception:
                    pass
                npm_cmd = [npm_bin, "run", "dev", "--", "--host", "--port", dev_port]
                npm_proc = subprocess.Popen(npm_cmd, cwd=frontend_dir)
                env["TAUPY_EXTERNAL_HTTP"] = "1"
                env["TAUPY_HTTP_PORT"] = dev_port
                time.sleep(2)

        subprocess.run(["python", "main.py", "--dev"], env=env)
    finally:
        if npm_proc and npm_proc.poll() is None:
            npm_proc.terminate()
