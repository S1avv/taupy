from __future__ import annotations
import json
import asyncio
from typing import Set, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol
    from taupy.app import App

from .devui import DevUI


class TauServer:
    """
    Internal WebSocket server used by TauPy to synchronize UI events
    between the Python backend and the embedded WebView client.

    The server manages:
        • Client connections
        • Event dispatching (click, input)
        • State updates broadcast
        • Initial route navigation

    This class is not intended to be created manually - it is created
    automatically by `App`.
    """

    def __init__(self, app: "App") -> None:
        """
        Initialize the WebSocket server.

        Parameters:
            app (App): The parent TauPy application instance.
        """
        self.app = app
        self.clients: Set[WebSocketServerProtocol] = set()

    async def handler(self, websocket: "WebSocketServerProtocol") -> None:
        """
        Main connection handler for each client WebSocket.

        Manages:
            • Register client
            • Run connection init handlers
            • Navigate to the initial route
            • Process incoming events

        Parameters:
            websocket (WebSocketServerProtocol): Connected client instance.
        """
        self.clients.add(websocket)

        await self.app._run_connect_handlers()

        await self.init_navigation()

        DevUI.banner(self.app.title, self.app.http_port, dev=self.app.dev)

        try:
            async for message in websocket:
                data: Dict[str, Any] = json.loads(message)
                event_type = data.get("type")

                if event_type == "click":
                    await self.app.dispatcher.dispatch_click(data["id"])
                elif event_type == "input":
                    await self.app.dispatcher.dispatch_input(
                        data["id"], data.get("value", "")
                    )
                elif event_type == "window_cmd":
                    cmd = data.get("command") or data.get("payload") or {}
                    await self.app.send_window_command(cmd)
                elif event_type == "window_event":
                    await self.app._handle_window_event(
                        data.get("name"), data.get("payload", {})
                    )

        except Exception:
            raise

        finally:
            self.clients.discard(websocket)

    async def broadcast(self, msg: Dict[str, Any]) -> None:
        """
        Send a JSON message to all connected WebSocket clients.

        Used internally to update UI:
            • State change updates
            • Theme switching
            • DOM replacing (navigation)

        Parameters:
            msg (dict): JSON-serializable message.
        """
        if not self.clients:
            return

        text = json.dumps(msg)

        await asyncio.gather(
            *(ws.send(text) for ws in self.clients if ws.open), return_exceptions=True
        )

    async def init_navigation(self) -> None:
        """
        Navigate the client to the root route ("/") after connection.

        Called automatically on each new WebSocket connection.
        """
        from taupy.app import AppMode

        if getattr(self.app, "mode", AppMode.GENERATE_HTML) != AppMode.GENERATE_HTML:
            return
        await self.app.navigate("/")
