import requests
from packaging import version

def check_for_updates():
    try:
        local = importlib.metadata.version("TauPy")

        r = requests.get(
            "https://api.github.com/repos/S1avv/taupy/releases/latest",
            timeout=3
        )
        latest = r.json()["tag_name"]

        if version.parse(latest) > version.parse(local):
            click.secho(
                f"⚠ TauPy {latest} is available! You have {local}.",
                fg="yellow"
            )
            click.secho("Update with:", fg="cyan")
            click.secho("    pip install --upgrade taupy", fg="green")
        else:
            click.secho("✔ TauPy is up to date.", fg="green")

    except Exception:
        pass
