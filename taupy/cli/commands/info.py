import os
import sys
import platform
import importlib.metadata
import click
import tomllib
from pathlib import Path
from typing import Optional


def _load_config(cwd: str) -> dict:
    cfg_path = os.path.join(cwd, "taupy.toml")
    if not os.path.exists(cfg_path):
        return {}
    try:
        with open(cfg_path, "rb") as fh:
            return tomllib.load(fh)
    except Exception:
        return {}


def _detect_webview2_version() -> Optional[str]:
    candidates = [
        Path(os.environ.get("ProgramFiles(x86)", ""))
        / "Microsoft"
        / "EdgeWebView"
        / "Application",
        Path(os.environ.get("ProgramFiles", ""))
        / "Microsoft"
        / "EdgeWebView"
        / "Application",
    ]
    versions = []
    for base in candidates:
        if base.exists():
            for entry in base.iterdir():
                if entry.is_dir() and any(ch.isdigit() for ch in entry.name):
                    versions.append(entry.name)
    if versions:
        return max(versions)
    return None


def _detect_frontend(cwd: str, cfg: dict) -> str:
    frontend_cfg = cfg.get("frontend", {}) if isinstance(cfg, dict) else {}
    f_type = frontend_cfg.get("type")
    external = frontend_cfg.get("external_http") or frontend_cfg.get("external-http")

    pkg_paths = [
        Path(cwd) / "package.json",
        Path(cwd) / "vite-project" / "package.json",
        Path(cwd) / "fr" / "package.json",
    ]
    has_pkg = any(p.exists() for p in pkg_paths)

    if f_type:
        base = f_type
    elif has_pkg:
        base = "react"
    else:
        base = "python"

    suffix = " (external)" if external or has_pkg else ""
    return f"{base.capitalize()}{suffix}"


def _detect_engine(cwd: str) -> str:
    exe = Path(cwd) / "Engine" / "taupy.exe"
    return "rust/release" if exe.exists() else "missing"


@click.command()
def info():
    """Show TauPy environment info (for diagnostics)."""
    cwd = os.getcwd()
    cfg = _load_config(cwd)

    try:
        taupy_ver = importlib.metadata.version("taupy-framework")
    except importlib.metadata.PackageNotFoundError:
        taupy_ver = "unknown"

    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    os_str = f"{platform.system()} {platform.release()}"
    webview_ver = _detect_webview2_version() or "not detected"
    frontend = _detect_frontend(cwd, cfg)
    engine = _detect_engine(cwd)

    click.echo(f"TauPy v{taupy_ver}")
    click.echo(f"Python {py_ver}")
    click.echo(f"OS: {os_str}")
    click.echo(f"WebView: WebView2 {webview_ver}")
    click.echo(f"Frontend: {frontend}")
    click.echo(f"Lake Engine: {engine}")
