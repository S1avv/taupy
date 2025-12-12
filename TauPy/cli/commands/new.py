import os
import shutil
import click
import time
import threading
import itertools
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(BASE_DIR, "utils")
TEMPLATE_PY = os.path.join(UTILS_DIR, "template.py")
TEMPLATE_REACT = os.path.join(UTILS_DIR, "template_react.py")
DLL_FILE = os.path.join(UTILS_DIR, "WebView2Loader.dll")
CLIENTJS = os.path.join(UTILS_DIR, "client.js")
TAUPY_EXE = os.path.join(UTILS_DIR, "taupy.exe")
VITE_TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "vite-react")


def loading_animation(stop_flag):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while not stop_flag["stop"]:
        print(f"\rCreating project... {next(spinner)}", end="", flush=True)
        time.sleep(0.1)
    print("\r", end="")


def choose_frontend(default="python"):
    options = ["python", "react"]
    if not sys.stdin.isatty():
        return default

    try:
        import msvcrt
    except ImportError:
        return click.prompt(
            "Choose frontend template",
            type=click.Choice(options, case_sensitive=False),
            default=default,
            show_choices=True,
        ).lower()

    idx = 0 if default == "python" else 1
    header = "Choose frontend template (↑/↓ Enter):"

    def redraw():
        sys.stdout.write("\x1b[2K\r" + header + "\n")
        for i, opt in enumerate(options):
            marker = "●" if i == idx else "○"
            sys.stdout.write(f"\x1b[2K\r  {marker} {opt}\n")
        sys.stdout.write(f"\x1b[{len(options)+1}A")
        sys.stdout.flush()

    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

    try:
        redraw()
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                sys.stdout.write(f"\x1b[{len(options)+1}B\r\x1b[0K")
                sys.stdout.flush()
                return options[idx]
            if ch == "\xe0":
                key = msvcrt.getwch()
                if key == "H":
                    idx = (idx - 1) % len(options)
                    redraw()
                elif key == "P":
                    idx = (idx + 1) % len(options)
                    redraw()
    finally:
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()


@click.command()
@click.argument("name")
@click.option(
    "--frontend",
    "-f",
    type=click.Choice(["python", "react"], case_sensitive=False),
    default=None,
    help="Choose UI template: python (TauPy widgets) or react (Vite + React).",
)
def new(name, frontend):
    project_path = os.path.abspath(name)
    frontend = (frontend or "").lower()

    if os.path.exists(project_path):
        click.secho("Folder already exists. Choose another name.", fg="red")
        return

    if not frontend:
        frontend = choose_frontend(default="python")

    os.makedirs(project_path)
    launcher_dir = os.path.join(project_path, "launcher")
    os.makedirs(launcher_dir)

    dist_dir = os.path.join(project_path, "dist")
    os.makedirs(dist_dir)

    if not frontend:
        frontend = click.prompt(
            "Choose frontend template",
            type=click.Choice(["python", "react"], case_sensitive=False),
            default="python",
            show_choices=True,
        ).lower()

    template_file = TEMPLATE_REACT if frontend == "react" else TEMPLATE_PY
    try:
        shutil.copy(template_file, os.path.join(project_path, "main.py"))
    except FileNotFoundError:
        pass

    try:
        shutil.copy(DLL_FILE, os.path.join(launcher_dir, "WebView2Loader.dll"))
    except FileNotFoundError:
        pass

    try:
        shutil.copy(CLIENTJS, os.path.join(dist_dir, "client.js"))
    except FileNotFoundError:
        pass

    try:
        shutil.copy(TAUPY_EXE, os.path.join(launcher_dir, "taupy.exe"))
    except FileNotFoundError:
        pass

    if frontend == "react":
        try:
            if os.path.exists(VITE_TEMPLATE_DIR):
                shutil.copytree(VITE_TEMPLATE_DIR, project_path, dirs_exist_ok=True)
        except Exception as e:
            click.secho(f"Could not copy React template: {e}", fg="red")

    stop_flag = {"stop": False}
    thread = threading.Thread(target=loading_animation, args=(stop_flag,))
    thread.start()
    time.sleep(1.5)
    stop_flag["stop"] = True
    thread.join()

    click.secho("Project created successfully!", fg="green", bold=True)

    click.echo()
    click.secho("Next steps:", fg="cyan")
    click.secho(f"  cd {name}", fg="yellow")
    if frontend == "react":
        click.secho("  npm install", fg="yellow")
    click.secho("  taupy dev", fg="yellow")

    click.echo()
    click.secho("Happy coding with TauPy!", fg="magenta")
