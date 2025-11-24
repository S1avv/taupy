import os
import shutil
import click
import time
import threading
import itertools

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIST_DIR = os.path.join(BASE_DIR, "dist")
UTILS_DIR = os.path.join(BASE_DIR, "utils")
TEMPLATE_FILE = os.path.join(UTILS_DIR, "template.py")
DLL_FILE = os.path.join(UTILS_DIR, "WebView2Loader.dll")
CLIENTJS = os.path.join(UTILS_DIR, "client.js")
TAUPY_EXE = os.path.join(UTILS_DIR, "taupy.exe")

def loading_animation(stop_flag):
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_flag["stop"]:
        print(f"\rCreating project... {next(spinner)}", end="", flush=True)
        time.sleep(0.1)
    print("\r", end="")


@click.command()
@click.argument("name")
def new(name):

    project_path = os.path.abspath(name)

    if os.path.exists(project_path):
        click.secho("✖ Folder already exists. Choose another name.", fg="red")
        return

    stop_flag = {"stop": False}
    thread = threading.Thread(target=loading_animation, args=(stop_flag,))
    thread.start()

    time.sleep(0.5)

    os.makedirs(project_path)
    launcher_dir = os.path.join(project_path, "launcher")
    os.makedirs(launcher_dir)

    dist_dir = os.path.join(project_path, "dist")
    os.makedirs(dist_dir)

    try:
        shutil.copy(TEMPLATE_FILE, os.path.join(project_path, "main.py"))
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

    time.sleep(6)

    stop_flag["stop"] = True
    thread.join()

    click.secho("✔ Project created successfully!", fg="green", bold=True)

    click.echo()
    click.secho("Next steps:", fg="cyan")
    click.secho(f"  cd {name}", fg="yellow")
    click.secho("  taupy dev", fg="yellow")

    click.echo()
    click.secho("Happy coding with TauPy! ✨", fg="magenta")
