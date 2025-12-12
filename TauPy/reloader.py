import time
import asyncio
import importlib
import traceback
import platform
import os
import sys
import subprocess
from watchfiles import awatch, DefaultFilter


class TauFilter(DefaultFilter):
    def __call__(self, change, path: str) -> bool:
        p = path.replace("\\", "/")

        if p.startswith("dist/") or "/dist/" in p:
            return False
        if p.startswith("launcher/") or "/launcher/" in p:
            return False

        return super().__call__(change, path)


_last_reload = 0

def clear_console():
    """
    Clear the console if we are attached to one.

    In GUI builds on Windows there is no attached console; calling `cls`
    would spawn a transient `cmd.exe` window. We skip clearing in that case.
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
                    f'netstat -ano | findstr :{port}',
                    shell=True, encoding="utf-8", errors="ignore"
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

    async for changes in awatch(".", watch_filter=TauFilter()):
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
            await app.server.broadcast({
                "type": "hmr_error",
                "message": err
            })
            continue

        await app.hot_reload_broadcast("hot_reload")

        try:
            await app.server.stop()
        except:
            pass

        if app.window_process:
            try:
                app.window_process.terminate()
            except:
                pass

        print("[HMR] Soft restarting...")

        module = importlib.import_module(app.root_module_name)
        importlib.reload(module)

        if hasattr(module, "main"):
            asyncio.create_task(module.main())
        else:
            print(f"[HMR] ERROR: main() not found in {app.root_module_name}")
