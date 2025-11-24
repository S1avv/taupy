import time
import asyncio
import os
import sys
import traceback
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


async def start_hot_reload(app) -> None:
    """
    Watches for file changes, sends hot-reload events and restarts process.

    Works automatically. No dev-runner required.
    """
    global _last_reload

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

        print("[HMR] Broadcasting reload event...")

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

        print("[HMR] Restarting process...")

        args = sys.argv[:]
        if "--dev" not in args:
            args.append("--dev")
        if "--no-window" not in args:
            args.append("--no-window")

        os.execv(sys.executable, [sys.executable] + args)
