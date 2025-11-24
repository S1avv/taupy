from __future__ import annotations

import signal
import asyncio
import os
import pathlib
import sys
import subprocess
from typing import Any, Awaitable, Callable, Optional

import websockets

from .dispatcher import Dispatcher
from .devui import DevUI
from .router import Router
from .widgets.component import Component
from .widgets.elements import Button_, Text_, Input_
from .events.events import Resize
from .state import State
from .server import TauServer

from .reloader import start_hot_reload

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

    def __init__(self, title: str, width: int, height: int, theme: str = "light", dev: bool = False) -> None:
        """
        Initialize the application.

        Parameters:
            title (str): Window title.
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            theme (str): DaisyUI theme name.
        """
        self.root_module_name = sys.argv[0].replace(".py", "").replace("/", ".").replace("\\", ".")
        self.root_module_path = sys.argv[0]

        self.theme = theme
        self.title = title
        self.width = width
        self.height = height

        self.dispatcher = Dispatcher()
        self.router = Router()
        self.root_component: Optional[Component] = None

        self.server = TauServer(self)
        self.connect_handlers: list[Callable[[], Awaitable[None] | None]] = []

        self.dev = True if "--dev" in sys.argv else False
        self.no_window = "--no-window" in sys.argv

        self._shutting_down = False
        self.window_process = None
        self._reload_task = None

    async def run(self, root_component: Component, port: int = 8765) -> None:
        """
        Start the TauPy backend and launch the native window.

        Steps performed:
            1. Render UI into /dist/index.html
            2. Start WebSocket backend
            3. Launch native window (Rust WebView)
            4. Run indefinitely

        Parameters:
            root_component (Component): Root UI container that holds all screens.
        """
        self.root_component = root_component
        self._render_and_save_html(root_component)
        
        await websockets.serve(self.server.handler, "localhost", port)
        
        if not self.no_window:
            self._launch_window_process()

        if self.dev:
            DevUI.banner(self.title, 8000)
            self._reload_task = asyncio.create_task(start_hot_reload(self))

        loop = asyncio.get_running_loop()

        def sigint_handler(*_):
            asyncio.create_task(self.shutdown())

        try:
            loop.add_signal_handler(signal.SIGINT, sigint_handler)
        except:
            signal.signal(signal.SIGINT, lambda *_: asyncio.run_coroutine_threadsafe(self.shutdown(), loop))

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
        Recursively attach event handlers and state subscriptions
        to all components in the UI tree.
        """

        from inspect import isfunction

        if isinstance(component, Text_) and isfunction(component.value):
            func = component.value
            states: set[State] = set()

            closure = func.__closure__ or []
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
                st.subscribe(
                    lambda _v, cid=component.id, f=func: self._update_text_component(
                        cid, f()
                    )
                )

        if isinstance(component, Button_):
            if component.on_click:
                self.dispatcher.on_click(component.id)(component.on_click)

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

        if self.root_component:
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

        subprocess.Popen(
            [
                exe_path,
                f"--title={self.title}",
                f"--width={self.width}",
                f"--height={self.height}",
                "--port=8000",
            ]
        )

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

        print("\n[HMR] Shutting down...")

        if self._reload_task:
            self._reload_task.cancel()
            try:
                await self._reload_task
            except:
                pass

        try:
            await self.server.stop()
        except:
            pass

        if self.window_process:
            try:
                self.window_process.terminate()
            except:
                pass

            try:
                self.window_process.wait(timeout=2)
            except:
                self.window_process.kill()

        print("[HMR] Stopped.")
        os._exit(0)