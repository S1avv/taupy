import os
import shutil
import click
import time
import threading
import itertools
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(BASE_DIR, "utils")
TEMPLATE_REACT = os.path.join(UTILS_DIR, "template_react.py")
TEMPLATE_VANILLA = os.path.join(UTILS_DIR, "template_vanilla.py")
TEMPLATE_PYTHON = os.path.join(UTILS_DIR, "template.py")
VITE_TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "vite-react")
VANILLA_TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "vanilla")


def loading_animation(stop_flag):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while not stop_flag["stop"]:
        print(f"\rCreating project... {next(spinner)}", end="", flush=True)
        time.sleep(0.1)
    print("\r", end="")


def choose_frontend(default="react"):
    options = [
        {"value": "react", "label": "react (recommended)"},
        {"value": "vanilla", "label": "vanilla"},
        {"value": "python", "label": "python"},
    ]
    if not sys.stdin.isatty():
        return default

    try:
        import msvcrt
    except ImportError:
        values = [opt["value"] for opt in options]
        return click.prompt(
            "Choose frontend template [react is recommended]",
            type=click.Choice(values, case_sensitive=False),
            default=default,
            show_choices=True,
        ).lower()

    values = [opt["value"] for opt in options]
    try:
        idx = values.index(default)
    except ValueError:
        idx = 0
    header = "Choose frontend template (Up/Down + Enter):"

    def redraw():
        sys.stdout.write("\x1b[2K\r" + header + "\n")
        for i, opt in enumerate(options):
            marker = ">" if i == idx else " "
            sys.stdout.write(f"\x1b[2K\r  {marker} {opt['label']}\n")
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
                return options[idx]["value"]
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


def _prompt_value(message: str, default, value_type=str):
    if sys.stdin.isatty():
        return click.prompt(
            message, default=default, type=value_type, show_default=True
        )
    return default


def _prompt_bool(message: str, default: bool) -> bool:
    if sys.stdin.isatty():
        return click.confirm(message, default=default)
    return default


def _collect_config(frontend_choice: str) -> dict:
    frontend_default = frontend_choice or "react"
    click.secho("\n=== TauPy dev setup ===", fg="cyan", bold=True)
    click.echo(f"Frontend template: {frontend_default}")

    click.secho("\n[Dev server]", fg="cyan")
    click.echo("  Port for TauPy backend or your external dev server.")
    dev_port = _prompt_value("Dev HTTP port", 8000, int)

    click.secho("\n[Hot reload]", fg="cyan")
    click.echo('  Live reload transport (default "ws").')
    hot_reload = str(_prompt_value("Hot reload mode", "ws", str)).strip() or "ws"

    click.secho("\n[Frontend]", fg="cyan")
    click.echo(f"  Using frontend template: {frontend_default}")
    frontend_type = frontend_default.lower()

    click.secho("\n[External HTTP]", fg="cyan")
    click.echo("  URL of the dev server used by the frontend (Vite, etc).")
    external_http_default = "http://localhost:5173"
    external_http = str(
        _prompt_value("External frontend URL", external_http_default, str)
    )

    click.secho("\n[Build]", fg="cyan")
    click.echo("  Backend bundling preferences for production.")
    onefile = _prompt_bool("Bundle backend as single executable (onefile)?", False)
    strip_bin = _prompt_bool("Strip binaries after build?", True)

    return {
        "dev_port": dev_port,
        "hot_reload": hot_reload,
        "frontend_type": frontend_type,
        "external_http": external_http,
        "onefile": onefile,
        "strip": strip_bin,
    }


def _write_taupy_config(project_path: str, cfg: dict) -> None:
    cfg_path = os.path.join(project_path, "taupy.toml")
    content = (
        "[dev]\n"
        f"port = {cfg['dev_port']}\n"
        f'hot_reload = "{cfg["hot_reload"]}"\n'
        "\n"
        "[frontend]\n"
        f'type = "{cfg["frontend_type"]}"\n'
        f'external_http = "{cfg["external_http"]}"\n'
        "\n"
        "[build]\n"
        f"onefile = {str(cfg['onefile']).lower()}\n"
        f"strip = {str(cfg['strip']).lower()}\n"
    )
    with open(cfg_path, "w", encoding="utf-8") as fh:
        fh.write(content)


@click.command()
@click.argument("name")
@click.option(
    "--frontend",
    "-f",
    type=click.Choice(["react", "vanilla", "python"], case_sensitive=False),
    default=None,
    help="Choose UI template: react (Vite), vanilla (HTML/CSS/JS), or python (TauPy components).",
)
def new(name, frontend):
    project_path = os.path.abspath(name)
    frontend = (frontend or "").lower()

    if os.path.exists(project_path):
        click.secho("Folder already exists. Choose another name.", fg="red")
        return

    if not frontend:
        frontend = choose_frontend(default="react")

    config_answers = _collect_config(frontend)
    frontend = config_answers["frontend_type"]

    os.makedirs(project_path)

    if not frontend:
        frontend = click.prompt(
            "Choose frontend template [react is recommended]",
            type=click.Choice(["react", "vanilla", "python"], case_sensitive=False),
            default="react",
            show_choices=True,
        ).lower()

    if frontend == "react":
        template_file = TEMPLATE_REACT
    elif frontend == "vanilla":
        template_file = TEMPLATE_VANILLA
    else:
        template_file = TEMPLATE_PYTHON
    try:
        shutil.copy(template_file, os.path.join(project_path, "main.py"))
    except FileNotFoundError:
        pass

    if frontend == "react":
        try:
            if os.path.exists(VITE_TEMPLATE_DIR):
                shutil.copytree(VITE_TEMPLATE_DIR, project_path, dirs_exist_ok=True)
        except Exception as e:
            click.secho(f"Could not copy React template: {e}", fg="red")
    elif frontend == "vanilla":
        try:
            if os.path.exists(VANILLA_TEMPLATE_DIR):
                shutil.copytree(VANILLA_TEMPLATE_DIR, project_path, dirs_exist_ok=True)
        except Exception as e:
            click.secho(f"Could not copy Vanilla template: {e}", fg="red")

    _write_taupy_config(project_path, config_answers)

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
    click.secho("  taupy run", fg="yellow")
    if frontend == "python":
        click.echo()
        click.secho("  UI is built with Python components (VStack, Text, Button, etc.)", fg="cyan")
        click.secho("  No npm or frontend build needed!", fg="cyan")

    click.echo()
    click.secho("Happy coding with TauPy!", fg="magenta")
