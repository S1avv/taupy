from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional
from .events.events import Click, Input


EventHandler = Callable[[Any], Awaitable[None]]


class Dispatcher:
    """
    Centralized event dispatcher responsible for handling UI events
    such as clicks, input updates, navigation actions and window resize
    notifications.

    Each event type stores a mapping:
        { widget_id: async handler_function }
    """

    def __init__(self) -> None:
        """
        Initialize the event dispatcher with empty handler registries.
        """
        self.handlers: Dict[str, Dict[str, EventHandler]] = {
            "click": {},
            "input": {},
            "navigate": {},
            "resize": {},
        }

    def on_click(self, widget_id: str) -> Callable[[EventHandler], EventHandler]:
        """
        Register an asynchronous click event handler for a specific widget ID.

        Usage:
            @app.dispatcher.on_click("button_id")
            async def handler(event: Click):
                ...

        Parameters:
            widget_id (str): The ID of the widget that triggers this event.

        Returns:
            Callable: A decorator that registers the handler.
        """

        def decorator(func: EventHandler) -> EventHandler:
            self.handlers["click"][widget_id] = func
            return func

        return decorator

    def on_input(self, widget_id: str) -> Callable[[EventHandler], EventHandler]:
        """
        Register an asynchronous input-change event handler.

        Parameters:
            widget_id (str): The ID of the input widget.

        Returns:
            Callable: A decorator that registers the handler.
        """

        def decorator(func: EventHandler) -> EventHandler:
            self.handlers["input"][widget_id] = func
            return func

        return decorator

    # -------------------------------------------------------------------------
    # Dispatching
    # -------------------------------------------------------------------------

    async def dispatch(self, event: Any) -> Optional[Any]:
        """
        Dispatch an event object to the appropriate handler based on its type.

        Parameters:
            event (Any): The event object must have `.type` and `.widget_id`.

        Returns:
            Optional[Any]: The result of the handler, if any.
        """
        event_type = event.type
        widget_id = event.widget_id

        handler = self.handlers.get(event_type, {}).get(widget_id)
        if handler:
            return await handler(event)
        return None

    async def dispatch_click(self, component_id: str) -> Optional[Any]:
        """
        Dispatch a click event for a given widget ID.

        Parameters:
            component_id (str): The clicked widget's ID.

        Returns:
            Optional[Any]: Handler result if the handler exists.
        """
        handler = self.handlers["click"].get(component_id)
        if handler:
            event = Click(component_id)
            return await handler(event)
        return None

    async def dispatch_input(self, component_id: str, value: str) -> Optional[Any]:
        """
        Dispatch an input-change event for a given widget ID.

        Parameters:
            component_id (str): The input widget ID.
            value (str): The updated text value.

        Returns:
            Optional[Any]: Handler result if the handler exists.
        """
        handler = self.handlers["input"].get(component_id)
        if handler:
            event = Input(component_id, value)
            return await handler(event)
        return None
