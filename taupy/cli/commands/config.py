import os
import click
import tomllib
from typing import Any


CONFIG_FILENAME = "taupy.toml"


def _load_config(cwd: str) -> dict:
    path = os.path.join(cwd, CONFIG_FILENAME)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except Exception as exc:
        click.secho(f"Could not read {CONFIG_FILENAME}: {exc}", fg="red")
        return {}


def _serialize_value(val: Any) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _emit_table(name: str, table: dict) -> list[str]:
    lines: list[str] = []
    header_written = False
    if name:
        lines.append(f"[{name}]")
        header_written = True

    for key, val in table.items():
        if isinstance(val, dict):
            continue
        lines.append(f"{key} = {_serialize_value(val)}")

    if header_written:
        lines.append("")

    for key, val in table.items():
        if isinstance(val, dict):
            child_name = f"{name}.{key}" if name else key
            lines.extend(_emit_table(child_name, val))

    return lines


def _dump_config(data: dict) -> str:
    lines: list[str] = []
    for key, val in data.items():
        if isinstance(val, dict):
            continue
        lines.append(f"{key} = {_serialize_value(val)}")
    if lines:
        lines.append("")

    for key, val in data.items():
        if isinstance(val, dict):
            lines.extend(_emit_table(key, val))
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def _traverse_get(data: dict, path: str):
    node: Any = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _traverse_set(data: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    node = data
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value


def _parse_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


@click.group()
def config():
    """Inspect or edit taupy.toml in the current directory."""


@config.command()
def show():
    """Print taupy.toml as-is."""
    cwd = os.getcwd()
    path = os.path.join(cwd, CONFIG_FILENAME)
    if not os.path.exists(path):
        click.secho(f"{CONFIG_FILENAME} not found in {cwd}", fg="red")
        return
    with open(path, "r", encoding="utf-8") as fh:
        click.echo(fh.read())


@config.command()
@click.argument("key")
def get(key):
    """Get a value by dotted path, e.g. build.onefile."""
    cfg = _load_config(os.getcwd())
    val = _traverse_get(cfg, key)
    if val is None:
        click.secho(f"Key '{key}' not found.", fg="red")
        return
    click.echo(val)


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a value by dotted path, e.g. dev.port 9000."""
    cwd = os.getcwd()
    cfg = _load_config(cwd)
    parsed_val = _parse_value(value)
    _traverse_set(cfg, key, parsed_val)
    content = _dump_config(cfg)
    path = os.path.join(cwd, CONFIG_FILENAME)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    click.secho(f"Updated {CONFIG_FILENAME}: {key} = {parsed_val}", fg="green")
