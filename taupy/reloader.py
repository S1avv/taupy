import time
import asyncio
import importlib
import traceback
import platform
import os
import sys
import subprocess
from typing import Callable, Dict, Iterable, List, Optional, Tuple


class TauFilter:
    def __call__(self, change, path: str) -> bool:
        p = path.replace("\\", "/")

        if p.startswith("dist/") or "/dist/" in p:
            return False
        if p.startswith("Engine/") or "/Engine/" in p:
            return False

        return True


_last_reload: float = 0.0


def clear_console():
    """
    Clear the console if we are attached to one.
    """
    stdout_attached = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    stderr_attached = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    if not (stdout_attached or stderr_attached):
        return

    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def free_port(port: int):
    try:
        if sys.platform.startswith("win"):
            try:
                result = subprocess.check_output(
                    f"netstat -ano | findstr :{port}",
                    shell=True,
                    encoding="utf-8",
                    errors="ignore",
                )
            except subprocess.CalledProcessError as cpe:
                if cpe.returncode == 1:
                    return
                raise
            self_pid = str(os.getpid())

            for line in result.splitlines():
                parts = line.split()
                if not parts:
                    continue
                pid = parts[-1]
                if not pid.isdigit() or pid == "0":
                    continue
                if pid == self_pid:
                    continue
                print(f"[HMR] Killing process on port {port}, PID={pid}")
                subprocess.call(f"taskkill /PID {pid} /F", shell=True)

        else:
            subprocess.call(f"fuser -k {port}/tcp", shell=True)

    except Exception as e:
        print("[HMR] Could not free port:", e)


async def start_hot_reload(app) -> None:
    """
    Watches for file changes and restarts the Python module
    """
    global _last_reload

    print("[HMR] Enabled (soft reload mode)")

    await asyncio.sleep(0.4)

    async for changes in _poll_changes(".", TauFilter()):
        now = time.time()
        if now - _last_reload < 0.4:
            continue

        _last_reload = now
        print("[HMR] Changes detected:", changes)

        await asyncio.sleep(0.05)

        try:
            import py_compile

            py_compile.compile(app.root_module_path, doraise=True)
        except Exception as e:
            err = "".join(traceback.format_exception(e))
            print("[HMR] Syntax error:\n", err)
            await app.server.broadcast({"type": "hmr_error", "message": err})
            continue

        await app.hot_reload_broadcast("hot_reload")

        try:
            await app.server.stop()
        except Exception:
            pass

        if app.window_process:
            try:
                app.window_process.terminate()
            except Exception:
                pass

            print("[HMR] Soft restarting...")

            module = importlib.import_module(app.root_module_name)
            importlib.reload(module)

            if hasattr(module, "main"):
                asyncio.create_task(module.main())
            else:
                print(f"[HMR] ERROR: main() not found in {app.root_module_name}")


async def start_static_reload(app, watch_dir: str = "dist") -> None:
    """
    Watches the static dist folder and triggers a page reload on change.
    Intended for RAW_HTML mode projects (vanilla).
    """
    global _last_reload

    print(f"[HMR] Watching {watch_dir} for static changes")

    await asyncio.sleep(0.4)

    async for changes in _poll_changes(watch_dir, None):
        now = time.time()
        if now - _last_reload < 0.3:
            continue
        _last_reload = now
        print("[HMR] Static changes detected:", changes)
        await app.hot_reload_broadcast("hot_reload")


async def _poll_changes(
    root: str, watch_filter: Optional[Callable[[str, str], bool]] = None
) -> Iterable[List[Tuple[str, str]]]:
    """
    Lightweight polling-based file watcher implemented with stdlib only.
    Yields lists of (change_kind, path) tuples.
    """
    snapshot: Dict[str, float] = {}

    def should_watch(path: str) -> bool:
        if watch_filter is None:
            return True
        return bool(watch_filter("modified", path))

    while True:
        changes: List[Tuple[str, str]] = []

        current: Dict[str, float] = {}
        for dirpath, dirnames, filenames in os.walk(root):
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace("\\", "/")
                if not should_watch(rel):
                    continue
                try:
                    mtime = os.path.getmtime(full)
                except OSError:
                    continue
                current[rel] = mtime
                old_mtime = snapshot.get(rel)
                if old_mtime is None:
                    changes.append(("created", rel))
                elif mtime > old_mtime:
                    changes.append(("modified", rel))

        for path in snapshot:
            if path not in current:
                if should_watch(path):
                    changes.append(("deleted", path))

        snapshot = current

        if changes:
            yield changes

        await asyncio.sleep(0.4)
