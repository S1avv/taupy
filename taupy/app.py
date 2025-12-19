from __future__ import annotations

import signal
import json
import asyncio
import os
import sys
import subprocess
from typing import Any, Awaitable, Callable, Optional
from enum import Enum
from types import CellType

import websockets

from .dispatcher import Dispatcher
from .router import Router
from .widgets.component import Component
from .widgets.elements import Button_, Text_, Input_
from .state import State
from .server import TauServer

from .reloader import start_hot_reload, start_static_reload, free_port


class AppMode(Enum):
    GENERATE_HTML = "generate"
    RAW_HTML = "raw"


class App:
    """
    Core application controller for TauPy UI framework.

    The `App` class manages:
      • Rendering and saving the initial HTML layout
      • Running the WebSocket server
      • Injecting UI components
      • Navigating between routes
      • Launching the native window (Rust WebView wrapper)
      • Handling connect events and UI theme updates
    """

    def __init__(
        self,
        title: str,
        width: int,
        height: int,
        theme: str = "light",
        dev: bool = False,
        mode: AppMode = AppMode.GENERATE_HTML,
        http_port: int | None = None,
        external_http: bool | None = None,
        frameless: bool = False,
        transparent: bool = False,
        always_on_top: bool = False,
        resizable: bool = True,
        min_width: int | None = None,
        min_height: int | None = None,
        max_width: int | None = None,
        max_height: int | None = None,
    ) -> None:
        """
        Initialize the application.

        Parameters:
            title (str): Window title.
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            theme (str): DaisyUI theme name.
            mode (AppMode): GENERATE_HTML renders to dist/, RAW_HTML reuses existing dist/.
            frameless (bool): Remove native window frame (Rust launcher).
            transparent (bool): Make window background transparent (Rust launcher).
        """
        self.root_module_name = (
            sys.argv[0].replace(".py", "").replace("/", ".").replace("\\", ".")
        )
        self.root_module_path = sys.argv[0]

        dev_flag = True if "--dev" in sys.argv else False

        env_external_http = os.getenv("TAUPY_EXTERNAL_HTTP")
        if env_external_http is not None:
            external_http = env_external_http not in ("0", "false", "False")
        elif external_http is None:
            if mode == AppMode.RAW_HTML:
                external_http = dev_flag
            else:
                # In GENERATE_HTML mode we host dist ourselves even in dev.
                external_http = False

        env_http_port = os.getenv("TAUPY_HTTP_PORT")
        if env_http_port and env_http_port.isdigit():
            http_port = int(env_http_port)
        elif http_port is None:
            http_port = 5173 if external_http else 8000

        self.theme = theme
        self.title = title
        self.width = width
        self.height = height

        self.dispatcher = Dispatcher()
        self.router = Router()
        self.root_component: Optional[Component] = None
        self.mode = mode
        self.http_port = http_port
        self.external_http = external_http
        self.ws_port = 8765

        self.server = TauServer(self)
        self.connect_handlers: list[Callable[[], Awaitable[None] | None]] = []

        self.dev = dev_flag
        self.no_window = "--no-window" in sys.argv
        self.open_devtools = (
            "--open-devtools" in sys.argv or os.getenv("TAUPY_OPEN_DEVTOOLS") == "1"
        )
        self.frameless = frameless
        self.transparent = transparent
        self.always_on_top = always_on_top
        self.resizable = resizable
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

        self._shutting_down = False
        self.window_process: subprocess.Popen[str] | None = None
        self._reload_task: asyncio.Task[None] | None = None
        self._window_watch_task: asyncio.Task[None] | None = None
        self._window_event_handlers: list[
            Callable[[str, dict], Awaitable[None] | None]
        ] = []
        self._window_stdout_task: asyncio.Task[None] | None = None

    async def run(
        self, root_component: Optional[Component] = None, port: int = 8765
    ) -> None:
        """
        Start the TauPy backend and launch the native window.

        Steps performed:
            1. Render UI into /dist/index.html (optional when using prebuilt dist/)
            2. Start WebSocket backend
            3. Launch native window (Rust WebView)
            4. Run indefinitely

        Parameters:
            root_component (Component): Root UI container that holds all screens.
        """
        if self.mode == AppMode.GENERATE_HTML and root_component is None:
            raise ValueError(
                "root_component is required when mode=AppMode.GENERATE_HTML"
            )

        env_ws_port = os.getenv("TAUPY_WS_PORT")
        if env_ws_port and env_ws_port.isdigit():
            port = int(env_ws_port)
        self.ws_port = port

        self.root_component = root_component
        if self.mode == AppMode.GENERATE_HTML:
            self._render_and_save_html(root_component)  # type: ignore[arg-type]
        elif root_component:
            self._bind_events_and_states(root_component)

        try:
            await websockets.serve(self.server.handler, "localhost", port)
        except OSError as e:
            if e.errno == 10048:
                free_port(port)
                await websockets.serve(self.server.handler, "localhost", port)
            else:
                raise

        if not self.no_window:
            if not self.external_http:
                try:
                    free_port(self.http_port)
                except Exception:
                    pass
            self._launch_window_process()
            if self.window_process:
                self._window_watch_task = asyncio.create_task(self._watch_window_exit())
                self._window_stdout_task = asyncio.create_task(
                    self._consume_window_stdout()
                )

        if self.dev:
            if self.mode == AppMode.GENERATE_HTML:
                self._reload_task = asyncio.create_task(start_hot_reload(self))
            elif self.mode == AppMode.RAW_HTML:
                self._reload_task = asyncio.create_task(start_static_reload(self))

        loop = asyncio.get_running_loop()

        def sigint_handler(*_):
            asyncio.create_task(self.shutdown())

        try:
            loop.add_signal_handler(signal.SIGINT, sigint_handler)
        except Exception:
            signal.signal(
                signal.SIGINT,
                lambda *_: asyncio.run_coroutine_threadsafe(self.shutdown(), loop),
            )

        await asyncio.Future()

    def _render_and_save_html(self, component: Component) -> None:
        """
        Render the root component and embed it into the HTML template.

        Output directory:
            dist/index.html
            dist/public/

        Parameters:
            component (Component): UI element tree root.
        """
        rendered_body = component.render()

        template_path = os.path.join(
            os.path.dirname(__file__), "templates", "base.html"
        )

        with open(template_path, "r", encoding="utf-8") as tpl_file:
            template_html = tpl_file.read()

        full_html = template_html.format(
            title=self.title, theme=self.theme, body=rendered_body
        )

        os.makedirs("dist", exist_ok=True)
        os.makedirs("dist/public", exist_ok=True)

        with open("dist/index.html", "w", encoding="utf-8") as f:
            f.write(full_html)

        self._bind_events_and_states(component)

    def _bind_events_and_states(self, component: Component) -> None:
        """
        Recursively propagate the App reference, connect reactive State bindings,
        and attach input handlers.
        """

        from inspect import isfunction

        component.app = self

        if isinstance(component, Text_) and isfunction(component.value):
            func = component.value
            states: set[State] = set()

            closure: tuple[CellType, ...] = func.__closure__ or ()
            for cell in closure:
                val = cell.cell_contents
                if isinstance(val, State):
                    states.add(val)

            for name in func.__code__.co_names:
                if name in func.__globals__:
                    val = func.__globals__[name]
                    if isinstance(val, State):
                        states.add(val)

            for st in states:

                def _on_state_change(_v, cid=component.id, f=func):
                    self._update_text_component(cid, f())

                st.subscribe(_on_state_change)

        if isinstance(component, Button_):
            pass

        if isinstance(component, Input_):
            if component.on_input:
                self.dispatcher.on_input(component.id)(component.on_input)

        for child in component.children:
            self._bind_events_and_states(child)

    def _update_text_component(self, component_id: str, new_value: Any) -> None:
        """
        Send a WebSocket message updating a reactive <Text> component.

        Parameters:
            component_id (str): UI element ID.
            new_value (Any): Value to render inside the <Text>.
        """
        asyncio.create_task(
            self.server.broadcast(
                {"type": "update_text", "id": component_id, "value": str(new_value)}
            )
        )

    async def navigate(self, route: str) -> None:
        """
        Render a new screen and send it to all connected clients.

        Parameters:
            route (str): Route path string (e.g. "/settings").
        """
        handler = self.router.get(route)
        if not handler:
            return

        result = handler()
        if asyncio.iscoroutine(result):
            result = await result

        new_screen: Component = result

        if not self.root_component:
            raise RuntimeError("App has no root component to navigate from.")

        self.root_component.children = [new_screen]

        self._bind_events_and_states(new_screen)

        await self.server.broadcast(
            {
                "type": "replace",
                "id": self.root_component.id,
                "html": new_screen.render(),
            }
        )

    def on_connect(self, func: Callable[[], Awaitable[None] | None]):
        """
        Register a callback executed when a client establishes connection.

        Parameters:
            func (Callable): Sync or async function.

        Returns:
            Callable: The decorated function.
        """
        self.connect_handlers.append(func)
        return func

    def on_window_event(self, func: Callable[[str, dict], Awaitable[None] | None]):
        """
        Register a callback to react to native window events
        (close_request, focus, resize, etc).
        """
        self._window_event_handlers.append(func)
        return func

    async def _run_connect_handlers(self) -> None:
        """Execute all registered connect callbacks."""
        for handler in self.connect_handlers:
            result = handler()
            if asyncio.iscoroutine(result):
                await result

    async def set_theme(self, theme: str) -> None:
        """
        Broadcast a DaisyUI theme switch to all clients.

        Parameters:
            theme (str): Theme name.
        """
        await self.server.broadcast({"type": "set_theme", "theme": theme})

    def _launch_window_process(self) -> None:
        """
        Spawn the native Rust WebView window process.

        Expected executable location:
            launcher/taupy.exe
        """
        exe_path = os.path.join(os.getcwd(), "launcher", "taupy.exe")

        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Main launcher missing at: {exe_path}")

        args = [
            exe_path,
            f"--title={self.title}",
            f"--width={self.width}",
            f"--height={self.height}",
            f"--port={self.http_port}",
        ]

        if self.external_http:
            args.append("--external")
        if self.frameless:
            args.append("--frameless")
        if self.transparent:
            args.append("--transparent")
        if self.always_on_top:
            args.append("--always-on-top")
        if not self.resizable:
            args.append("--resizable=false")
        if self.open_devtools:
            args.append("--open-devtools")
        if self.min_width is not None:
            args.append(f"--min-width={self.min_width}")
        if self.min_height is not None:
            args.append(f"--min-height={self.min_height}")
        if self.max_width is not None:
            args.append(f"--max-width={self.max_width}")
        if self.max_height is not None:
            args.append(f"--max-height={self.max_height}")

        creation_flags = 0
        if os.name == "nt":
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        self.window_process = subprocess.Popen(
            args,
            creationflags=creation_flags,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    async def _watch_window_exit(self) -> None:
        """Shut down backend when the native window is closed."""
        if not self.window_process:
            return
        try:
            await asyncio.to_thread(self.window_process.wait)
        except Exception:
            return
        if not self._shutting_down:
            await self.shutdown()

    def route(self, path: str):
        """
        Decorator for registering a route handler.

        Example:
            @app.route("/")
            def home():
                return VStack(...)
        """

        def decorator(handler: Callable[..., Component | Awaitable[Component]]):
            self.router.register(path, handler)
            return handler

        return decorator

    async def hot_reload_broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.

        Parameters:
            message (str): Message string.
        """
        if self.dev:
            await self.server.broadcast({"type": "hot_reload", "message": message})

    async def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True

        if self._reload_task:
            self._reload_task.cancel()
            try:
                await self._reload_task
            except Exception:
                pass
        if (
            self._window_watch_task
            and self._window_watch_task is not asyncio.current_task()
        ):
            self._window_watch_task.cancel()
        if (
            self._window_stdout_task
            and self._window_stdout_task is not asyncio.current_task()
        ):
            self._window_stdout_task.cancel()

        try:
            await self.server.stop()
        except Exception:
            pass

        if self.window_process:
            try:
                self.window_process.terminate()
            except Exception:
                pass

            free_port(self.ws_port)

            try:
                self.window_process.wait(timeout=2)
            except Exception:
                self.window_process.kill()

        print("Stopped.")
        os._exit(0)

    async def update_component(self, component_id: str, new_html: str):
        await self.server.broadcast(
            {"type": "update_html", "id": component_id, "html": new_html}
        )

    async def send_window_command(self, command: dict):
        """
        Send a window command to the native launcher via the WebView IPC bridge.
        Supported commands (dict form):
            - {"type": "minimize"}
            - {"type": "maximize"}
            - {"type": "toggle_maximize"}
            - {"type": "restore"}
            - {"type": "center"}
            - {"type": "toggle_fullscreen"}
            - {"type": "set_size", "width": int, "height": int}
            - {"type": "set_position", "x": int, "y": int}
            - {"type": "set_title", "title": str}
            - {"type": "focus"}
            - {"type": "always_on_top", "enabled": bool}
            - {"type": "resizable", "enabled": bool}
            - {"type": "min_size", "width": int, "height": int}
            - {"type": "max_size", "width": int, "height": int}
            - {"type": "show_cursor", "visible": bool}
            - {"type": "start_drag"}
        """
        if self.window_process and self.window_process.stdin:
            try:
                self.window_process.stdin.write(json.dumps(command) + "\n")
                self.window_process.stdin.flush()
            except Exception:
                pass

        await self.server.broadcast({"type": "window_cmd", "command": command})

    async def _handle_window_event(self, name: str | None, payload: dict):
        if not name:
            return
        for handler in self._window_event_handlers:
            result = handler(name, payload)
            if asyncio.iscoroutine(result):
                await result

    async def _consume_window_stdout(self):
        """
        Read JSON lines from the launcher stdout and forward as window events.
        """
        if not self.window_process or not self.window_process.stdout:
            return
        reader = self.window_process.stdout
        try:
            while True:
                line = await asyncio.to_thread(reader.readline)
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    await self._handle_window_event(data.get("type"), data)
                except Exception:
                    continue
        except Exception:
            pass
