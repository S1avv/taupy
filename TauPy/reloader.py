import time
import asyncio
import os
import sys
import traceback
from watchfiles import awatch, DefaultFilter


class TauFilter(DefaultFilter):
    def __call__(self, change, path: str) -> bool:
        p = path.replace("\\", "/")

        if "/launcher/" in p or p.startswith("launcher/"):
            return False
        if "/dist/" in p or p.startswith("dist/"):
            return False

        return super().__call__(change, path)


_last_reload = 0


async def start_hot_reload(app) -> None:
    global _last_reload

    await asyncio.sleep(0.5)

    async for changes in awatch(".", watch_filter=TauFilter()):
        now = time.time()
        if now - _last_reload < 0.3:
            continue

        _last_reload = now
        print("[HMR] Changes detected:", changes)

        await asyncio.sleep(0.05)

        try:
            import py_compile
            py_compile.compile(app.root_module_path, doraise=True)

        except Exception as e:
            err = "".join(traceback.format_exception(e))
            print("[HMR] Syntax error detected:\n", err)

            await app.server.broadcast({
                "type": "hmr_error",
                "message": err
            })

            continue

        print("[HMR] Restarting server...")

        args = sys.argv[:]

        if "--dev" not in args:
            args.append("--dev")
        if "--no-window" not in args:
            args.append("--no-window")

        await asyncio.sleep(0.2)

        os.execv(sys.executable, [sys.executable] + args)
